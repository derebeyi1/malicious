import argparse
import configparser
import json
import mimetypes
import os
import pprint
import tempfile
from zipfile import ZipFile
import asyncpg
import asyncio
import requests
from datetime import datetime
from asyncpg import UniqueViolationError
import schedule
import time
import logging

from utilities import error_write_db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by IP Address or Csv File Address.')

# parser.add_argument('--file', dest='file', type=str, help='Query File at filepath (e.g. /foo/bar/blah.exe)')
parser.add_argument('--ip', dest='ip', type=str, help='IP Address')
parser.add_argument('--mode', dest='mode', type=str, help='Update Records From AbuseIPDB, --mode updateRecords')
# parser.add_argument('--resource', dest='resource', type=str, help='MalwareBazaar, VirusShare, MalShare, VXVault')
parser.add_argument('--csv', dest='csv', type=str,
                     help='Csv file path(c:/data.csv) or url(https://bazaar.abuse.ch/export/csv/recent/)')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]

async def csvFromAbuseIPDB():
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    querystring = {
        'confidenceMinimum': '90'
    }
    headers = {
        'Accept': 'application/json',
        'Key': config('abuseipdb_api_key')
    }
    fileName1 = ""
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if args.csv is None:
            args.csv = conf.get(name, 'blacklist_url')
        if str(args.csv).startswith("http"):
            r = requests.get(url=args.csv, headers=headers, params=querystring)
            if r.status_code == 200:
                temp = tempfile.gettempdir()
                print(temp)
                tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                ext = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])
                if ext == ".zip":
                    with open(os.path.join(tempFolder, 'file') + ext, 'wb') as f:
                        f.write(r.content)
                    with ZipFile(os.path.join(tempFolder, 'file') + ext, 'r') as zipObj:
                        # Get a list of all archived file names from the zip
                        listOfFileNames = zipObj.namelist()
                        # Iterate over the file names
                        for fileName in listOfFileNames:
                            if fileName.endswith('.csv'):
                                zipObj.extract(fileName, tempFolder)
                                fileName1 = fileName
                elif ext == '.csv' or ext == '.txt' or ext == '.json':
                    fileName1 = 'file' + ext
                    with open(os.path.join(tempFolder, fileName1), 'wb') as f:
                        f.write(r.content)
                else:
                    print("Dosya türü hatalı.")
                    quit()
                fname = os.path.join(tempFolder, fileName1)
        else:
            fname = args.csv
        sql_str1 = ""
        j = 0
        f = open(fname)
        data = json.load(f)
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        for i in data['data']:
            date_time_str = i['lastReportedAt']
            try:
                a = datetime.fromisoformat(date_time_str)
                f1 = "%Y-%m-%d %H:%M:%S"
                c = a.strftime(f1)
            except Exception as e:
                print(e)
            sql_str1 = "INSERT INTO public.malips(" \
                       "confidence_level, country, ip, lastreportedat, resource_name, maintype, subtype, user_name, datetime)" \
                       "VALUES($1,$2,$3,$4, 'AbuseIPDB', 'Malips', 'abuse', 'admin', CURRENT_TIMESTAMP) RETURNING id"
            try:
                csv_row_number += 1
                post_id = await conn.fetchval(sql_str1, i['abuseConfidenceScore'], i['countryCode'], i['ipAddress'], c)
                j += 1
            except UniqueViolationError as uve:
                duplicate_row_number += 1
                pass
            except Exception as e:
                except_row_number += 1
                pass
            finally:
                pass
        f.close()
        print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
        print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
    except IndexError as ie:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (ie, ie.__class__))
    except Exception as e:
        except_row_number += 1
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()
    print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")


