import configparser

from django import template
from django.contrib.auth.decorators import login_required
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime
import json
import os
import tempfile

import asyncpg
from asyncpg import UniqueViolationError
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.template import loader
from django.urls import reverse

from apps.home.models import Company
from apps.home.utilities import isUserAuthMenu
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env"))
name = os.path.splitext(os.path.basename(__file__))[0]
temp = tempfile.gettempdir()
tempFolder = os.path.join(temp, name)
tm = 'UC'


# @login_required(login_url="auth/login/")
async def iocs_index(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        try:
            interval = request.GET['id']
            if not isinstance(int(interval), int):
                interval = 1
        except Exception as e:
            interval = 1

        cid = request.session['company_id']
        apikey = Company.objects.get(id=cid).apikey
        # url = 'http://10.8.0.34:5000/iocs/api/v1/'
        conf = configparser.ConfigParser()
        conf.read("apps/iocs/settings.ini")
        url = conf.get(tm, 'restapiurl')
        # url = 'http://185.214.134.100:5000/iocs/api/v1/'
        try:
            response = requests.post(url, json={'interval': interval}, auth=('1', apikey), timeout=2.50)
            context = json.loads(response.text)
            # context = await getStatistics(int(interval))
            # context = json.loads(context)
            # if (type(context) == str):
            #     context = json.loads(context)
            # err = context['query_status']
            if response.status_code != 500:
                mesaj = 'Daily selected'
                if interval == '7':
                    mesaj = 'Weekly selected'
                elif interval == '30':
                    mesaj = 'Monthly selected'
                messages.success(request, mesaj)
                return render(request, 'iocs/index.html', context)
            else:
                messages.error(request, context['data'])
                return render(request, 'iocs/index.html')
        except ConnectionError as ce:
            context = {"data": "Unexpected api error"}
            messages.error(request, context['data'])
            return render(request, 'iocs/index.html')
        except Exception as e:
            context = {"data": "Unexpected api error"}
            messages.error(request, context['data'])
            return render(request, 'iocs/index.html')
    except Exception as e:
        context = {"data": "Unexpected api error"}
        messages.error(request, context['data'])
        return render(request, 'iocs/index.html')
    finally:
        pass
    return render(request, 'iocs/index.html', context)


@login_required(login_url="auth/login/")
def iocs_search(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('iocs/page-404.html')
    cid = request.session['company_id']
    apikey = Company.objects.get(id=cid).apikey
    context = {}
    context['apikey'] = apikey
    conf = configparser.ConfigParser()
    conf.read("apps/iocs/settings.ini")
    url = conf.get(tm, 'restapiurl')
    context['url'] = url
    return render(request, 'iocs/search.html', context)


def iocs_index1(request):
    return render(request, 'iocs/index1.html')


def iocs_starter(request):
    return render(request, 'iocs/starter.html')


def home_view(request):
    return render(request, 'iocs/home.html')
# @login_required(login_url="auth/login/")
# def pages(request):
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
#
#         load_template = request.path.split('/')[-1]
#
#         if load_template == 'admin':
#             return HttpResponseRedirect(reverse('admin:index'))
#         context['segment'] = load_template
#
#         html_template = loader.get_template('home/' + load_template)
#         return HttpResponse(html_template.render(context, request))
#
#     except template.TemplateDoesNotExist:
#
#         html_template = loader.get_template('home/page-404.html')
#         return HttpResponse(html_template.render(context, request))
#
#     except:
#         html_template = loader.get_template('home/page-500.html')
#         return HttpResponse(html_template.render(context, request))


def getConnection():
    db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
    return asyncpg.connect(db_conn_str)

async def getStatistics(interval):
    try:
        dizi = {}
        today = datetime.date.today()
        if interval == 1:
            filename = 'DailyStatistics_' + str(today)
        elif interval == 7:
            filename = 'WeeklyStatistics_' + str(today)
        elif interval == 30:
            filename = 'MonthlyStatistics_' + str(today)
        else:
            interval = 1
            filename = 'DailyStatistics_' + str(today)
        if not os.path.exists(tempFolder):
            os.mkdir(tempFolder)
        path = tempFolder + os.path.sep + filename + '.json'
        interval = str(interval)
        db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
        conn = await asyncpg.connect(db_conn_str)
        if os.path.isfile(path):
            f = open(path, "r")
            data = json.loads(f.read())
            f.close()

            sql_str9 = "SELECT * FROM (SELECT iocvalue, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" + interval + "' day group by iocvalue limit 10) tbl ORDER by tbl.sayi desc"
            row9 = await conn.fetch(sql_str9)
            searches = {}
            searches.update(row9)

            data['searches'] = searches;
            with open(path, 'r+') as f:
                f.truncate(0)
                f.seek(0)
            f = open(path, "a")
            f.truncate()
            dizi = json.dumps(data)
            f.write(dizi)
            f.close()
        else:
            sql_str1 = "SELECT 'malwares' as type, count(*) as sayi FROM malwares WHERE datetime > current_date - interval '" +interval+ "' day"
            sql_str2 = "SELECT 'malips' as type, count(*) as sayi FROM malips WHERE datetime > current_date - interval '" +interval+ "' day"
            sql_str3 = "SELECT 'maldomains' as type, count(*) as sayi FROM maliocs WHERE ioctype = 'domain' and datetime > current_date - interval '" +interval+ "' day"
            sql_str4 = "SELECT 'malurls' as type, count(*) as sayi FROM maliocs WHERE ioctype = 'url' and datetime > current_date - interval '" +interval+ "' day"
            sql_str5 = "SELECT resource_name, count(*) as sayi FROM malwares WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str6 = "SELECT resource_name, count(*) as sayi FROM malips WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str7 = "SELECT resource_name, count(*) as sayi FROM maliocs WHERE datetime > current_date - interval '" +interval+ "' day group by resource_name"
            sql_str8 = "SELECT ioctype, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" +interval+ "' day group by ioctype"
            sql_str9 = "SELECT * FROM (SELECT iocvalue, count(*) as sayi FROM SEARCHES WHERE datetime > current_date - interval '" +interval+ "' day group by iocvalue limit 10) tbl ORDER by tbl.sayi desc"

            row1 = await conn.fetch(sql_str1)
            row2 = await conn.fetch(sql_str2)
            row3 = await conn.fetch(sql_str3)
            row4 = await conn.fetch(sql_str4)
            conn.close()
            db_conn_str = 'postgresql://' + config('DATABASE_USER') + ':'+ config('DATABASE_PASS') + '@localhost/'+ config('DATABASE_NAME')
            conn = await asyncpg.connect(db_conn_str)
            row5 = await conn.fetch(sql_str5)
            row6 = await conn.fetch(sql_str6)
            row7 = await conn.fetch(sql_str7)
            row8 = await conn.fetch(sql_str8)
            row9 = await conn.fetch(sql_str9)
            data = {}
            types = {}
            searches = {}
            data.update(row1)
            data.update(row2)
            data.update(row3)
            data.update(row4)

            data1 = {}
            data1.update(row5)
            data2 = {}
            data2.update(row6)
            data3 = {}
            data3.update(row7)
            data4 = await updateDict(data1, data2)
            data5 = await updateDict(data4, data3)

            # data.update(row5)
            # data.update(row6)
            data.update(data5)
            types.update(row8)
            searches.update(row9)
            dizi = json.dumps({'data': data, 'types': types, 'searches': searches})
            f = open(path, "a")
            f.write(dizi)
            f.close()

    except UniqueViolationError as uve:
        print('hata::>', uve)
    except Exception as e:
        print('hata::>', e)
    finally:
        if conn is not None:
            conn.close
    return dizi


async def updateDict(dict1, dict2):
    for key2, value2 in dict2.items():
        knt = 0
        for key1, value1 in dict1.items():
            if key2 == key1:
                knt = 1
                dict1[key1] = value1 + value2
                break
        if knt == 0:
            dict1[key2] = value2
    return dict1


@login_required(login_url="auth/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('iocs/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('iocs/page-500.html')
        return HttpResponse(html_template.render(context, request))