import argparse
import configparser
import csv
import os
import tempfile

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
parser = argparse.ArgumentParser(description='Query sample information by Csv File Address.')
parser.add_argument('--url', dest='url', type=str,
                    help='Url like https://virusshare.com/hashfiles/VirusShare_00000.md5')
# parser.add_argument('--csv', dest='csv', type=str, help='Csv file path(c:/data.csv)')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
now = datetime.now()
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]

async def md5FromVirusShare():
    csv_row_number = 0
    duplicate_row_number = 0
    except_row_number = 0
    conf = configparser.ConfigParser()
    conf.read("virusshare.ini")
    j = 0
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if str(args.url).startswith("http"):
            if str(args.url).find("VirusShare_") <= -1:
                url = args.url
                fname = os.path.dirname(os.path.realpath(__file__))
                temp = tempfile.gettempdir()
                tempFolder = os.path.join(temp, name)
                if not os.path.exists(tempFolder):
                    os.mkdir(tempFolder)
                str1 = str(url).split('/')[4]
                fname = tempFolder + os.path.sep + str1
                if os.path.isfile(fname) and os.path.getsize(fname) > 0:
                    print("WARNING :", fname, " dosyası daha önce aktarılmıştır. ")
                    pass
                else:
                    r = requests.get(url)
                    if r.status_code == 404:
                        print(url, " sayfası bulunamadı. 404")
                    else:
                        str1 = str(url).split('/')[4]
                        fname = tempFolder + os.path.sep + str1
                        with open(fname, 'wb') as write_obj:
                            write_obj.write(r.content)

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
                                    if (not row[0].startswith("#") and not row[0].startswith("Original_MD5")):
                                        md5_hash = row[0].split('  ')[0]
                                        sql_str1 = "INSERT INTO public.malwares(md5_hash, resource_name, maintype, subtype, user_name, datetime)" \
                                                   " VALUES ($1, 'VirusShare', 'Malware', 'abuse', 'admin', CURRENT_TIMESTAMP)"
                                        try:
                                            csv_row_number += 1
                                            await conn.execute(sql_str1, md5_hash)
                                            j += 1
                                        except UniqueViolationError as uve:
                                            duplicate_row_number += 1
                                            pass
                                        except Exception as e:
                                            except_row_number += 1
                                            pass
                                        finally:
                                            if (csv_row_number % 10000) == 0:
                                                print(j, "/", csv_row_number, "kayıt eklendi.", duplicate_row_number, "tekrar ve", except_row_number, "hatalı kayıt var.")
                                            pass
                                print("DOSYA ADI: ", "VirusShare_", str1, ".md5")
                                print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
                                print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number,
                                      " kayıt hatalı.")
                            except csv.Error as ce:
                                print(f'file {fname}, line {liste.line_num:d}: {ce}')
            else:
                k = 0
                # virusshare hash dosya isimlendirmesine göre sırayla hepsini indirir ve
                # db ye yazar
                # https://virusshare.com/hashfiles/unpacked_hashes.md5
                # https://virusshare.com/hashfiles/VirusShare_00000.md5
                # https://virusshare.com/hashfiles/VirusShare_00001.md5
                str1 = args.url[args.url.index('VirusShare_') + len('VirusShare_'):len(args.url) - 4]
                sil = str1.lstrip('0')
                if sil == '':
                    sil = 0
                url = args.url
                k = int(sil)
                last_id = int(conf.get(name, 'last_id'))
                dongu = True
                while dongu:
                    fname = os.path.dirname(os.path.realpath(__file__))
                    temp = tempfile.gettempdir()
                    tempFolder = os.path.join(temp, name)
                    if not os.path.exists(tempFolder):
                        os.mkdir(tempFolder)
                    fname = tempFolder + os.path.sep + "VirusShare_" + str1 + ".md5"
                    if not os.path.isfile(fname):
                        r = requests.get(url)
                        if r.status_code == 200:
                            fname = tempFolder + os.path.sep + "VirusShare_" + str1 + ".md5"
                            with open(fname, 'wb') as write_obj:
                                write_obj.write(r.content)

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
                                        if (not row[0].startswith("#") and not row[0].startswith("Original_MD5")):
                                            md5_hash = row[0].split('  ')[0]
                                            sql_str1 = "INSERT INTO public.malwares(md5_hash, resource_name, maintype, subtype, user_name, datetime)" \
                                                       " VALUES ($1, 'VirusShare', 'Malware', 'abuse', 'admin', CURRENT_TIMESTAMP)"
                                            try:
                                                csv_row_number += 1
                                                await conn.execute(sql_str1, md5_hash)
                                                j += 1
                                            except UniqueViolationError as uve:
                                                duplicate_row_number += 1
                                                pass
                                            except Exception as e:
                                                except_row_number += 1
                                                await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
                                                pass
                                            finally:
                                                if (csv_row_number % 10000) == 0:
                                                    print(j, "/", csv_row_number, "kayıt eklendi.", duplicate_row_number, "tekrar ve", except_row_number, "hatalı kayıt var.")
                                                pass
                                    print('DOSYA ADI: ', str(url).split('/')[4])
                                    print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
                                    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")
                                except csv.Error as ce:
                                    print(f'file {fname}, line {liste.line_num:d}: {ce}')
                                    k += 1
                                    str3 = str1
                                    str2 = str1[0:len(str1) - len(str(k))]
                                    str1 = str2 + str(k)
                                    url = url.replace(str3, str1)
                                    conf.set(name, 'last_data_url', url)
                                    conf.write(open("virusshare.ini", "w"))
                            k += 1
                            str3 = str1
                            str2 = str1[0:len(str1) - len(str(k))]
                            str1 = str2 + str(k)
                            url = url.replace(str3, str1)
                            conf.set(name, 'last_data_url', url)
                            conf.write(open("virusshare.ini", "w"))
                        else:
                            dongu = False
                            break

                    else:
                        print("WARNING :", fname, " dosyası daha önce aktarılmıştır. ")
                        k += 1
                        str3 = str1
                        str2 = str1[0:len(str1) - len(str(k))]
                        str1 = str2 + str(k)
                        url = url.replace(str3, str1)
                        conf.set(name, 'last_data_url', url)
                        conf.write(open("virusshare.ini", "w"))
        else:
            fname = args.url
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
                    for row in csv_reader:
                        if (not row[0].startswith("#") and not row[0].startswith("Original_MD5")):
                            md5_hash = row[0].split('  ')[0]
                            sql_str1 = "INSERT INTO public.malwares(md5_hash, resource_name, maintype, subtype, user_name, datetime)" \
                                       " VALUES ('" + md5_hash + "', 'VirusShare', 'Malware', 'abuse', 'admin', CURRENT_TIMESTAMP)"
                            try:
                                csv_row_number += 1
                                await conn.execute(sql_str1)
                                j += 1
                            except UniqueViolationError as uve:
                                duplicate_row_number += 1
                                pass
                            except Exception as e:
                                except_row_number += 1
                                await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
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
    if csv_row_number != 0:
        print("RESULT: ", csv_row_number, " kayıttan ", j, " kayıt eklendi.")
        print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("virusshare.ini")
    if args.schedule is None:
        args.schedule = int(conf.get(name, 'last_data_url_schedule'))
    if args.url is None:
        args.url = conf.get(name, 'csv_url')
        asyncio.get_event_loop().run_until_complete(md5FromVirusShare())
        args.url = conf.get(name, 'last_data_url')

    schedule.every(args.schedule).minutes.do(
        lambda: asyncio.get_event_loop().run_until_complete(md5FromVirusShare()))
    asyncio.get_event_loop().run_until_complete(md5FromVirusShare())
    while True:
        schedule.run_pending()
        time.sleep(1)