async def updateRecordsFromAbuseIPDB():
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        options = Options()
        options.add_argument("--headless")
        if os.name == 'nt':
            driver = webdriver.Chrome(chrome_options=options, executable_path=r'g:\chromedriver.exe')
        else:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')

        sql_str = """SELECT * FROM malips WHERE resource_name = 'AbuseIPDB' and (usagetype is NULL or domainname is NULL or hostname is NULL 
                    or country is NULL or confidence_level is NULL)"""
        try:
            rows = await conn.fetch(sql_str)
            aa = len(rows)
            print(aa)
        except Exception as e:
            print("hata:>", e, e.__class__, sql_str[sql_str.index('VALUES'):sql_str.index('VALUES') + 50])
        config = configparser.ConfigParser()
        config.read("settings.ini")
        url = config.get(name, 'checkip_url')

        for row in rows:
            ip = row[2]
            try:
                time.sleep(2)
                driver.get(url + ip)
                # xpath1 = '//*[@id="report-wrapper"]/div[1]/div[1]/div/div[1]/div/span'
                xpath = "(//div[@id='page']//child::tr[2]//child::a)"
                # elem = driver.find_element(By.XPATH, xpath1)
                # confidence = elem.text
                # confidence_level = confidence[:-1]
                sql_str1 = "UPDATE public.malips SET datetime = CURRENT_TIMESTAMP(0), "
                columns = []
                tablo = driver.find_element(By.CLASS_NAME, 'table')
                str1 = tablo.text
                str2 = str1.split("\n")
                confidence_level = 0
                usagetype = ""
                domainname = ""
                hostname = ""
                country = ""
                i = 0
                k = 0
                if str1.find('Usage Type') > -1:
                    k += 1
                    usagetype = str2[k][11:]
                if str1.find('Hostname') > -1:
                    k += 1
                    hostname = str2[k][12:]
                if str1.find('Domain Name') > -1:
                    k += 1
                    domainname = str2[k][12:]
                if str1.find('Country') > -1:
                    k += 1
                    country = str2[k][8:]

                if row[6] is None:
                    columns.append(usagetype)
                    i += 1
                    sql_str1 = sql_str1 + "usagetype=$" + str(i) + ","
                if row[7] is None:
                    i += 1
                    columns.append(domainname)
                    sql_str1 = sql_str1 + "domainname=$" + str(i) + ","
                if row[8] is None:
                    i += 1
                    columns.append(hostname)
                    sql_str1 = sql_str1 + "hostname=$" + str(i) + ","
                if row[9] is None:
                    i += 1
                    columns.append(country)
                    sql_str1 = sql_str1 + "country=$" + str(i) + ","
                # i += 1
                sql_str1 = sql_str1[:-1]
                sql_str1 = sql_str1 + " WHERE id = " + str(row[0])
                stmt = await conn.prepare(sql_str1)
                # ssss = stmt.get_parameters()
                if i == 1:
                    await stmt.fetchval(columns[0])
                elif i == 2:
                    await stmt.fetchval(columns[0], columns[1])
                elif i == 3:
                    await stmt.fetchval(columns[0], columns[1], columns[2])
                elif i == 4:
                    await stmt.fetchval(columns[0], columns[1], columns[2], columns[3])
                elif i == 5:
                    await stmt.fetchval(columns[0], columns[1], columns[2], columns[3], columns[4])
                print("RESULT: malips tablosunda ", row[0], " numaralı kayıt güncellendi.")
                # print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
            except Exception as e:
                await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    except IndexError as ie:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (ie, ie.__class__))
    except Exception as e:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()

async def checkIpFromAbuseIPDB(ip):
    name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        url = config.get(name, 'checkip_url_apk')
        response_json = ''
        while response_json == '':
            try:
                querystring = {
                    'ipAddress': ip,
                    'maxAgeInDays': '90'
                }
                headers = {
                    'Accept': 'application/json',
                    'Key': config.get(name, 'api_key')
                }
                response_json = requests.get(url, headers=headers, params=querystring)
                break
            except Exception as e:
                print("hata", e)
                time.sleep(5)
                continue
            finally:
                pass
                # await conn.close()
        print('')
        print("AbuseIPDB Malicious Data for the IP: " + ip)
        print('#-----------------------------------------------------------------#')
        print('#*******||||||||||||||||||  AbuseIPDB  ||||||||||||||||||*******#')
        print('')
        pprint.pprint(response_json.json(), sort_dicts=False)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    # if args.ip is None and args.csv is None and args.mode is None:
    #     parser.error("at least one of --csv, --ip or --mode (updateRecords) required")
    if args.ip is not None:
        print('')
        print(
            "##########################################################################################################")
        print("AbuseIPDB Malicious Data for the IP: " + args.ip)
        print(
            "##########################################################################################################")
        print('')
        print('')
        ip = args.ip
        asyncio.get_event_loop().run_until_complete(checkIpFromAbuseIPDB(ip))
    elif args.mode =='updateRecords':
        schedule.every(args.schedule).seconds.do(
            lambda: asyncio.get_event_loop().run_until_complete(updateRecordsFromAbuseIPDB()))
        asyncio.get_event_loop().run_until_complete(updateRecordsFromAbuseIPDB())
        while True:
            schedule.run_pending()
            time.sleep(2)
    else:
        if args.schedule is None:
            args.schedule = int(config.get(name, 'blacklist_url_schedule'))
        schedule.every(args.schedule).minutes.do(
            lambda: asyncio.get_event_loop().run_until_complete(csvFromAbuseIPDB()))
        asyncio.get_event_loop().run_until_complete(csvFromAbuseIPDB())
        while True:
            schedule.run_pending()
            time.sleep(1)