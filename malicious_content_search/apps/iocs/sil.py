import re
# reg = r'^/s/(([^/]*)((/[^/]+)*))$'
patern = '/home/users/[0-9]/'
patern = '/home/'
url = '/home/users/'
regex = re.compile(patern)
aa = re.match(regex, url)
print(aa is not None)

sil = {'58': 'ff:13', '45': 'dddddddd:0', '46': 'bizim sirket:1', '29': 'admin333222111:12', '31': 'saasdas:-16', '53': 'dssss:1', '54': 'diger sirket1111:0', '55': 'bizim sirket333:8', '56': 'ccc:0', '16': 'admin66:-6', '17': 'admin55:-6', '37': 're1444:-5', '43': 'sw111:1', '20': 'admin1234554321:1', '27': 'admin12222:-23', '30': 'a company:-24', '48': 'rrrreee:1', '44': 'admin9999:22', '52': 'dasdas:-13', '50': 'ddd:2', '49': 'diger sirket1:-3', '42': 'sss:-22', '60': 'tt1234567:13'}
print('::>',sil['58'])
print('::',sil[58])
