import argparse
import asyncio
import logging
import os
import time

import asyncpg
import schedule
from asyncpg import UniqueViolationError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utilities import error_write_db
import configparser
from webdriver_manager.chrome import ChromeDriverManager
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
parser = argparse.ArgumentParser(description='Fetching sample information by Scraping.')
parser.add_argument('--schedule', dest='schedule', type=int, help='minute')
args = parser.parse_args()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
hata_str = ""
name = os.path.splitext(os.path.basename(__file__))[0]


async def scrapFromVXVaultUrl():
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        name = os.path.splitext(os.path.basename(__file__))[0]
        except_row_number = 0
        txt_row_number = 0
        duplicate_row_number = 0
        j = 0
        options = Options()
        options.add_argument("--headless")
        if os.name == 'nt':
            # driver = webdriver.Chrome(chrome_options=options, executable_path=r'g:\chromedriver.exe')
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        else:
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
            # driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/local/bin/chromedriver')
        driver.get('http://vxvault.net/ViriList.php')
        xpath = "(//div[@id='page']//child::tr[2]//child::a)"
        elem = driver.find_element(By.XPATH, xpath)
        link = elem.get_attribute('href')
        conf = configparser.ConfigParser()
        conf.read("vxvault.ini")
        conf.set(name, 'last_id', link.split("=")[1])
        conf.write(open("vxvault.ini", "w"))
        id = int(conf.get(name, 'id'))
        last_id = int(conf.get(name, 'last_id'))
        sql_str1 = "INSERT INTO public.malwares(file_name, size, md5_hash, sha1_hash, sha256_hash, url, ip, first_seen_utc, resource_name, maintype, subtype, user_name, datetime)" \
                   " VALUES ($1,$2,$3,$4,$5,$6,$7,$8, 'VXVault', 'Malware', 'abuse', 'admin', CURRENT_TIMESTAMP) RETURNING id"
        dongu = True
        while dongu:
            file_name = ""
            size = 0
            md5_hash = ""
            sha1_hash = ""
            sha256_hash = ""
            url = ""
            ip = ""
            first_seen_utc = ""
            driver.get('http://vxvault.net/ViriFiche.php?ID=' + str(id))
            a = driver.find_element(By.ID, 'page')
            # print(id, a.text)
            aa = a.text.split("\n")
            if a.text.find('Hash not found.') > -1:
                # print('Hash not found.', id)
                id1 = id + 1
                i = 0
                k = 0
                while i < 20:
                    driver.get('http://vxvault.net/ViriFiche.php?ID=' + str(id1))
                    a = driver.find_element(By.ID, 'page')
                    # print(id1, a.text)
                    if a.text.find('Hash not found.') > -1:
                        id1 += 1
                        i += 1
                    else:
                        id = id1
                        k += 1
                        aa = a.text.split("\n")
                        break
                if k == 0:
                    dongu = False
                    break
            else:
                pass
            if dongu:
                for data in aa:
                    if data == '' or data.startswith("Tools"):
                        pass
                    elif data.startswith("File"):
                        file_name = data.split(": ")[1]
                    elif data.startswith("Size"):
                        size = int(data.split(": ")[1])
                    elif data.startswith("MD5"):
                        md5_hash = data.split(": ")[1]
                    elif data.startswith("SHA-1"):
                        sha1_hash = data.split(": ")[1]
                    elif data.startswith("SHA-256"):
                        sha256_hash = data.split(": ")[1]
                    elif data.startswith("Link"):
                        url = data.split(": ")[1]
                    elif data.startswith("IP"):
                        ip = data.split(": ")[1]
                    elif data.startswith("Added"):
                        first_seen_utc = data.split(": ")[1]
                    else:
                        pass

                try:
                    txt_row_number += 1
                    if sha256_hash == '':
                        sha256_hash = md5_hash
                    post_id = await conn.fetchval(sql_str1, file_name, size, md5_hash, sha1_hash, sha256_hash, url,
                                                  ip, first_seen_utc)
                    j += 1
                except UniqueViolationError as uve:
                    duplicate_row_number += 1
                    pass
                except Exception as e:
                    except_row_number += 1
                    await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
                    pass
                finally:
                    id += 1
                    conf.set(name, 'id', str(id))
                    conf.write(open("vxvault.ini", "w"))
                    pass
                if j % 100 == 0:
                    print("RESULT: ", txt_row_number, " kayıttan ", j, " kayıt eklendi.")
                    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number,
                          " kayıt hatalı.")
            time.sleep(1)
        driver.quit()
        print('while dan çıktı')
    except IndexError as ie:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    except Exception as e:
        except_row_number += 1
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()

    print("RESULT: ", txt_row_number, " kayıttan ", j, " kayıt eklendi.")
    print("WARNING: ", duplicate_row_number, " kayıt tekrar etti ve ", except_row_number, " kayıt hatalı.")


if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read("vxvault.ini")
    if args.schedule is None:
        args.schedule = int(conf.get(name, 'data_url_schedule'))
    schedule.every(args.schedule).minutes.do(
        lambda: asyncio.get_event_loop().run_until_complete(scrapFromVXVaultUrl()))
    asyncio.get_event_loop().run_until_complete(scrapFromVXVaultUrl())
    while True:
        schedule.run_pending()
        time.sleep(1)
