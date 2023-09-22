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
from csv import reader
from datetime import datetime
from asyncpg import UniqueViolationError
import schedule
import time
import logging
from utilities import error_write_db
import validators
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by Hash or Csv File Address.')

parser.add_argument('--hash', dest='hash', type=str, help='IOC Hash')
parser.add_argument('--ioc', dest='ioc', type=str, help='IOC Value')
parser.add_argument('--csv', dest='csv', type=str,
                     help='Csv file path(c:/data.csv) or url(https://threatfox.abuse.ch/export/csv/full/)')
parser.add_argument('--url', dest='url', type=str,
                     help='Csv file path(c:/data.csv) or url(https://threatfox.abuse.ch/export/csv/recent/)')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]
url = ""
csv = ""

async def csvFromTHREATfox(url):
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    fileName1 = ""
    j = 0
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if str(url).startswith("http"):
            r = requests.get(url)
            if r.status_code == 200:
                temp = tempfile.gettempdir()
                tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                ext = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])
                if ext == ".zip":
                    with open(os.path.join(tempFolder, os.path.sep, 'file') + ext, 'wb') as f:
                        f.write(r.content)
                    with ZipFile(os.path.join(tempFolder, os.path.sep, 'file') + ext, 'r') as zipObj:
                        # Get a list of all archived file names from the zip
                        listOfFileNames = zipObj.namelist()
                        # Iterate over the file names
                        for fileName in listOfFileNames:
                            if fileName.endswith('.csv'):
                                zipObj.extract(fileName, tempFolder)
                                fileName1 = fileName
                            elif fileName.endswith('.txt'):
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
            fname = url
        with open(fname, 'r') as read_obj:
            csv_reader = reader(read_obj, delimiter=',', quotechar='"', skipinitialspace=True)
            # Iterate over each row after the header in the csv
            try:
                liste = list(csv_reader)
                lines = len(liste)
                if lines > 10000:
                    print(lines, " kayıt var, kayıt işlemi biraz uzun sürebilir.")
                csv_row_number = 0
                duplicate_row_number = 0
                except_row_number = 0
                j = 0
                for row in liste:
                    if (not row[0].startswith("#")):
                        sql_str1 = "INSERT INTO public.maliocs(" \
                                   "first_seen_utc, ioctype, iocvalue, fk_malware, malware_alias, malware_printable, confidence_level, reference, tags, last_seen_utc, resource_name, maintype, subtype, user_name, datetime)" \
                                   "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10, 'THREATfox', 'Malioc', $11, 'admin', CURRENT_TIMESTAMP) RETURNING id"
                        try:
                            csv_row_number += 1
                            post_id = await conn.fetchval(sql_str1, row[0], row[3], row[2], row[5], row[6], row[7], int(row[9]), row[10], row[11], row[8], row[4])
                            j += 1
                        except UniqueViolationError as uve:
                            duplicate_row_number += 1
                            pass
                        finally:
                            if (csv_row_number % 10000) == 0:
                                print(j, "/", csv_row_number, "kayıt eklendi.", duplicate_row_number, "tekrar ve",
                                      except_row_number, "hatalı kayıt var.")
                            pass
                print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
                print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
            except csv.Error as ce:
                print(f'file {fname}, line {liste.line_num:d}: {ce}')
    except IndexError as ie:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (ie, ie.__class__))
    except Exception as e:
        except_row_number += 1
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()
    print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")


async def iocHashQueryFromTHREATfox(hash):
    name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        conf = configparser.ConfigParser()
        conf.read("settings.ini")
        url = conf.get(name, 'api_url')
        response_json = ''
        while response_json == '':
            try:
                querystring = {
                    'query': "search_hash",
                    'hash': hash
                }
                data = json.dumps(querystring)
                response_json = requests.post(url, data)
                break
            except Exception as e:
                print("hata", e)
                time.sleep(5)
                continue
            finally:
                pass
        print('')
        print("THREATfox IOC Info for the HASH: " + hash)
        print('#-----------------------------------------------------------------#')
        print('#*******||||||||||||||||||  THREATfox  ||||||||||||||||||*******#')
        print('')
        pprint.pprint(response_json.json(), sort_dicts=False)
    except Exception as e:
        print(e)

async def iocQueryFromTHREATfox(ioc):
    name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        conf = configparser.ConfigParser()
        conf.read("settings.ini")
        url = conf.get(name, 'api_url')
        response_json = ''
        while response_json == '':
            try:
                querystring = {
                    'query': "search_ioc",
                    'search_term': ioc
                }
                data = json.dumps(querystring)
                response_json = requests.post(url, data)
                break
            except Exception as e:
                print("hata", e)
                time.sleep(5)
                continue
            finally:
                pass
        print('')
        print("THREATfox IOC Info for the IOC: " + ioc)
        print('#-----------------------------------------------------------------#')
        print('#*******||||||||||||||||||  THREATfox  ||||||||||||||||||*******#')
        print('')
        pprint.pprint(response_json.json(), sort_dicts=False)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    if args.hash is not None:
        print('')
        print(
            "##########################################################################################################")
        print("THREATfox IOC Info for the HASH: " + args.hash)
        print(
            "##########################################################################################################")
        print('')
        print('')
        asyncio.get_event_loop().run_until_complete(iocHashQueryFromTHREATfox(args.hash))
    elif args.ioc is not None:
        print('')
        print(
            "##########################################################################################################")
        print("THREATfox IOC Info for the IOC: " + args.ioc)
        print(
            "##########################################################################################################")
        print('')
        print('')
        asyncio.get_event_loop().run_until_complete(iocQueryFromTHREATfox(args.ioc))
    else:
        if args.schedule is None:
            args.schedule = int(conf.get(name, 'recent_csv_url_schedule'))
        if args.csv is None:
            csv = conf.get(name, 'full_csv_url')
        else:
            if str(args.csv).startswith('http'):
                if validators.url(args.csv):
                    csv = args.csv
                else:
                    parser.error("--csv argument is not valid.")
            else:
                csv = args.csv
        if args.url is None:
            url = conf.get(name, 'recent_csv_url')
        else:
            if str(args.url).startswith('http'):
                if validators.url(args.csv):
                    url = args.url
                else:
                    parser.error("--csv argument is not valid.")
            else:
                url = args.url
        # full csv data 1 kez çalışacak
        asyncio.get_event_loop().run_until_complete(csvFromTHREATfox(csv))
        # recent csv data günde 1 kez çalışacak
        schedule.every(args.schedule).minutes.do(
            lambda: asyncio.get_event_loop().run_until_complete(csvFromTHREATfox(url)))
        asyncio.get_event_loop().run_until_complete(csvFromTHREATfox(url))
        while True:
            schedule.run_pending()
            time.sleep(1)
