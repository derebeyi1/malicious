import argparse
import configparser
import csv
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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by Hash, Csv or Txt File Address.')
# parser.add_argument('--ip', dest='ip', type=str, help='Query IP Address')
# parser.add_argument('--mode', dest='mode', type=str, help='Update Records From FEODOtracker, --mode updateRecords')
# parser.add_argument('--csv', dest='csv', type=str,
#                      help='Csv file path(c:/data.csv) or url(https://feodotracker.abuse.ch/downloads/ipblocklist.csv)')
# parser.add_argument('--txt', dest='txt', type=str,
#                      help='txt file path(c:/data.txt) or url(https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt)')
parser.add_argument('--url', dest='url', type=str,
                     help='--url https://github.com/firehol/blocklist-ipsets/archive/refs/heads/master.zip')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]
tempFolder = os.path.join(tempfile.gettempdir(), name)

async def ipsetFromfirehol():
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    fileName1 = ""
    j = 0
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if args.url is None:
            conf = configparser.ConfigParser()
            conf.read("firehol.ini")
            args.url = conf.get(name, 'url')
        if str(args.url).startswith("http"):
            r = requests.get(args.url)
            if r.status_code == 200:
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                ext = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])
                if ext == ".zip":
                    with open(os.path.join(tempFolder, 'file') + ext, 'wb') as f:
                        f.write(r.content)
                    with ZipFile(os.path.join(tempFolder, 'file') + ext, 'r') as zipObj:
                        # Get a list of all archived file names from the zip
                        zipObj.extractall(tempFolder)
                        listOfFileNames = zipObj.namelist()
                        # Iterate over the file names
                        for fileName in listOfFileNames:
                            if fileName.endswith(".ipset") or fileName.endswith(".netset"):
                                fname = os.path.join(tempFolder, fileName)
                                sql_str1 = ""
                                j = 0
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
                                        for row in liste:
                                            i = 0
                                            if not row[0].startswith("#") and not row[0].startswith("first_seen_utc"):
                                                sql_str1 = "INSERT INTO public.malips(" \
                                                           "ip, resource_name, maintype, subtype, user_name, datetime)" \
                                                           "VALUES($1, 'firehol', 'Botnet', 'blocklist', 'admin', CURRENT_TIMESTAMP) RETURNING id"
                                                try:
                                                    csv_row_number += 1
                                                    post_id = await conn.fetchval(sql_str1, row[0])
                                                    j += 1
                                                except UniqueViolationError as uve:
                                                    duplicate_row_number += 1
                                                    pass
                                                finally:
                                                    if (csv_row_number % 10000) == 0:
                                                        print(j, "/", csv_row_number, "kayıt eklendi.",
                                                              duplicate_row_number, "tekrar ve",
                                                              except_row_number, "hatalı kayıt var.")
                                                    pass
                                        print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
                                        print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ",
                                              except_row_number, " kayıt hatalı.")
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


if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("firehol.ini")
    if args.schedule is None:
        args.schedule = int(conf.get(name, 'url_schedule'))
    if args.url is None:
        args.url = conf.get(name, 'url')
    schedule.every(args.schedule).minutes.do(
        lambda: asyncio.get_event_loop().run_until_complete(ipsetFromfirehol()))
    asyncio.get_event_loop().run_until_complete(ipsetFromfirehol())
    while True:
        schedule.run_pending()
        time.sleep(10)