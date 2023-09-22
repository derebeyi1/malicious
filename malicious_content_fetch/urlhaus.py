import argparse
import configparser
import csv
import mimetypes
import os
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
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Query sample information by Hash or Csv File Address.')
parser.add_argument('--hash', dest='hash', type=str, help='Query Hash (MD5)')
parser.add_argument('--csv', dest='csv', type=str,
                     help='Csv file path(c:/data.csv) or url(https://bazaar.abuse.ch/export/csv/recent/)')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]

async def csvFromURLHaus():
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    fileName1 = ""
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if args.csv is None:
            conf = configparser.ConfigParser()
            conf.read("settings.ini")
            args.csv = conf.get(name, 'data_url')
        if str(args.csv).startswith("http"):
            r = requests.get(args.csv)
            if r.status_code == 200:
                temp = tempfile.gettempdir()
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
            fname = args.csv
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
                    if (not row[0].startswith("#")):
                        sql_str1 = "INSERT INTO public.maliocs(" \
                                   "first_seen_utc, ioctype, iocvalue, iocstatus, tags, resource_name, maintype, subtype, user_name, datetime)" \
                                   "VALUES($1,'url',$2,$3,$4, 'URLhaus', 'Malurl', $5, 'admin', CURRENT_TIMESTAMP) RETURNING id"
                        try:
                            csv_row_number += 1;
                            # await conn.execute(sql_str1, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
                            post_id = await conn.fetchval(sql_str1, row[1], row[2], row[3], row[5], row[4])
                            j += 1
                        except UniqueViolationError as uve:
                            duplicate_row_number += 1
                            pass
                        finally:
                            if (csv_row_number % 10000) == 0:
                                print(j, "/", csv_row_number, "kayıt eklendi.", duplicate_row_number, "tekrar ve", except_row_number, "hatalı kayıt var.")
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


async def urlhauslookup(hash):
    # todo
    pass


if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    if args.schedule is None:
        args.schedule = int(conf.get(name, 'data_url_schedule'))
    if args.hash is not None:
        print('')
        print(
            "##########################################################################################################")
        print("URLhaus MalUrl Info for the HASH: " + args.hash)
        print(
            "##########################################################################################################")
        print('')
        print('')

        urlhauslookup(args.hash)
    if args.csv is None:
        args.csv = conf.get(name, 'csv_url')
        asyncio.get_event_loop().run_until_complete(csvFromURLHaus())
        args.csv = conf.get(name, 'data_url')

    schedule.every(args.schedule).minutes.do(
        lambda: asyncio.get_event_loop().run_until_complete(csvFromURLHaus()))
    asyncio.get_event_loop().run_until_complete(csvFromURLHaus())
    while True:
        schedule.run_pending()
        time.sleep(1)