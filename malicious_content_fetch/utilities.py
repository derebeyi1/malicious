import ipaddress
import os

import asyncpg
import requests
from asyncpg import UniqueViolationError
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))

async def error_write_db(hata_str):
    try:
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        sql_str = "INSERT INTO public.logs(log, ip, user_name, datetime)" \
                  " VALUES ($1, '127.0.0.1', 'admin', CURRENT_TIMESTAMP)"
        # print(sql_str)
        try:
            await conn.execute(sql_str, hata_str)
        except UniqueViolationError as uve:
            print("hata:>", uve, uve.__class__, sql_str[sql_str.index('VALUES'):sql_str.index('VALUES') + 50])
        except Exception as e:
            print("hata:>", e, e.__class__, sql_str[sql_str.index('VALUES'):sql_str.index('VALUES') + 50])
    except Exception as e:
        print("hata:>", e, e.__class__, sql_str[sql_str.index('VALUES'):sql_str.index('VALUES') + 50])
    finally:
        await conn.close()

def get_bytes_from_file(filename):
    return open(filename, "rb").read()

def write_bytes_to_file(binarydata):
    with open("file1.zip", "wb") as f:
        return f.write(binarydata)
        # f.close()

async def mal_file_write_db(post_id, she256_hash, name):
    try:
        payload = {"query": "get_file",
                   "sha256_hash": she256_hash,
                   }
        r = requests.post("https://mb-api.abuse.ch/api/v1/", data=payload)
        file_name = "file.zip"
        if r.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(r.content)
                f.close()
            byteaa = get_bytes_from_file(file_name)

        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        sql_str = "INSERT INTO public.mal_files(malwares_id, file_name, file, file_size, ip, username, datetime)" \
                  " VALUES ($1, $2, $3, $4, '127.0.0.1', 'admin', CURRENT_TIMESTAMP)"
        #print(sql_str, post_id, file_name, byteaa, 1)
        try:
            await conn.execute(sql_str, post_id, file_name, byteaa, 1)
        except UniqueViolationError as uve:
            await error_write_db("ERROR:" + name + ".py:%s:%s" % (uve, uve.__class__))
        except Exception as e:
            await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    except Exception as e:
        await error_write_db("ERROR:" + name + ".py:%s:%s" % (e, e.__class__))
    finally:
        await conn.close()


def validate_ip_address(address):
    try:
        ip = ipaddress.ip_address(address)
        # print("IP address {} is valid. The object returned is {}".format(address, ip))
        return True
    except ValueError:
        # print("IP address {} is not valid".format(address))
        return False

def md5(hash):
    hs = 'ae11fd697ec92c7c98de3fac23aba525'
    if len(hash)==len(hs) and hash.isdigit()==False and hash.isalpha()==False and hash.isalnum()==True:
        return True
    else:
        return False

def sha256(hash):
    hs = '2c740d20dab7f14ec30510a11f8fd78b82bc3a711abe8a993acdb323e78e6d5e'
    if len(hash)==len(hs) and hash.isdigit()==False and hash.isalpha()==False and hash.isalnum()==True:
        return True
    else:
        return False

def sha1(hash):
    hs = '4a1d4dbc1e193ec3ab2e9213876ceb8f4db72333'
    if len(hash)==len(hs) and hash.isdigit()==False and hash.isalpha()==False and hash.isalnum()==True:
        return True
    else:
        return False

def sha384(hash):
    hs='3b21c44f8d830fa55ee9328a7713c6aad548fe6d7a4a438723a0da67c48c485220081a2fbc3e8c17fd9bd65f8d4b4e6b'
    if len(hash)==len(hs) and hash.isdigit()==False and hash.isalpha()==False and hash.isalnum()==True:
        return True
    else:
        return False


if __name__ == '__main__':
    print(os.name)