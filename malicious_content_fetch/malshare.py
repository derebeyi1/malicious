import argparse
import configparser
import csv
import os
import pprint
import sys
import tempfile

import asyncpg
import asyncio
import requests


from csv import reader
from datetime import datetime, timedelta
from asyncpg import UniqueViolationError
import schedule
import time
import logging

from utilities import error_write_db
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by Hash or Csv File Address.')
parser.add_argument('--hash', dest='hash', type=str, help='Query Hash (MD5)')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
parser.add_argument('--api_key', dest='api_key', type=str, help='Api Key')
parser.add_argument('--action', dest='action', type=str, help='Action(getlist, details)')
parser.add_argument('--url', dest='url', type=str, help='Url')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
conf = configparser.ConfigParser()
conf.read("malshare.ini")
name = os.path.splitext(os.path.basename(__file__))[0]
api_url = conf.get(name, 'api_url')
#api_key = conf.get(name, 'api_key')
api_key = config('malshare_api_key')

async def malsharelookupGetList():
    response_json = ''
    while response_json == '':
        try:
            if args.api_key is None: args.api_key = api_key
            response_json = requests.get(api_url, headers=None, params={  # url parameters
                'api_key': args.api_key,
                'action': 'getlist',
            })
        except Exception as e:
            print("hata", e)
            time.sleep(5)
            continue

    print('')
    print("MalShare Malwares Info")
    print('#-----------------------------------------------------------------#')
    print('#*******||||||||||||||||||  MalShare  ||||||||||||||||||*******#')
    print('')
    pprint.pprint(response_json, sort_dicts=False)
    return response_json.json()

async def malsharelookupDetail(hash):
    conf = configparser.ConfigParser()
    conf.read("malshare.ini")
    url = conf.get(name, 'api_url')
    response_json = ''
    while response_json == '':
        try:
            if args.api_key is None: args.api_key = api_key
            if args.hash is None: args.hash = hash
            response_json = requests.get(url, headers=None, params={  # url parameters
                'api_key': args.api_key,
                'hash': args.hash,
                'action': 'details',
            })
        except Exception as e:
            print("hata", e)
            time.sleep(5)
            continue

    print('')
    print("MalShare Malware Info for the HASH: \n" + args.hash)
    print('#-----------------------------------------------------------------#')
    print('#*******||||||||||||||||||  MalShare  ||||||||||||||||||*******#')
    print('')
    pprint.pprint(response_json.json(), sort_dicts=False)
    return response_json.json()

