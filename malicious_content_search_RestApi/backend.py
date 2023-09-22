import configparser
import datetime
import json
import os
import re
import sys
import tempfile
import traceback
import urllib

import asyncpg
import requests
import validators
from asyncpg import UniqueViolationError
from flask import Response

import utilities
from urllib.parse import urljoin
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

name = os.path.splitext(os.path.basename(__file__))[0]
# name = os.path.splitext(os.path.basename(__file__))[0]
temp = tempfile.gettempdir()
tempFolder = os.path.join(temp, name)
vt = 'VirusTotal'
av = 'AlienVault'
ar = 'AnyRun'
misp = 'MISP'
tm = 'UC'
conf = configparser.ConfigParser()


async def error_write_db(hata_str, ip, username):
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        sql_str = "INSERT INTO public.logs(log, ip, user_name, datetime)" \
                  " VALUES ('%s', '%s', '%s', %s);" % (hata_str.replace('\'', ''), ip, username, 'CURRENT_TIMESTAMP')
        try:
            await conn.execute(sql_str)
        except UniqueViolationError as uve:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
            raise Exception(error)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        raise Exception(error)
    finally:
        await conn.close()


async def getioctype(query):
    global ioctype1
    global ioctype
    if utilities.sha256(query):
        ioctype1 = 'malware'
        ioctype = 'sha256'
    elif utilities.md5(query):
        ioctype1 = 'malware'
        ioctype = 'md5'
    elif utilities.sha1(query):
        ioctype1 = 'malware'
        ioctype = 'sha1'
    elif utilities.validate_ip_address(query):
        ioctype1 = 'ip'
        ioctype = 'ip'
    elif validators.url(query):
        ioctype1 = 'ioc'
        ioctype = 'url'
    elif validators.domain(query):
        ioctype1 = 'ioc'
        ioctype = 'domain'
    else:
        # ip:port formatinda ise split edip hem malips hem de maliocs tablosundan sorguluyorum
        ipport = query.split(':')
        if len(ipport) == 2 and utilities.validate_ip_address(ipport[0]) and ipport[1].isnumeric():
            ioctype1 = 'ipport'
            ioctype = 'ip'
        else:
            ioctype = ''
            ioctype1 = ''
    return ioctype


async def getsqlstr(ioctype):
    if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, md5_hash, sha256_hash, sha1_hash, maintype, subtype, imphash, vtpercent, tlsh, clamav, mime_type, file_name, file_type_guess, signature, reporter, tags, confidence_level, ip, url, first_seen_utc, last_seen_utc) d)) as json FROM malwares WHERE "
        if ioctype == 'sha256':
            sql_str += "sha256_hash = $1"
        elif ioctype == 'md5':
            sql_str += "md5_hash = $1"
        elif ioctype == 'sha1':
            sql_str += "sha1_hash = $1"
    elif ioctype1 == 'ipport':
        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ioctype, iocvalue, maintype, subtype, tags, malware_alias, fk_malware, confidence_level,first_seen_utc, last_seen_utc) d)) as json FROM maliocs WHERE iocvalue = $1"  # FETCH FIRST 1 ROWS ONLY
    elif ioctype == 'ip':
        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ip, port, ip_status, maintype, subtype, confidence_level, domainname, hostname, country, first_seen_utc, lastreportedat) d)) as json FROM malips WHERE ip = $1"
    elif ioctype1 == 'ioc':
        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ioctype, iocvalue, maintype, subtype, tags, malware_alias, fk_malware, confidence_level,first_seen_utc, last_seen_utc) d)) as json FROM maliocs WHERE iocvalue = $1"
    return sql_str


