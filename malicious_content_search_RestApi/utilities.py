import ipaddress
import validators
import re

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
    ipport = '62.182.156.24:12780'.split(':')
    print(len(ipport))
    print(ipport[1].isnumeric())
    print(validate_ip_address(ipport[0]))
    if len(ipport) == 2 and validate_ip_address(ipport[0]) and ipport[1].isnumeric():
        ioctype = "ip"

    print('23'.isnumeric())

    print(validate_ip_address('2.3.3.4'))
    print(md5('2ffad5dbd034ba211818daa42d988b7a'))
    print(sha1('54338e23346a09524aw9dfebe23606d0df9aee25'))
    print(sha256('2076f68cce9b78a9677bcw85212c1f9045e3c1db5b13173b1d7a16fzf73e32dq'))
    print(validators.url("http://google.com"))
    print(validators.url("http://1.2.3.4:90"))
    print(validators.url("http://1.2.3.4:90/dfdf/a.css"))
    print(validators.url("http://abc.google.com:90"))
    print(validators.url("https://abc.google.com:90/a.html"))
    print(validators.url("https://abc.google.com:90/a.jsp?a=4"))
    print(validators.url("https://abc1.google.com:90/a.html/s"))
    print(validators.url("www.kuppers.info"), "    --->")
    print(validators.url("www.aliveli.com:90"))
    print(validators.url("http://www.59.99.200.127:35556/i"))


    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    print(re.match(regex, "http://ww1.examPle.com") is not None)  # True
    print(re.match(regex, "http://www.59.99.200.127:35556/i") is not None)  # False
    print(re.match(regex, "www.google.com") is not None)  # True
    print(re.match(regex, "www.aliveli.com:90") is not None)  # False
    print(re.match(regex, "https://abc.google.com:90/a.jsp?a=4") is not None)  # True
    print(re.match(regex, "http://google.m") is not None)  # False
    print(re.match(regex, "www.abc.google.com") is not None)  # True
    print(re.match(regex, "http://1.2.3.4:90") is not None)  # False