async def txtFromMalShareUrl():
    txt_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    url = str(args.url)
    filename = url.split("/")[5]
    j = 0
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        dongu = True
        j = 0
        if (str(args.url).startswith("http")):
            date = url.split("/")[4]
            format = "%Y-%m-%d"
            date_time_obj1 = datetime.strptime(date, format).date()
            # date_time_obj1 = date_time_obj + timedelta(days=1)
            while date_time_obj1 <= datetime.now().date():
                path = os.path.dirname(os.path.realpath(__file__))
                temp = tempfile.gettempdir()
                tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                fname = os.path.join(tempFolder, filename)
                if not os.path.isfile(fname):
                    r = requests.get(url)
                    if r.status_code == 200:
                        with open(fname, 'wb') as write_obj:
                            write_obj.write(r.content)
                        # else:
                        #     fname = args.url
                        sql_str1 = ""
                        j = 0
                        try:
                            with open(fname, 'r') as read_obj:
                                txt_reader = reader(read_obj, delimiter='	')
                                # Iterate over each row after the header in the csv
                                liste = list(txt_reader)
                                lines = len(liste)
                                if lines > 10000:
                                    print(lines, " kayıt var, kayıt işlemi biraz uzun sürebilir.")
                                txt_row_number = 0
                                duplicate_row_number = 0
                                except_row_number = 0
                                sql_str1 = "INSERT INTO public.malwares(sha256_hash, md5_hash, sha1_hash, file_type_guess, ssdeep, resource_name, maintype, subtype, user_name, datetime)" \
                                           " VALUES ($1,$2,$3,$4,$5, 'MalShare', 'Malware', 'abuse', 'admin', CURRENT_TIMESTAMP) RETURNING id"
                                for row in liste:
                                    ssdeep = row[3]
                                    md5_hash = row[0]
                                    sha1_hash = row[1]
                                    sha256_hash = row[2]
                                    try:
                                        txt_row_number += 1;
                                        # TODO detail servisi yavaş çalışıyor, kapattım
                                        # detail = malsharelookupDetail(row[2])
                                        file_type = ""
                                        if sha256_hash == '':
                                            sha256_hash = md5_hash
                                        post_id = await conn.fetchval(sql_str1, sha256_hash, md5_hash, sha1_hash, file_type, ssdeep)
                                        j += 1
                                    except UniqueViolationError as uve:
                                        duplicate_row_number += 1
                                        pass
                                    except Exception as e:
                                        except_row_number += 1
                                        pass
                                    finally:
                                        if (txt_row_number % 10000) == 0:
                                            print(j, "/", txt_row_number, "kayıt eklendi.", duplicate_row_number,
                                                  "tekrar ve", except_row_number, "hatalı kayıt var.")
                                        pass
                                print("DOSYA ADI: ", filename)
                                print("RESULT: ", txt_row_number, " kayıttan ", j, " kayıt eklendi.")
                                print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
                                conf.set(name, 'last_data_url', url)
                                conf.write(open("malshare.ini", "w"))
                        except IndexError as ie:
                            await error_write_db("ERROR:" + name + ".py:%s:%s" % (ie, ie.__class__))
                        except csv.Error as ce:
                            print(f'file {filename}, line {txt_reader.line_num:d}: {ce}')
                            # sys.exit('file %s, line %d: %s' % (filename, txt_reader.line_num, ce))
                        except Exception as e:
                            except_row_number += 1
                            await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
                        finally:
                            date = url.split("/")[4]
                            format = "%Y-%m-%d"
                            date_time_obj = datetime.strptime(date, format).date()
                            date_time_obj1 = date_time_obj + timedelta(days=1)
                            url = url.replace(date, str(date_time_obj1), 2)
                            filename = url.split("/")[5]
                            fname = path + "_hashes/" + filename
                            conf.set(name, 'last_data_url', url)
                            conf.write(open("malshare.ini", "w"))
                    else:
                        if date_time_obj1 < datetime.now().date():
                            date = url.split("/")[4]
                            format = "%Y-%m-%d"
                            date_time_obj = datetime.strptime(date, format).date()
                            date_time_obj1 = date_time_obj + timedelta(days=1)
                            url = url.replace(date, str(date_time_obj1), 2)
                            filename = url.split("/")[5]
                            fname = path + "_hashes/" + filename
                        else:
                            break
                        conf.set(name, 'last_data_url', url)
                        conf.write(open("malshare.ini", "w"))
                else:
                    date = url.split("/")[4]
                    format = "%Y-%m-%d"
                    date_time_obj = datetime.strptime(date, format).date()
                    date_time_obj1 = date_time_obj + timedelta(days=1)
                    url = url.replace(date, str(date_time_obj1), 2)
                    filename = url.split("/")[5]
                    fname = path + "_hashes/" + filename
                conf.set(name, 'last_data_url', url)
                conf.write(open("malshare.ini", "w"))
    except IndexError as ie:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (ie, ie.__class__))
    except Exception as e:
        except_row_number += 1
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()
    print("RESULT: ", txt_row_number, " kayıttan ", j, " kayıt eklendi.")
    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
    conf.set(name, 'last_data_url', url)
    conf.write(open("malshare.ini", "w"))

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("malshare.ini")    
    if args.hash is None and args.action is None:
        if args.schedule is None:
            args.schedule = int(conf.get(name, 'data_url_schedule'))
        if args.url is None:
            if conf.get(name, 'last_data_url') == 'None':
                args.url = conf.get(name, 'data_url')
            else:
                args.url = conf.get(name, 'last_data_url')
        schedule.every(args.schedule).minutes.do(
            lambda: asyncio.get_event_loop().run_until_complete(txtFromMalShareUrl()))
        asyncio.get_event_loop().run_until_complete(txtFromMalShareUrl())
        while True:
            schedule.run_pending()
            time.sleep(1)
    elif args.action is not None and args.action == 'getlist':
        asyncio.get_event_loop().run_until_complete(malsharelookupGetList())
    elif args.hash is not None:
        asyncio.get_event_loop().run_until_complete(malsharelookupDetail(args.hash))
