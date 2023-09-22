import json
import re

from django.contrib import messages
from django.contrib.auth.models import User
from django.core import serializers
from django.db import migrations
from django.forms import modelformset_factory, model_to_dict
from django.db import models
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from apps.analyst.forms import AlarmTypeForm, ContentTypeForm, AlarmForm, ContentForm
from apps.analyst.models import AlarmType, ContentType, Alarm, Content, AlarmCompany
from apps.home.models import Company
from apps.home.utilities import isUserAuthMenu, getUserCompaniesIds, get_severities, get_alarmtypes


@login_required(login_url="auth/login/")
def alarmtypes(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                id = request.POST.get('id')
                if id is None or id == '':
                    form = AlarmTypeForm(request.POST or None, request.FILES or None)
                else:
                    alarmtype = get_object_or_404(AlarmType, pk=id)
                    form = AlarmTypeForm(request.POST or None, request.FILES or None, instance=alarmtype)
                if form.is_valid():
                    alarmtype = form.save(commit=False)
                    alarmtype.username = request.user.username
                    alarmtype.ip = request.META.get("REMOTE_ADDR")
                    alarmtype.save()
                    if id is None or id == '':
                        form.cleaned_data['id'] = alarmtype.id
                    data = form.cleaned_data
                    if id is None or id == '':
                        message = 'The alarm type named ' + alarmtype.title + ' has been successfully created.'
                    else:
                        message = 'The alarm type named ' + alarmtype.title + ' has been successfully updated.'
                    return JsonResponse({'data': data, 'message': message}, status=200)
                    # ser_instance = serializers.serialize('json', data)
                else:
                    data = form.errors.as_json()
                    return JsonResponse({'data': data}, status=400)
            else:
                id = request.GET.get('id')
                alarmtype = get_object_or_404(AlarmType, pk=id)
                # if alarmtype.logo is None or company.logo.name == '':
                #     company.logo = 'None'
                ser_comp = serializers.serialize('json', [alarmtype, ])
                return JsonResponse({"data": ser_comp}, status=200)
        else:
            if request.method == 'GET':
                form = AlarmTypeForm(request.GET or None)
                context['form'] = form
            alarmtypes = AlarmType.objects.all()
            context['severities'] = get_severities()
            context['page_obj'] = alarmtypes
    except Exception as e:
        print(e)
    return render(request, "analyst/alarmtypes.html", context)


@login_required(login_url="auth/login/")
def alarmtype_update(request, id):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    # user = User.objects.get(id=request.user.id)
    # ids = getUserCompaniesIds(user.id)
    # if id not in ids and not user.is_superuser:
    #     return redirect('home/page-404.html')
    context = {}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'GET':
            company = get_object_or_404(AlarmType, pk=id)
            if company.logo is None or company.logo.name == '':
                company.logo = 'None'
            ser_comp = serializers.serialize('json', [company, ])
            return JsonResponse({"instance": ser_comp}, status=200)
        else:
            alarmtype = get_object_or_404(AlarmType, pk=id)
            form = AlarmTypeForm(request.POST or None, request.FILES or None, instance=alarmtype)
            # if form.is_valid():
            #     try:
            #         image = request.FILES['logo']
            #         context['image'] = image
            #     except Exception as e:
            #         pass
            #     company = Company.objects.get(pk=id)
            #     company.username = request.user.username
            #     form = CompanyForm(request.POST, request.FILES or None, instance=company)
            #     form.save()
            #     messages.success(request, "The company named " + company.name + " has been successfully updated.")
            #     context['messages'] = messages.get_messages(request)
            #     form = CompanyForm()
            #     # context['form_error'] = False
            # else:
            #     context['form_error'] = True
            #     form = CompanyForm(request.POST or None, request.FILES or None)
            # if request.user.is_superuser and request.user.id == 1:
            #     companies = Company.objects.all()
            # else:
            #     companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
            # context['page_obj'] = companies
            # countries = Country.objects.values_list('name', flat=True)
            # context['countries'] = list(countries)
            # context['licensetypeTags'] = licensetypeTags()
            # context['companysizeTags'] = companysizeTags()
            # context['activityareaTags'] = activityareaTags()
            # context['securitygradeTags'] = securitygradeTags()
            # context['form'] = form
            # context['islem'] = 'update'
    else:
        if request.method == 'POST':
            alarmtype = get_object_or_404(AlarmType, pk=id)
            form = AlarmTypeForm(request.POST or None, request.FILES or None, instance=alarmtype)
            # if form.is_valid():
            #     try:
            #         image = request.FILES['logo']
            #         context['image'] = image
            #     except Exception as e:
            #         pass
            #     company = Company.objects.get(pk=id)
            #     company.username = request.user.username
            #     form = CompanyForm(request.POST, request.FILES or None, instance=company)
            #     form.save()
            #     messages.success(request, "The company named " + company.name + " has been successfully updated.")
            #     context['messages'] = messages.get_messages(request)
            #     form = CompanyForm()
            #     # context['form_error'] = False
            # else:
            #     context['form_error'] = True
            #     form = CompanyForm(request.POST or None, request.FILES or None)
            # if request.user.is_superuser and request.user.id == 1:
            #     companies = Company.objects.all()
            # else:
            #     companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
            # context['page_obj'] = companies
            # countries = Country.objects.values_list('name', flat=True)
            # context['countries'] = list(countries)
            # context['licensetypeTags'] = licensetypeTags()
            # context['companysizeTags'] = companysizeTags()
            # context['activityareaTags'] = activityareaTags()
            # context['securitygradeTags'] = securitygradeTags()
            # context['form'] = form
            # context['islem'] = 'update'
            # return render(request, "home/company.html", context)
        else:
            alarmtype = get_object_or_404(AlarmType, id=id)
            form = AlarmType(request.POST or None, request.FILES or None, instance=alarmtype)
        return render(request, 'home/company.html', context)


@login_required(login_url="auth/login/")
def alarmtype_delete(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    # bu firmayı silmek için yetkisi var mı?
    id = request.GET.get('id')
    user = User.objects.get(id=request.user.id)
    ids = getUserCompaniesIds(user.id)
    if id not in ids and not user.is_superuser:
        return redirect('home/page-404.html')
    alarmtype = get_object_or_404(AlarmType, id=id)
    alarmtypename = alarmtype.title
    alarmtype.delete()
    message = 'The alarm type named ' + alarmtypename + ' has been successfully deleted.'
    return JsonResponse({"message": message}, status=200)


@login_required(login_url="auth/login/")
def content_type_create(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                # id = request.POST.get('id')
                form = ContentTypeForm(request.POST or None)
                # else:
                #     content_type = get_object_or_404(ContentType, pk=id)
                #     form = ContentTypeForm(request.POST or None, request.FILES or None, instance=content_type)
                # form = CompanyForm(request.POST or None, request.FILES or None)
                if form.is_valid():
                    # try:
                    #     image = request.FILES['logo']
                    #     context['image'] = image
                    # except MultiValueDictKeyError as me:
                    #     image = None
                    # company = form.save(commit=False)
                    # company.username = request.user.username
                    # if image is not None:
                    #     company.logo = image
                    # # company.modified = datetime.datetime.now()
                    content_type = form.save()
                    # if content_type.type == 'String':
                    #     migrations.AddField(
                    #         model_name='content',
                    #         name=content_type.name,
                    #         field=models.CharField(max_length=100, default=''),
                    #         preserve_default=False,
                    #     )
                    # elif content_type.type == 'Date':
                    #     migrations.AddField(
                    #         model_name='content',
                    #         name=content_type.name,
                    #         field=models.DateTimeField(null=True, blank=True),
                    #         preserve_default=False,
                    #     )
                    # elif content_type.type == 'File':
                    #     migrations.AddField(
                    #         model_name='content',
                    #         name=content_type.name,
                    #         field=models.ImageField(blank=True, null=True),
                    #         preserve_default=False,
                    #     )
                    # migrations.RunPython().noop()
                    # if id is None or id == '':
                    #     form.cleaned_data['id'] = content_type.id
                    # messages.success(request,
                    #                  "The company named " + company.name + " has been successfully created.")
                    # context['messages'] = messages.get_messages(request)
                    # form = CompanyForm()
                    # context['form'] = form
                    # context['form_error'] = False
                    # if image is not None:
                    #     form.cleaned_data['logo'] = str(image)
                    # elif form.cleaned_data['logo'] is not None:
                    #     form.cleaned_data['logo'] = form.cleaned_data['logo'].name
                    # else:
                    #     form.cleaned_data['logo'] = 'None'
                    data = form.cleaned_data
                    data['id'] = content_type.id
                    # img_path = data['logo'].url
                    # data['logo'] = str(img_path)
                    message = content_type.form_name + ' added.'
                    return JsonResponse({'data': data, 'message': message}, status=200)
                    # ser_instance = serializers.serialize('json', data)
                else:
                    data = form.errors.as_json()
                    return JsonResponse({'data': data}, status=400)
                    # context['form_error'] = True
                    # form = CompanyForm(request.POST or None)
                    # form = CompanyForm()
                    # context['form'] = form
                    # ser_instance = serializers.serialize('json', form)
                    # data = form.cleaned_data
                    # ser_comp = serializers.serialize('json', [company, ])
                    # return JsonResponse({"instance": ser_comp}, status=200)
                    # ser_instance = serializers.serialize('json', data)
                    # json_serializer.serialize(form)
                # return render(request, 'home/companies.html', context)
            else:
                pass
        else:
            pass
            # if request.method == 'POST':
            #     form = CompanyForm(request.POST or None, request.FILES or None)
            #     if form.is_valid():
            #         try:
            #             image = request.FILES['logo']
            #             context['image'] = image
            #         except MultiValueDictKeyError as me:
            #             pass
            #         company = form.save(commit=False)
            #         company.username = request.user.username
            #         company.save()
            #         messages.success(request, "The company named " + company.name + " has been successfully created.")
            #         context['messages'] = messages.get_messages(request)
            #         form = CompanyForm()
            #         context['form'] = form
            #         context['form_error'] = False
            #     else:
            #         context['form_error'] = True
            #         form = CompanyForm(request.POST or None)
            #         context['form'] = form
            # else:
            #     form = CompanyForm(request.POST or None)
            #     context['form'] = form
            # if request.user.is_superuser and request.user.id == 1:
            #     companies = Company.objects.all()
            # else:
            #     companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
            # countries = Country.objects.values_list('name', flat=True)
            # context['countries'] = list(countries)
            # context['licensetypeTags'] = licensetypeTags()
            # context['companysizeTags'] = companysizeTags()
            # context['activityareaTags'] = activityareaTags()
            # context['securitygradeTags'] = securitygradeTags()
            # context['page_obj'] = companies
    except Exception as e:
        print(e)
    return render(request, "analyst/alarmtypes.html")


@login_required(login_url="auth/login/")
def get_contents(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    try:
        # todo
        data = 'contentssssss'
    except Exception as e:
        pass
    return JsonResponse({"data": data}, status=200)


@login_required(login_url="auth/login/")
def get_alarm_type(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    try:
        alarm_type_id = request.GET.get('alarm_type_id')
        alarmtype = AlarmType.objects.get(id=alarm_type_id)
        ids = re.findall('(\d+)', alarmtype.content_type_ids)
        ctypes = ContentType.objects.filter(id__in=ids).values('id', 'name', 'form_name', 'type')
        ctypes_json = json.dumps(list(ctypes))
        data = serializers.serialize('json', [alarmtype, ])
        return JsonResponse({"data": data, "content_types": ctypes_json}, status=200)
    except Exception as e:
        print(e)


@login_required(login_url="auth/login/")
def alarms(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                id = request.POST.get('id')
                if id is None or id == '':
                    form = AlarmForm(request.POST or None, request.FILES or None)
                else:
                    alarm = get_object_or_404(Alarm, pk=id)
                    form = AlarmForm(request.POST or None, request.FILES or None, instance=alarm)
                if form.is_valid():
                    if id is not None and id != '':
                        # ac_ids = re.findall('(\d+)', alarm.content_ids)
                        # sil = list(ac_ids)
                        ac_ids_sp = alarm.content_ids.split(',')
                        ac_ids = []
                        for ac_id in ac_ids_sp:
                            if ac_id != '':
                                ac_ids.append(int(ac_id))
                        contents = Content.objects.filter(id__in=ac_ids)
                        contents.delete()
                    ctnames = request.POST.get('content_type_names').split(',')
                    your_dict = model_to_dict(Content,
                                              fields=ctnames,
                                              # exclude=["fields to exclude"]
                                              )
                    content_ids = ''
                    ct_count_str = request.POST.get('content_type_count')
                    try:
                        ct_count = int(ct_count_str)
                    except Exception as e:
                        ct_count = 11
                    for i in range(1, ct_count):
                        control = False
                        for ctname in ctnames:
                            if ctname is not None and ctname != '':
                                ctname_i = ctname + '_' + str(i)
                                val1 = request.POST.get(ctname_i)
                                try:
                                    image = request.FILES[ctname_i]
                                    context['image'] = image
                                except MultiValueDictKeyError as me:
                                    image = None
                                if (val1 is not None and val1 != '') or (image is not None and image != ''):
                                    control = True
                                    if ctname == 'screenshot':
                                        your_dict[ctname] = image
                                    else:
                                        your_dict[ctname] = request.POST.get(ctname_i)
                        if control:
                            form1 = ContentForm(your_dict)
                            if form1.is_valid():
                                if 'screenshot' in your_dict:
                                    image = your_dict['screenshot']
                                    cobj = form1.save(commit=False)
                                    if image is not None:
                                        cobj.screenshot = image
                                        cobj = form1.save()
                                else:
                                    cobj = form1.save()
                                content_ids += str(cobj.id) + ','
                            else:
                                error = form1.errors.as_json()
                    # if content_ids != '':
                    #     content_ids = content_ids[:-1]
                    # for key in request.POST.keys():
                    #     i = 1
                    #     for ctname in ctnames:
                    #         ctname1 = ctname + '_' + str(i)
                    #         if key.startswith(ctname1) and request.POST.get(ctname1) != '':
                    #             your_dict[ctname] = request.POST.get(ctname1)
                    # form1 = ContentForm(your_dict)
                    # if form1.is_valid():
                    #     cobj = form1.save()
                    # else:
                    #     error = form1.errors.as_json()
                    alarm = form.save(commit=False)
                    alarm.username = request.user.username
                    alarm.ip = request.META.get("REMOTE_ADDR")
                    alarm.content_ids = content_ids
                    alarm.analyst_state = 1  # 1:created, 2:Sent, 3:Approved, 4:Revoked
                    alarm.save()

                    if id is None or id == '':
                        form.cleaned_data['id'] = alarm.id
                    data = form.cleaned_data
                    companies_ids = form.cleaned_data['companies']
                    for company_id in companies_ids:
                        ac = AlarmCompany.objects.create(alarm_id=alarm.id, company_id=company_id, company_state=1,
                                                         username=alarm.username, ip=alarm.ip)
                        ac.save()

                    if id is None or id == '':
                        message = 'The alarm named ' + alarm.title + ' has been successfully created.'
                    else:
                        message = 'The alarm named ' + alarm.title + ' has been successfully updated.'
                    return JsonResponse({'data': data, 'message': message}, status=200)
                    # ser_instance = serializers.serialize('json', data)
                else:
                    data = form.errors.as_json()
                    return JsonResponse({'data': data}, status=400)
            else:
                id = request.GET.get('id')
                alarm = get_object_or_404(Alarm, pk=id)
                if alarm.content_ids != '':
                    content_ids = alarm.content_ids[:-1].split(',')
                alarm_type_id = alarm.alarm_type_id
                alarm_type = get_object_or_404(AlarmType, pk=alarm_type_id)
                content_type_ids = alarm_type.content_type_ids
                ids = re.findall('(\d+)', content_type_ids)

                ctypes = ContentType.objects.filter(id__in=ids).values('id', 'name', 'form_name', 'type')
                ctypes_json = json.dumps(list(ctypes))
                ct_names2 = list(ctypes)
                ct_names = []
                ct_form_names = []
                ct_types = []
                # for ct_name in ct_names1:
                #     names += ct_name['name'] + ','
                for ct_name in ct_names2:
                    ct_names.append(ct_name['name'])
                    ct_form_names.append(ct_name['form_name'])
                    ct_types.append(ct_name['type'])
                # names = names[:-1]
                # sil = ct_names1[0]
                list_contents = []
                if alarm.content_ids != '':
                    contents = Content.objects.filter(id__in=content_ids).values_list(*ct_names)
                    list_contents = list(contents)
                companies = AlarmCompany.objects.filter(alarm_id=alarm.id).values_list('company_id', flat=True)
                # ctypes_json = json.dumps(list(ctypes))
                # data = serializers.serialize('json', [alarmtype, ])
                # return JsonResponse({"data": data, "content_types": ctypes_json}, status=200)
                # if alarmtype.logo is None or company.logo.name == '':
                #     company.logo = 'None'
                ser_alarm = serializers.serialize('json', [alarm, ])
                d = json.loads(ser_alarm)
                bb = d[0]['fields']['companies'] = list(companies)
                dd = json.dumps(d)
                return JsonResponse({"data": dd, "contents": list_contents, "ct_names": ct_names, 'ct_form_names': ct_form_names, 'ct_types': ct_types, 'content_types': ctypes_json}, status=200)
        else:
            if request.method == 'GET':
                form = AlarmForm(request.GET or None)
                context['form'] = form
                context['ct_range'] = range(1, 11)
                context['ct_count'] = max(range(1, 11)) + 1
            alarms = Alarm.objects.all()
            context['severities'] = get_severities()
            context['alarmtypes'] = get_alarmtypes()
            context['page_obj'] = alarms
    except Exception as e:
        print(e)
    return render(request, "analyst/alarms.html", context)


@login_required(login_url="auth/login/")
def get_alarm(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'GET':
                id = request.GET.get('id')
                alarm = get_object_or_404(Alarm, pk=id)
                if alarm.content_ids != '':
                    content_ids = alarm.content_ids[:-1].split(',')
                alarm_type_id = alarm.alarm_type_id
                alarm_type = get_object_or_404(AlarmType, pk=alarm_type_id)
                content_type_ids = alarm_type.content_type_ids
                ids = re.findall('(\d+)', content_type_ids)

                ctypes = ContentType.objects.filter(id__in=ids).values('id', 'name', 'form_name', 'type')
                ctypes_json = json.dumps(list(ctypes))
                ct_names2 = list(ctypes)
                ct_names = []
                ct_form_names = []
                ct_types = []
                # for ct_name in ct_names1:
                #     names += ct_name['name'] + ','
                for ct_name in ct_names2:
                    ct_names.append(ct_name['name'])
                    ct_form_names.append(ct_name['form_name'])
                    ct_types.append(ct_name['type'])
                # names = names[:-1]
                # sil = ct_names1[0]
                list_contents = []
                if alarm.content_ids != '':
                    contents = Content.objects.filter(id__in=content_ids).values_list(*ct_names)
                    list_contents = list(contents)
                company_ids = AlarmCompany.objects.filter(alarm_id=alarm.id).values_list('company_id', flat=True)
                companies = Company.objects.filter(id__in=company_ids).values_list('name', flat=True)
                # ctypes_json = json.dumps(list(ctypes))
                # data = serializers.serialize('json', [alarmtype, ])
                # return JsonResponse({"data": data, "content_types": ctypes_json}, status=200)
                # if alarmtype.logo is None or company.logo.name == '':
                #     company.logo = 'None'
                ser_alarm = serializers.serialize('json', [alarm, ])
                d = json.loads(ser_alarm)
                bb = d[0]['fields']['companies'] = list(companies)
                dd = json.dumps(d)
                return JsonResponse({"data": dd, "contents": list_contents, "ct_names": ct_names, 'ct_form_names': ct_form_names, 'ct_types': ct_types, 'content_types': ctypes_json}, status=200)
        # else:
        #     if request.method == 'GET':
        #         form = AlarmForm(request.GET or None)
        #         context['form'] = form
        #         context['ct_range'] = range(1, 11)
        #         context['ct_count'] = max(range(1, 11)) + 1
        #     alarms = Alarm.objects.all()
        #     context['severities'] = get_severities()
        #     context['alarmtypes'] = get_alarmtypes()
        #     context['page_obj'] = alarms
    except Exception as e:
        print(e)
    return render(request, "analyst/alarms.html", context)


@login_required(login_url="auth/login/")
def alarm_delete(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    # bu alarmı silmek için yetkisi var mı?
    id = request.GET.get('id')
    # user = User.objects.get(id=request.user.id)
    # ids = getUserCompaniesIds(user.id)
    # if id not in ids and not user.is_superuser:
    #     return redirect('home/page-404.html')
    alarm = get_object_or_404(Alarm, id=id)
    alarmname = alarm.title
    alarm.delete()
    message = 'The alarm named ' + alarmname + ' has been successfully deleted.'
    return JsonResponse({"message": message}, status=200)