async def searchcreate(conn, ioctype1, query, sources, username, apikey, userip):
    sources1 = ''
    for source in sources:
        sources1 += (source + ',')
    sources1 = sources1[:-1]
    sql_str1 = "INSERT INTO public.searches(ioctype, iocvalue, sources, username, apikey, userip, datetime)" \
               " VALUES ('" + ioctype1 + "', '" + query + "', '" + sources1 + "', '" + username + "', '" + apikey + "','" + userip + "', CURRENT_TIMESTAMP)"
    try:
        await conn.execute(sql_str1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        raise Exception(error)
    finally:
        pass
        # conn.close()


async def uclookup(query, sources, username, apikey, userip):
    searches = {}
    sources = sources
    sources1 = []
    db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
    conn = await asyncpg.connect(db_conn_str)
    try:
        ioctype = await getioctype(query)
        if ioctype != '':
            sql_str = await getsqlstr(ioctype)
            str1 = str(sources)
            if str1.find(vt) > -1:
                vtresult = await vtlookup(query, ioctype, username, apikey, userip)
                if vtresult != '':
                    searches[vt] = vtresult
                    sources1.append(vt)
            if str1.find(av) > -1:
                avresult = await avlookup(query, ioctype, username, apikey, userip)
                if avresult != '':
                    searches[av] = avresult
                    sources1.append(av)
            if str1.find(misp) > -1:
                mispresult = await misplookup(query, ioctype, username, apikey, userip)
                if mispresult != '':
                    searches[misp] = mispresult
                    sources1.append(misp)
            # if str1.startswith(ar) > -1:
            #     arresult = await arlookup(query, ioctype, username, apikey, userip)
            if sql_str != "":
                conf.read("settings.ini")
                if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
                    rows = await conn.fetch(sql_str, query)
                    if rows is None or len(rows) == 0:
                        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ioctype, iocvalue, maintype, subtype, tags, malware_alias, fk_malware, confidence_level, first_seen_utc, last_seen_utc) d)) as json FROM maliocs WHERE iocvalue = $1"
                        rows = await conn.fetch(sql_str, query)
                        if rows is None or len(rows) == 0:
                            pass
                        else:
                            for x in range(0, len(rows)):
                                sources1.append(rows[x][0])
                                row = rows[x][1]
                                url = conf.get(rows[x][0], 'url');
                                if rows[x][0] == 'MalwareBazaar':
                                    url = url + await getioctype(query) + ':'
                                if rows[x][0] == 'MalShare':
                                    url = url + query
                                data = {'url': url, 'data': json.loads(row)}
                                searches[rows[x][0]] = data
                    else:
                        for x in range(0, len(rows)):
                            sources1.append(rows[x][0])
                            row = rows[x][1]
                            url = conf.get(rows[x][0], 'url');
                            if rows[x][0] == 'MalwareBazaar':
                                url = url + await getioctype(query) + ':'
                            if rows[x][0] == 'MalShare':
                                url = url + query
                            data = {'url': url, 'data': json.loads(row)}
                            searches[rows[x][0]] = data
                elif ioctype1 == 'ipport':
                    rows = await conn.fetch(sql_str, query)
                    if rows is None or len(rows) == 0:
                        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ip, port, ip_status, maintype, subtype, confidence_level, domainname, hostname, country, first_seen_utc, lastreportedat) d)) as json FROM malips WHERE ip = $1"
                        rows = await conn.fetch(sql_str, query.split(':')[0])
                        if rows is None or len(rows) == 0:
                            pass
                        else:
                            for x in range(0, len(rows)):
                                sources1.append(rows[x][0])
                                row = rows[x][1]
                                data = {'url': '', 'data': json.loads(row)}
                                searches[rows[x][0]] = data
                    else:
                        for x in range(0, len(rows)):
                            sources1.append(rows[x][0])
                            row = rows[x][1]
                            url = conf.get(rows[x][0], 'url')
                            if rows[x][0] == 'URLhaus':
                                url = url + query
                            elif rows[x][0] == 'THREATfox':
                                url = url + query
                            data = {'url': url, 'data': json.loads(row)}
                            searches[rows[x][0]] = data
                elif ioctype == 'ip':
                    rows = await conn.fetch(sql_str, query)
                    if rows is None or len(rows) == 0:
                        sql_str = "SELECT resource_name, row_to_json((SELECT d FROM (SELECT resource_name, ioctype, iocvalue, maintype, subtype, tags, malware_alias, fk_malware, confidence_level,first_seen_utc, last_seen_utc) d)) as json FROM maliocs WHERE split_part(iocvalue, ':', 1) = $1"
                        rows = await conn.fetch(sql_str, query)
                        if rows is None or len(rows) == 0:
                            pass
                        else:
                            for x in range(0, len(rows)):
                                sources1.append(rows[x][0])
                                row = rows[x][1]
                                url = conf.get(rows[x][0], 'url')
                                if rows[x][0] == 'AbuseIPDB':
                                    url = url + query
                                elif rows[x][0] == 'THREATfox':
                                    url = url + query
                                elif rows[x][0] == 'FEODOtracker':
                                    url = url + query
                                elif rows[x][0] == 'URLhaus':
                                    url = url + query
                                data = {'url': url, 'data': json.loads(row)}
                                searches[rows[x][0]] = data
                    else:
                        for x in range(0, len(rows)):
                            sources1.append(rows[x][0])
                            row = rows[x][1]
                            url = conf.get(rows[x][0], 'url')
                            if rows[x][0] == 'AbuseIPDB':
                                url = url + query
                            elif rows[x][0] == 'THREATfox':
                                url = url + query
                            elif rows[x][0] == 'FEODOtracker':
                                url = url + query
                            elif rows[x][0] == 'URLhaus':
                                url = url + query
                            data = {'url': url, 'data': json.loads(row)}
                            searches[rows[x][0]] = data
                elif ioctype1 == 'ioc':
                    rows = await conn.fetch(sql_str, query)
                    if rows is None or len(rows) == 0:
                        pass
                    else:
                        for x in range(0, len(rows)):
                            sources1.append(rows[x][0])
                            row = rows[x][1]
                            url = conf.get(rows[x][0], 'url')
                            if rows[x][0] == 'URLhaus':
                                url = url + query
                            if rows[x][0] == 'AbuseIPDB':
                                url = url + query
                            if rows[x][0] == 'THREATfox':
                                url = url + query
                            data = {'url': url, 'data': json.loads(row)}
                            searches[rows[x][0]] = data
            await searchcreate(conn, ioctype1, query, sources1, username, apikey, userip)
            return searches
        else:
            return searches
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        await error_write_db("ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno), userip, username)
        raise Exception(error)
    finally:
        pass
        # conn.close()


async def vtlookup(query, ioctype, username, apikey, userip):
    url = ''
    try:
        conf.read("settings.ini")
        #apikey = conf.get(vt, 'apikey');
        apikey = config('virustotal_api_key')
        if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
            url1 = conf.get(vt, 'url1')
            url1_method = conf.get(vt, 'url1_method')
            url = url1 + query
            method = url1_method
            url1 = conf.get(vt, 'urlfile')
        elif ioctype == 'ip':
            url2 = conf.get(vt, 'url2')
            url2_method = conf.get(vt, 'url2_method')
            url = url2 + query
            method = url2_method
            url1 = conf.get(vt, 'urlip')
        elif ioctype == 'domain':
            url3 = conf.get(vt, 'url3')
            url3_method = conf.get(vt, 'url3_method')
            url = url3 + query;
            method = url3_method
            url1 = conf.get(vt, 'urldomain')
        elif ioctype == 'url':
            url4 = conf.get(vt, 'url4')
            url4_method = conf.get(vt, 'url4_method')
            url = url4;
            method = url4_method
            url1 = conf.get(vt, 'urlurl')
        if url != '':
            headers = {
                'x-apikey': apikey,
            }
            if method == 'POST':
                data = {'url': query}
                response = requests.post(url, data=data, headers=headers)
                resp = response.json()
                id = str(resp['data']['id']).split('-')[1]
                url = urljoin(url4 + '/', id)
                response = requests.get(url, headers=headers)

                conf.read("settings.ini")
                vtres = response.json()
                json_obj = json.loads(json.dumps(vtres, sort_keys=True))
                lar = json_obj["data"]["attributes"]["last_analysis_results"]
                prm1 = vtres['data']['links']['self'].split('/')[-1]
                # url2 = vtres['data']['links']['self']
                data = {
                    'url': url1 + prm1,
                    'data': lar
                }
            else:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    conf.read("settings.ini")
                    vtres = response.json()
                    json_obj = json.loads(json.dumps(vtres, sort_keys=True))
                    lar = json_obj["data"]["attributes"]["last_analysis_results"]
                    prm1 = vtres['data']['links']['self'].split('/')[-1]
                    # url2 = vtres['data']['links']['self']
                    data = {
                        'url': url1 + prm1,
                        'data': lar
                    }
                else:
                    data = ''
            return data
        else:
            return ''
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(
            exc_traceback.tb_lineno)
        # raise Exception(error)
        return ''
    finally:
        pass
    return ''


async def avlookup(query, ioctype, username, apikey, userip):
    url = ''
    section = '/general'
    try:
        conf.read("settings.ini")
        #apikey = conf.get(av, 'apikey');
        apikey = config('alienvault_api_key');
        urli = ''
        if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
            url1 = conf.get(av, 'url1')
            url1_method = conf.get(av, 'url1_method')
            url = url1 + query + section
            method = url1_method
            urli = conf.get(av, 'urlfile');
        elif ioctype == 'ip':
            url2 = conf.get(av, 'url2')
            url2_method = conf.get(av, 'url2_method')
            url = url2 + query + section
            method = url2_method
            urli = conf.get(av, 'urlip');
        elif ioctype == 'domain':
            url3 = conf.get(av, 'url3')
            url3_method = conf.get(av, 'url3_method')
            url = url3 + query + section
            method = url3_method
            urli = conf.get(av, 'urldomain');
        elif ioctype == 'url':
            url5 = conf.get(av, 'url5')
            url5_method = conf.get(av, 'url5_method')
            url = url5 + query + section
            method = url5_method
            urli = conf.get(av, 'urlurl');
        if url != '':
            response = requests.get(url)
            # json_obj = json.loads(json.dumps(response.json(), sort_keys=True))
            # lar = json_obj["pulse_info"]["pulses"]
            if response.status_code == 200:
                json_obj = json.loads(json.dumps(response.json(), sort_keys=True))
                lar = json_obj["pulse_info"]["pulses"]
                bi = json_obj["base_indicator"]
                asn = ''
                city = ''
                region = ''
                country_name = ''
                try:
                    asn = json_obj["asn"]
                except KeyError as ke:
                    pass
                try:
                    city = json_obj["city"]
                except KeyError as ke:
                    pass
                try:
                    region = json_obj["region"]
                except KeyError as ke:
                    pass
                try:
                    country_name = json_obj["country_name"]
                except KeyError as ke:
                    pass
                data = {'url': urli + query, 'data': {'base_indicator': bi, 'pulses': lar, 'asn': asn, 'city':city, 'region': region, 'country_name': country_name}}
                return data
            else:
                return ''
        else:
            return ''
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        # raise Exception(error)
        return ''
    finally:
        pass
    return ''


async def arlookup(query, ioctype, username, apikey, userip):
    url = ''
    try:
        conf.read("settings.ini")
        #apikey = conf.get(ar, 'apikey');
        apikey = config('anyrun_api_key')
        if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
            url1 = conf.get(ar, 'url1')
            url1_method = conf.get(ar, 'url1_method')
            url = url1 + query
            method = url1_method
        elif ioctype == 'ip':
            url2 = conf.get(ar, 'url2')
            url2_method = conf.get(ar, 'url2_method')
            url = url2 + query
            method = url2_method
        elif ioctype == 'domain':
            url3 = conf.get(ar, 'url3')
            url3_method = conf.get(ar, 'url3_method')
            url = url3 + query;
            method = url3_method
        elif ioctype == 'url':
            url4 = conf.get(ar, 'url4')
            url4_method = conf.get(ar, 'url4_method')
            url = url4
            method = url4_method
        if url != '':
            headers = {
                'x-apikey': apikey,
            }
            # params = {
            #     method: method,
            #     headers: headers,
            # }
            if method == 'POST':
                data = {'url': query}
                params = {
                    data: data,
                    headers: headers,
                }
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            return response.json()
        else:
            return ''
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        # raise Exception(error)
        return ''
    finally:
        pass
    return ''


async def misplookup(query, ioctype, username, apikey, userip):
    url = ''
    try:
        conf.read("settings.ini")
        #apikey = conf.get(misp, 'apikey');
        apikey = config('MISP_api_key')
        if ioctype == 'md5' or ioctype == 'sha1' or ioctype == 'sha256':
            type = ioctype
            url1 = conf.get(misp, 'url1')
            url1_method = conf.get(misp, 'url1_method')
            url = url1 + query
            method = url1_method
        elif ioctype == 'ip':
            url2 = conf.get(misp, 'url2')
            url2_method = conf.get(misp, 'url2_method')
            url = url2 + query
            method = url2_method
            type = 'ip-dst'
        elif ioctype == 'domain':
            url3 = conf.get(misp, 'url3')
            url3_method = conf.get(misp, 'url3_method')
            url = url3 + query;
            method = url3_method
            type = ioctype
        # elif ioctype == 'url':
        #     url4 = conf.get(misp, 'url4')
        #     url4_method = conf.get(misp, 'url4_method')
        #     url = url4;
        #     method = url4_method
        #     type = ioctype
        if url != '':
            headers = {
                'Authorization': apikey,
            }
            # params = {
            #     method: method,
            #     headers: headers,
            # }
            if method == 'POST':
                data = {'returnFormat': 'json', 'type': type, 'includeContext': 'eventinfo', 'category': ''}
                params = {
                    data: data,
                    headers: headers,
                }
                response = requests.post(url, data=data, headers=headers, verify=False)
            else:
                response = requests.get(url, headers=headers, verify=False)

            resp = response.json()
            json_obj = json.loads(json.dumps(resp, sort_keys=True))
            lar = json_obj['response']['Attribute']
            aa = len(lar)
            if len(lar) > 0:
                data = {
                    'url': url + query,
                    'data': resp
                }
            else:
                data = ''
            return data
        else:
            return ''
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        # raise Exception(error)
        return ''
    finally:
        pass
    return ''


async def getStatistics(interval):
    try:
        dizi = {}
        today = datetime.date.today()
        if interval == 1:
            filename = 'DailyStatistics_' + str(today)
        elif interval == 7:
            filename = 'WeeklyStatistics_' + str(today)
        elif interval == 30:
            filename = 'MonthlyStatistics_' + str(today)
        else:
            interval = 1
            filename = 'DailyStatistics_' + str(today)
        if not os.path.exists(tempFolder):
            os.mkdir(tempFolder)
        path = tempFolder + os.path.sep + filename + '.json'
        interval = str(interval)
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if os.path.isfile(path):
            f = open(path, "r")
            data = json.loads(f.read())
            f.close()

            sql_str9 = "SELECT * FROM (SELECT iocvalue, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" + interval + "' day group by iocvalue limit 10) tbl ORDER by tbl.sayi desc"
            row9 = await conn.fetch(sql_str9)
            searches = {}
            searches.update(row9)

            data['searches'] = searches;
            with open(path, 'r+') as f:
                f.truncate(0)
                f.seek(0)
            f = open(path, "a")
            f.truncate()
            dizi = json.dumps(data)
            f.write(dizi)
            f.close()
        else:
            sql_str1 = "SELECT 'malwares' as type, count(*) as sayi FROM malwares WHERE datetime > current_date - interval '" +interval+ "' day"
            sql_str2 = "SELECT 'malips' as type, count(*) as sayi FROM malips WHERE datetime > current_date - interval '" +interval+ "' day"
            sql_str3 = "SELECT 'maldomains' as type, count(*) as sayi FROM maliocs WHERE ioctype = 'domain' and datetime > current_date - interval '" +interval+ "' day"
            sql_str4 = "SELECT 'malurls' as type, count(*) as sayi FROM maliocs WHERE ioctype = 'url' and datetime > current_date - interval '" +interval+ "' day"
            sql_str5 = "SELECT resource_name, count(*) as sayi FROM malwares WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str6 = "SELECT resource_name, count(*) as sayi FROM malips WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str7 = "SELECT resource_name, count(*) as sayi FROM maliocs WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str8 = "SELECT ioctype, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" +interval+ "' day group by ioctype"
            sql_str9 = "SELECT * FROM (SELECT iocvalue, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" +interval+ "' day group by iocvalue limit 10) tbl ORDER by tbl.sayi desc"

            row1 = await conn.fetch(sql_str1)
            row2 = await conn.fetch(sql_str2)
            row3 = await conn.fetch(sql_str3)
            row4 = await conn.fetch(sql_str4)
            conn.close()
            db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
            conn = await asyncpg.connect(db_conn_str)
            row5 = await conn.fetch(sql_str5)
            row6 = await conn.fetch(sql_str6)
            row7 = await conn.fetch(sql_str7)
            row8 = await conn.fetch(sql_str8)
            row9 = await conn.fetch(sql_str9)
            data = {}
            types = {}
            searches = {}
            data.update(row1)
            data.update(row2)
            data.update(row3)
            data.update(row4)

            data1 = {}
            data1.update(row5)
            data2 = {}
            data2.update(row6)
            data3 = {}
            data3.update(row7)
            data4 = await updateDict(data1, data2)
            data5 = await updateDict(data4, data3)

            # data.update(row5)
            # data.update(row6)
            data.update(data5)
            types.update(row8)
            searches.update(row9)
            dizi = json.dumps({'data': data, 'types': types, 'searches': searches})
            f = open(path, "a")
            f.write(dizi)
            f.close()

    except UniqueViolationError as uve:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        raise Exception(error)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(exc_traceback.tb_lineno)
        raise Exception(error)
    finally:
        if conn is not None:
            conn.close
    return dizi


async def get_file_from_db(hash):
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        sql_str = "SELECT * FROM malwares WHERE "
        sql_str1 = ""
        if str(hash).startswith("sha256"):
            sql_str += "sha256_hash = $1"
            sql_str1 = hash[7:]
        elif str(hash).startswith("md5"):
            sql_str += "md5_hash = $1"
            sql_str1 = hash[4:]
        row1 = await conn.fetchrow(sql_str, sql_str1)
        if row1 is None:
            return []
        else:
            sql_str2 = "SELECT * FROM mal_files WHERE malwares_id = $1"
            malwares_id = row1[0]
            row2 = await conn.fetchrow(sql_str2, malwares_id)
            with open("file1.zip", "wb") as binary_file:
                binary_file.write(row2[3])
                binary_file.close()
            return binary_file

    except UniqueViolationError as uve:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (uve, uve.__class__))
    except Exception as e:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        conn.close()


async def isApiKeyAuthorized(apikey):
    db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
    conn = await asyncpg.connect(db_conn_str)
    sql_str = "SELECT * FROM home_company WHERE apikey = $1"
    record = await conn.fetchrow(sql_str, apikey)
    if record is None:
        return False
    return True


async def updateDict(dict1, dict2):
    for key2, value2 in dict2.items():
        knt = 0
        for key1, value1 in dict1.items():
            if key2 == key1:
                knt = 1
                dict1[key1] = value1 + value2
                break
        if knt == 0:
            dict1[key2] = value2
    return dict1
