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
parser.add_argument('--ip', dest='ip', type=str, help='Query IP Address')
parser.add_argument('--mode', dest='mode', type=str, help='Update Records From FEODOtracker, --mode updateRecords')
parser.add_argument('--csv', dest='csv', type=str,
                     help='Csv file path(c:/data.csv) or url(https://feodotracker.abuse.ch/downloads/ipblocklist.csv)')
parser.add_argument('--txt', dest='txt', type=str,
                     help='txt file path(c:/data.txt) or url(https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt)')
parser.add_argument('--url', dest='url', type=str,
                     help='--url https://feodotracker.abuse.ch/browse/host/')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]
tempFolder = os.path.join(tempfile.gettempdir(), name)

async def csvFromFEODOtracker():
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
            args.csv = conf.get(name, 'csv_url')
        if str(args.csv).startswith("http"):
            r = requests.get(args.csv)
            if r.status_code == 200:
                # temp = tempfile.gettempdir()
                # print(temp)
                # tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                ext = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])
                if ext == ".zip":
                    with open(os.path.join(tempFolder,'file') + ext, 'wb') as f:
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
                    i = 0
                    if (not row[0].startswith("#") and not row[0].startswith("first_seen_utc")):
                        sql_str1 = "INSERT INTO public.malips(" \
                                   "first_seen_utc, ip, port, ip_status, lastreportedat, resource_name, maintype, subtype, user_name, datetime)" \
                                   "VALUES($1,$2,$3,$4,$5, 'FEODOtracker', 'Botnet', $6, 'admin', CURRENT_TIMESTAMP) RETURNING id"
                        try:
                            csv_row_number += 1
                            post_id = await conn.fetchval(sql_str1, row[0], row[1], int(row[2]), row[3], row[4], row[5])
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

async def txtFromFEODOtracker():
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    fileName1 = ""
    # name = os.path.splitext(os.path.basename(__file__))[0]
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if args.txt is None:
            conf = configparser.ConfigParser()
            conf.read("settings.ini")
            args.csv = conf.get(name, 'txt_url')
        if str(args.txt).startswith("http"):
            r = requests.get(args.txt)
            if r.status_code == 200:
                temp = tempfile.gettempdir()
                print(temp)
                tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                ext = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])
                if ext == ".zip":
                    with open(os.path.join(tempFolder,'file') + ext, 'wb') as f:
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
            fname = args.txt
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
                    if (not row[0].startswith("#") and not row[0].startswith("first_seen_utc")):
                        sql_str1 = "INSERT INTO public.malips(" \
                                   "ip, resource_name, maintype, subtype, user_name, datetime)" \
                                   "VALUES($1,'FEODOtracker', 'Botnet', 'Blocklist', 'admin', CURRENT_TIMESTAMP) RETURNING id"
                        try:
                            csv_row_number += 1
                            post_id = await conn.fetchval(sql_str1, row[0])
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


async def updateRecordsFromFEODOtracker():
    # todo burası yapılacak
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        driver_exe = 'chromedriver'
        options = Options()
        options.add_argument("--headless")
        if os.name == 'nt':
            driver = webdriver.Chrome(chrome_options=options, executable_path=r'g:\chromedriver.exe')
        else:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')

        sql_str = """SELECT * FROM malips WHERE  resource_name = 'FEODOtracker' and (usagetype is NULL or domainname is NULL or hostname is NULL 
                    or country is NULL or confidence_level is NULL)"""
        try:
            rows = await conn.fetch(sql_str)
            aa = len(rows)
            print(aa)
        except Exception as e:
            print("hata:>", e, e.__class__, sql_str[sql_str.index('VALUES'):sql_str.index('VALUES') + 50])
        #conf = configparser.ConfigParser()
        #conf.read("settings.ini")
        url = args.url #conf.get(name, 'checkip_url')

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
                print(str2)
                # todo buraya bak
                for st in str2:
                    pass

                confidence_level = 0
                hostname = ""
                country = ""
                first_seen_utc = ""
                lastupdatedat = ""
                i = 0
                k = 0
                # if str1.find('Usage Type') > -1:
                #     k += 1
                #     usagetype = str2[k][11:]
                if str1.find('Hostname:') > -1:
                    k += 1
                    hostname = str2[k][10:]
                elif str1.find('Country:') > -1:
                    k += 1
                    country = str2[k][8:]
                elif str1.find('First seen:') > -1:
                    k += 1
                    first_seen_utc = str2[k][8:]
                elif str1.find('Last online:') > -1:
                    k += 1
                    lastupdatedat = str2[k][8:]
                else:
                    k+=1

                if row[8] is None:
                    i += 1
                    columns.append(hostname)
                    sql_str1 = sql_str1 + "hostname=$" + str(i) + ","
                if row[9] is None:
                    i += 1
                    columns.append(country)
                    sql_str1 = sql_str1 + "country=$" + str(i) + ","
                if row[9] is None:
                    i += 1
                    columns.append(first_seen_utc)
                    sql_str1 = sql_str1 + "first_seen_utc=$" + str(i) + ","
                if row[9] is None:
                    i += 1
                    columns.append(lastupdatedat)
                    sql_str1 = sql_str1 + "lastupdatedat=$" + str(i) + ","
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

async def feodotrackerlookupDetail(ip):
    # todo burası yapılacak
    # todo scraping yapılacak
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    url = conf.get(name, 'api_url')
    response_json = ''
    while response_json == '':
        try:
            if args.api_key is None: args.api_key = 'api_key'
            # if args.action is None: args.action = action
            if args.hash is None: args.hash = hash
            response_json = requests.get(url, headers=None, params={  # url parameters
                'api_key': args.api_key,
                'hash': args.hash,
                'action': 'details',
            })
            data = response_json.json()
            # break
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

async def csv_txt_fromFEODOtracker():
    await csvFromFEODOtracker()
    await txtFromFEODOtracker()


if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("settings.ini")
    if args.ip is not None:
        print('')
        print(
            "##########################################################################################################")
        print("FEODOtracker Malicious IP Info for the IP: " + args.ip)
        print(
            "##########################################################################################################")
        print('')
        print('')
        feodotrackerlookupDetail(args.ip)
    elif args.mode is not None and args.mode == 'updateRecords':
        if args.schedule is None:            
            args.schedule = int(conf.get(name, 'checkip_url_schedule'))
        if args.url is None:
            args.url = conf.get(name, 'checkip_url')
        schedule.every(args.schedule).minutes.do(
            lambda: asyncio.get_event_loop().run_until_complete(updateRecordsFromFEODOtracker()))
        asyncio.get_event_loop().run_until_complete(updateRecordsFromFEODOtracker())
        while True:
            schedule.run_pending()
            time.sleep(2)
    else:
        if args.schedule is None
            args.schedule = int(conf.get(name, 'csv_url_schedule'))
        if args.csv is None:
            args.csv = conf.get(name, 'csv_url')
        if args.txt is None:
            args.txt = conf.get(name, 'txt_url')
            schedule.every(args.schedule).minutes.do(
                lambda: asyncio.get_event_loop().run_until_complete(csv_txt_fromFEODOtracker()))
            asyncio.get_event_loop().run_until_complete(csv_txt_fromFEODOtracker())
            while True:
                schedule.run_pending()
                time.sleep(1)