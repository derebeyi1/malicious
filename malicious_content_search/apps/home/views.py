import datetime

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from apps.authentication.models import GroupMenu, UserCompany, MyUser
from apps.home.forms import CompanyForm, MyUserChangeForm, MenuForm, GroupMenuForm
from apps.home.models import Company, Country, Menu
from apps.home.utilities import licensetypeTags, companysizeTags, activityareaTags, securitygradeTags, \
    getUserCompaniesIds, isUserAuthMenu, getUsers, getUserCompaniesUsersIds, sendmail, getUserMenu1, getCompanyUsers, \
    getCompaniesIds, getCompanies, getGroupIdForUserRole, getUserMenuStrIdsForRole, getGroupMenuObjects

from django.contrib.auth.models import User, Group


@login_required(login_url="auth/login/")
def companies(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                id = request.POST.get('id')
                if id is None or id == '':
                    form = CompanyForm(request.POST or None, request.FILES or None)
                else:
                    company = get_object_or_404(Company, pk=id)
                    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
                # form = CompanyForm(request.POST or None, request.FILES or None)
                if form.is_valid():
                    try:
                        image = request.FILES['logo']
                        context['image'] = image
                    except MultiValueDictKeyError as me:
                        image = None
                    company = form.save(commit=False)
                    company.username = request.user.username
                    if image is not None:
                        company.logo = image
                    # company.modified = datetime.datetime.now()
                    company.save()
                    if id is None or id == '':
                        form.cleaned_data['id'] = company.id
                    # messages.success(request,
                    #                  "The company named " + company.name + " has been successfully created.")
                    # context['messages'] = messages.get_messages(request)
                    # form = CompanyForm()
                    # context['form'] = form
                    # context['form_error'] = False
                    if image is not None:
                        form.cleaned_data['logo'] = str(image)
                    elif form.cleaned_data['logo'] is not None:
                        form.cleaned_data['logo'] = form.cleaned_data['logo'].name
                    else:
                        form.cleaned_data['logo'] = 'None'
                    data = form.cleaned_data
                    # img_path = data['logo'].url
                    # data['logo'] = str(img_path)
                    if id is None or id == '':
                        message = 'The company named ' + company.name + ' has been successfully created.'
                    else:
                        message = 'The company named ' + company.name + ' has been successfully updated.'
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
                id = request.GET.get('id')
                company = get_object_or_404(Company, pk=id)
                if company.logo is None or company.logo.name == '':
                    company.logo = 'None'
                ser_comp = serializers.serialize('json', [company, ])
                return JsonResponse({"instance": ser_comp}, status=200)
        else:
            if request.method == 'POST':
                form = CompanyForm(request.POST or None, request.FILES or None)
                if form.is_valid():
                    try:
                        image = request.FILES['logo']
                        context['image'] = image
                    except MultiValueDictKeyError as me:
                        pass
                    company = form.save(commit=False)
                    company.username = request.user.username
                    company.save()
                    messages.success(request, "The company named " + company.name + " has been successfully created.")
                    context['messages'] = messages.get_messages(request)
                    form = CompanyForm()
                    context['form'] = form
                    context['form_error'] = False
                else:
                    context['form_error'] = True
                    form = CompanyForm(request.POST or None)
                    context['form'] = form
            else:
                form = CompanyForm(request.POST or None)
                context['form'] = form
            if request.user.is_superuser and request.user.id == 1:
                companies = Company.objects.all()
            else:
                companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
            countries = Country.objects.values_list('name', flat=True)
            context['countries'] = list(countries)
            context['licensetypeTags'] = licensetypeTags()
            context['companysizeTags'] = companysizeTags()
            context['activityareaTags'] = activityareaTags()
            context['securitygradeTags'] = securitygradeTags()
            context['page_obj'] = companies
    except Exception as e:
        pass
    return render(request, "home/companies.html", context)


# @login_required(login_url="auth/login/")
# def company_create(request):
#     if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
#     # if not (request.user.is_authenticated):
#         return redirect('home/page-404.html')
#     context = {}
#     try:
#         if request.method == 'POST':
#             form = CompanyForm(request.POST or None)
#             if form.is_valid():
#                 company = form.save(commit=False)
#                 company.username = request.user.username
#                 company.save()
#                 # messages.success(request, "The company named " + form.cleaned_data['name'] + " has been successfully created.")
#                 # context['messages'] = messages.get_messages(request)
#                 form = CompanyForm()
#                 # return HttpResponseRedirect(reverse('home:companies', kwargs={'messages': messages.get_messages(request)}))
#             else:
#                 form = CompanyForm(request.POST or None)
#         else:
#             form = CompanyForm(request.POST or None)
#     except Exception as e:
#         form = CompanyForm()
#     # companies = Company.objects.all().order_by('-modified')
#     countries = Country.objects.values_list('name', flat=True)
#     # context['companies'] = companies
#     context['countries'] = list(countries)
#     context['licensetypeTags'] = licensetypeTags()
#     context['companysizeTags'] = companysizeTags()
#     context['activityareaTags'] = activityareaTags()
#     context['securitygradeTags'] = securitygradeTags()
#     context['form'] = form
#     return render(request, "home/company.htm", context)


# @login_required(login_url="auth/login/")
# def getcompany(request, id):
#     if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
#         return redirect('home/page-404.html')
#     user = User.objects.get(id=request.user.id)
#     ids = getUserCompaniesIds(user.id)
#     if id not in ids and not user.is_superuser:
#         return redirect('home/page-404.html')
#     context = {}
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         if request.method == 'GET':
#             company = get_object_or_404(Company, pk=id)
#             if company.logo is None or company.logo.name == '':
#                 company.logo = 'None'
#             ser_comp = serializers.serialize('json', [company, ])
#             return JsonResponse({"instance": ser_comp}, status=200)
#         # else:
#         #     company = get_object_or_404(Company, pk=id)
#         #     form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
#         #     if form.is_valid():
#         #         try:
#         #             image = request.FILES['logo']
#         #             context['image'] = image
#         #         except Exception as e:
#         #             pass
#         #         company = Company.objects.get(pk=id)
#         #         company.username = request.user.username
#         #         form = CompanyForm(request.POST, request.FILES or None, instance=company)
#         #         form.save()
#         #         messages.success(request, "The company named " + company.name + " has been successfully updated.")
#         #         context['messages'] = messages.get_messages(request)
#         #         form = CompanyForm()
#         #         # context['form_error'] = False
#         #     else:
#         #         context['form_error'] = True
#         #         form = CompanyForm(request.POST or None, request.FILES or None)
#         #     if request.user.is_superuser and request.user.id == 1:
#         #         companies = Company.objects.all()
#         #     else:
#         #         companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
#         #     context['page_obj'] = companies
#         #     countries = Country.objects.values_list('name', flat=True)
#         #     context['countries'] = list(countries)
#         #     context['licensetypeTags'] = licensetypeTags()
#         #     context['companysizeTags'] = companysizeTags()
#         #     context['activityareaTags'] = activityareaTags()
#         #     context['securitygradeTags'] = securitygradeTags()
#         #     context['form'] = form
#         #     context['islem'] = 'update'
#     # else:
#     #     if request.method == 'POST':
#     #         company = get_object_or_404(Company, pk=id)
#     #         form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
#     #         if form.is_valid():
#     #             try:
#     #                 image = request.FILES['logo']
#     #                 context['image'] = image
#     #             except Exception as e:
#     #                 pass
#     #             company = Company.objects.get(pk=id)
#     #             company.username = request.user.username
#     #             form = CompanyForm(request.POST, request.FILES or None, instance=company)
#     #             form.save()
#     #             messages.success(request, "The company named " + company.name + " has been successfully updated.")
#     #             context['messages'] = messages.get_messages(request)
#     #             form = CompanyForm()
#     #             # context['form_error'] = False
#     #         else:
#     #             context['form_error'] = True
#     #             form = CompanyForm(request.POST or None, request.FILES or None)
#     #         if request.user.is_superuser and request.user.id == 1:
#     #             companies = Company.objects.all()
#     #         else:
#     #             companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
#     #         context['page_obj'] = companies
#     #         countries = Country.objects.values_list('name', flat=True)
#     #         context['countries'] = list(countries)
#     #         context['licensetypeTags'] = licensetypeTags()
#     #         context['companysizeTags'] = companysizeTags()
#     #         context['activityareaTags'] = activityareaTags()
#     #         context['securitygradeTags'] = securitygradeTags()
#     #         context['form'] = form
#     #         context['islem'] = 'update'
#     #         # return render(request, "home/company.html", context)
#     #     else:
#     #         company = get_object_or_404(Company, id=id)
#     #         form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
#     #         context['form'] = form
#     #         companies = Company.objects.all().order_by('-modified')
#     #         context['companies'] = companies
#     #         countries = Country.objects.values_list('name', flat=True)
#     #         context['countries'] = list(countries)
#     #         context['licensetypeTags'] = licensetypeTags()
#     #         context['companysizeTags'] = companysizeTags()
#     #         context['activityareaTags'] = activityareaTags()
#     #         context['securitygradeTags'] = securitygradeTags()
#     #         context['islem'] = 'update'
#     #         if request.user.is_superuser and request.user.id == 1:
#     #             companies = Company.objects.all()
#     #         else:
#     #             companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
#     #         context['page_obj'] = companies
#     #     return render(request, 'home/company.html', context)


@login_required(login_url="auth/login/")
def company_users(request, id):
    mesaj = ''
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    # user = User.objects.get(id=request.user.id)
    context = {}
    company = Company.objects.get(id=id)
    if request.user.is_superuser and request.user.id == 1:
        users = getCompanyUsers(id)
        if users is None or len(users) == 0:
            mesaj = 'No users found.'
        context = {
            'mesaj': mesaj,
            'companyusers': users,
            'companyname': company.name
        }
        return render(request, 'home/companyusers.html', context)
    else:
        users = getCompanyUsers(id)
        if users is None or len(users) == 0:
            mesaj = 'No users found.'
        else:
            users1 = users.filter(id=request.user.id)
            if users1 is None or len(users1) == 0:
                return redirect('home/page-404.html')
        context = {
            'mesaj': mesaj,
            'companyusers': users,
            'companyname': company.name
        }
        return render(request, 'home/companyusers.html', context)
    # ids = getCompanyUsers(company.id)
    # if id not in ids and not user.is_superuser:
    #     return redirect('home/page-404.html')
    #


@login_required(login_url="auth/login/")
def company_delete(request, id):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    # bu firmayı silmek için yetkisi var mı?
    user = User.objects.get(id=request.user.id)
    ids = getUserCompaniesIds(user.id)
    if id not in ids and not user.is_superuser:
        return redirect('home/page-404.html')
    context = {}
    company = get_object_or_404(Company, id=id)
    companyname = company.name
    company.delete()
    messages.success(request, "The company named " + companyname + " has been successfully deleted.")
    context['messages'] = messages.get_messages(request)
    if request.user.is_superuser and request.user.id == 1:
        companies = Company.objects.all()
    else:
        companies = Company.objects.filter(id__in=(getUserCompaniesIds(request.user.id))).order_by('-modified')
    context['page_obj'] = companies
    return HttpResponseRedirect(reverse('home:companies'))


@login_required(login_url="auth/login/")
def users(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                id = request.POST.get('id')
                groupid = request.POST.get('group')
                if id is None or id == '':
                    form = MyUserChangeForm(request.POST or None)
                else:
                    user = get_object_or_404(User, pk=id)
                    form = MyUserChangeForm(request.POST or None, instance=user)
                if form.is_valid():
                    user = form.save()
                    myuser = MyUser.objects.create(user=user)
                    print(type(user))
                    print(myuser)
                    group = Group.objects.get(id=groupid)
                    # user = User.objects.get(username=request.POST.get('username'))
                    user.groups.add(group)
                    # username = form.cleaned_data.get("username")
                    # email/print password
                    # raw_password = uuid.uuid4()

                    # raw_password = '.123Ankara'
                    if id is None or id == '':
                        password = User.objects.make_random_password(length=20, allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                                                                              'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                                                                              '23456789'
                                                                                              '.,;:@*-+/$#&%=?')
                        user.set_password(password)
                        print(password)
                        user.save(update_fields=['password'])
                    # user.set_password(raw_password)
                    # user.save()
                    # aa = request.get_full_path()
                    # bb = request.get_raw_uri()
                    # cc = request.build_absolute_uri()
                    # dd = request.get_host()
                    # ee = request.get_port()
                        sendmail(user, 'Welcome to UC, here is your password :', password,
                                 'http://' + request.get_host())
                    ids = form.cleaned_data['companies']
                    ucs = UserCompany.objects.filter(user_id=user.id)
                    ucs.delete()
                    for id in ids:
                        try:
                            uc = UserCompany(userid=user.id, companyid=id)
                            uc.save()
                        except IntegrityError as ie:
                            pass
                    data = form.cleaned_data
                    data['groups'] = list(data['groups'])
                    if id is None or id == '':
                        message = 'The user named ' + user.username + ' has been successfully created.'
                    else:
                        message = 'The user named ' + user.username + ' has been successfully updated.'
                    return JsonResponse({'data': data, 'message': message}, status=200)
                else:
                    data = form.errors.as_json()
                    return JsonResponse({'data': data}, status=400)
                    """ context['form_error'] = True
                    form = MyUserChangeForm(request.POST or None)
                    context['form'] = form """
            else:
                id = request.GET.get('id')
                user = User.objects.get(id=id)
                myuser = MyUser.objects.filter(id=id)
                print(myuser)
                ids = user.groups.values_list('id', flat=True)
                if user.is_authenticated and user.is_superuser:
                    # companies = user.companies
                    companies = Company.objects.order_by('-id').values_list('id', flat=True)
                else:
                    # companies = user.myuser.companies
                    companies = UserCompany.objects.filter(user_id=user.id).values_list('company_id', flat=True)
                initial = {
                    'group': list(ids),
                    'companies': list(companies)
                }
                # user = User.objects.get(id=id)
                # ids = user.groups.values_list('id', flat=True)
                # if user.is_authenticated and user.is_superuser:
                #     companies = Company.objects.order_by('-id').values_list('id', flat=True)
                # else:
                #     companies = UserCompany.objects.filter(userid=user.id).values_list('companyid', flat=True)
                # initial = {
                #     'group': list(ids),
                #     'companies': list(companies)
                # }
                # ser_usr = serializers.serialize('json', [user, ])
                # ser_user = serializers.serialize('json', user)
                # i = 0;
                # response_data = {}
                # for e in user.iterator():
                #     c = User(value=e.value, date=str(e.date));
                # response_data[0] = user;
                # ss = serializers.serialize("json", response_data)
                # ser_user = {"ss": ss}
                # form = MyUserChangeForm(instance=ser_user)
                # company = get_object_or_404(Company, pk=id)
                # form = MyUserChangeForm(request.GET or None, instance=user)
                # form = MyUserChangeForm(instance=user, initial=initial)
                # aa = form['fields']
                # bb = form['initial']
                # if form.is_valid():
                #     data = form.cleaned_data()
                # else:
                #     data = form.errors.as_json()
                # user = get_object_or_404(User, pk=id)
                # ser_usr = serializers.serialize('json', [user, ])
                ser_usr = serializers.serialize("json", [user, ])
                d = json.loads(ser_usr)

                # jsonString = json.dumps(list(ids))
                # jsonString1 = json.dumps(list(companies))
                aa = d[0]['fields']['group'] = list(ids)
                bb = d[0]['fields']['companies'] = list(companies)
                print(d)
                dd = json.dumps(d)
                # ser_usr = serializers.serialize("json", d)
                # data = {"User_json": ser_usr}
                # return JsonResponse({}, status=200)
                return JsonResponse({"instance": dd}, status=200)
        else:
            form = MyUserChangeForm()
            context['form'] = form
        user = User.objects.get(id=request.user.id)
        if user.id == 1 and user.is_superuser:  # todo
            users = User.objects.all().order_by('-date_joined')
        else:
            users = getUsers(user)
        context['page_obj'] = users
    except Exception as e:
        print(e)
        context['form_error'] = True
        form = MyUserChangeForm(request.POST or None)
        context['form'] = form
        messages.success(request, e)
        context['messages'] = messages.get_messages(request)
        user = User.objects.get(id=request.user.id)
        if user.id == 1 and user.is_superuser:  # todo
            users = User.objects.all().order_by('-date_joined')
        else:
            users = getUsers(user)
        context['page_obj'] = users
    return render(request, "home/users.html", context)


# @login_required(login_url="auth/login/")
# def user_create(request):
#     if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
#         return redirect('home/page-404.html')
#     context = {}
#     try:
#         if request.method == 'POST':
#             form = User(request.POST or None)
#             if form.is_valid():
#                 company = form.save(commit=False)
#                 company.username = request.user.username
#                 company.save()
#                 messages.success(request, "The user named " + form.cleaned_data['username'] + " has been successfully created.")
#                 context['messages'] = messages.get_messages(request)
#                 form = MyUserChangeForm()
#                 # return HttpResponseRedirect(reverse('home:companies', kwargs={'messages': messages.get_messages(request)}))
#             else:
#                 form = MyUserChangeForm(request.POST or None)
#         else:
#             form = MyUserChangeForm(request.POST or None)
#     except Exception as e:
#         form = MyUserChangeForm()
#     # companies = Company.objects.all().order_by('-modified')
#     countries = Country.objects.values_list('name', flat=True)
#     # context['companies'] = companies
#     context['countries'] = list(countries)
#     context['licensetypeTags'] = licensetypeTags()
#     context['companysizeTags'] = companysizeTags()
#     context['activityareaTags'] = activityareaTags()
#     context['securitygradeTags'] = securitygradeTags()
#     context['form'] = form
#     return render(request, "home/user.html", context)


# @login_required(login_url="auth/login/")
# def user_update(request, id):
#     if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
#         return redirect('iocs/page-404.html')
#     user = User.objects.get(id=request.user.id)
#     ids = getUserCompaniesUsersIds(user.id)
#     if id not in ids and not user.is_superuser:
#         return redirect('home/page-404.html')
#     context = {}
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         if request.method == 'GET':
#             user = User.objects.get(id=id)
#             ids = user.groups.values_list('id', flat=True)
#             if user.is_authenticated and user.is_superuser:
#                 companies = Company.objects.order_by('-id').values_list('id', flat=True)
#             else:
#                 companies = UserCompany.objects.filter(userid=user.id).values_list('companyid', flat=True)
#             initial = {
#                 'group': list(ids),
#                 'companies': list(companies)
#             }
#             # user = User.objects.get(id=id)
#             # ids = user.groups.values_list('id', flat=True)
#             # if user.is_authenticated and user.is_superuser:
#             #     companies = Company.objects.order_by('-id').values_list('id', flat=True)
#             # else:
#             #     companies = UserCompany.objects.filter(userid=user.id).values_list('companyid', flat=True)
#             # initial = {
#             #     'group': list(ids),
#             #     'companies': list(companies)
#             # }
#             # ser_usr = serializers.serialize('json', [user, ])
#             # ser_user = serializers.serialize('json', user)
#             # i = 0;
#             # response_data = {}
#             # for e in user.iterator():
#             #     c = User(value=e.value, date=str(e.date));
#             # response_data[0] = user;
#             # ss = serializers.serialize("json", response_data)
#             # ser_user = {"ss": ss}
#             # form = MyUserChangeForm(instance=ser_user)
#             # company = get_object_or_404(Company, pk=id)
#             # form = MyUserChangeForm(request.GET or None, instance=user)
#             # form = MyUserChangeForm(instance=user, initial=initial)
#             # aa = form['fields']
#             # bb = form['initial']
#             # if form.is_valid():
#             #     data = form.cleaned_data()
#             # else:
#             #     data = form.errors.as_json()
#             # user = get_object_or_404(User, pk=id)
#             # ser_usr = serializers.serialize('json', [user, ])
#             ser_usr = serializers.serialize("json", [user, ])
#             d = json.loads(ser_usr)
#
#
#             # jsonString = json.dumps(list(ids))
#             # jsonString1 = json.dumps(list(companies))
#             aa = d[0]['fields']['group'] = list(ids)
#             bb = d[0]['fields']['companies'] = list(companies)
#             print(d)
#             dd = json.dumps(d)
#             # ser_usr = serializers.serialize("json", d)
#             # data = {"User_json": ser_usr}
#             # return JsonResponse({}, status=200)
#             return JsonResponse({"instance": dd}, status=200)
#         else:
#             user = get_object_or_404(User, pk=id)
#             form = MyUserChangeForm(request.POST or None, request.FILES or None, instance=user)
#             if form.is_valid():
#                 user = User.objects.get(pk=id)
#                 user.username = request.user.username
#                 form = MyUserChangeForm(request.POST, request.FILES or None, instance=user)
#                 form.save()
#                 messages.success(request, "The user " + user.name + " has been successfully updated.")
#                 context['messages'] = messages.get_messages(request)
#                 form = MyUserChangeForm()
#             else:
#                 context['form_error'] = True
#                 form = MyUserChangeForm(request.POST or None, request.FILES or None)
#             if request.user.is_superuser and request.user.id == 1:
#                 users = User.objects.all()
#             else:
#                 users = User.objects.filter(id__in=(getUsersIds(request.user.id))).order_by(
#                     '-modified')
#             context['page_obj'] = users
#             context['groupsTags'] = groupsTags()
#             context['companiesTags'] = companiesTags()
#             context['form'] = form
#             context['islem'] = 'update'
#     else:
#         groupid = request.POST.get('group')
#         if request.method == 'POST':
#             user = User.objects.get(id=id)
#             # ids = user.groups.values_list('id', flat=True)
#             # if user.is_authenticated and user.is_superuser:
#             #     companies = Company.objects.order_by('-id').values_list('companyid', flat=True)
#             # else:
#             #     companies = UserCompany.objects.filter(userid=user.id).values_list('companyid', flat=True)
#             # initial = {
#             #     'group': list(ids),
#             #     'companies': list(companies)
#             # }
#             form = MyUserChangeForm(request.POST, instance=user)
#             if form.is_valid():
#                 form.save()
#                 gid = form.cleaned_data['group']
#                 group = Group.objects.get(id=gid)
#                 # user = User.objects.get(username=request.POST.get('username'))
#                 user.groups.add(group)
#                 cids = form.cleaned_data['companies']
#                 ucs = UserCompany.objects.filter(userid=user.id)
#                 ucs.delete()
#                 for id in cids:
#                     uc = UserCompany(userid=user.id, companyid=id)
#                     try:
#                         uc.save()
#                     except IntegrityError as ie:
#                         pass
#                 messages.success(request, "The user named '" + user.username + "' has been successfully updated.")
#                 context['messages'] = messages.get_messages(request)
#                 initial = {
#                     'group': [],
#                     'companies': []
#                 }
#                 form = MyUserChangeForm(initial=initial)
#             else:
#                 context['form_error'] = True
#                 form = MyUserChangeForm(request.POST or None)
#             context['form'] = form
#         else:
#             # todo
#             user = User.objects.get(id=id)
#             ids = user.groups.values_list('id', flat=True)
#             if user.is_authenticated and user.is_superuser:
#                 companies = Company.objects.order_by('-id').values_list('id', flat=True)
#             else:
#                 companies = UserCompany.objects.filter(userid=user.id).values_list('companyid', flat=True)
#             initial = {
#                 'group': list(ids),
#                 'companies': list(companies)
#             }
#             form = MyUserChangeForm(instance=user, initial=initial)
#             # groups = Group.objects.order_by('-id').filter(id=id).values_list('id', 'name')
#             # form.fields['group'].initial = [3]
#             # form.initial['group'] = [1]
#             # form.fields['groups'].initial = list(groups)[0]
#             # if user.is_authenticated and user.is_superuser:
#             #     companies = Company.objects.order_by('-id').values_list('id', 'name')
#             # else:
#             #     companies = UserCompany.objects.filter(userid=user.id).values_list('id', 'name')
#             # form.companies = list(companies)
#             # form.fields['companies'].initial = [56,43,44]
#             # form.initial['companies'] = [58]
#             context['form'] = form
#             context['islem'] = 'update'
#
#             user = User.objects.get(id=request.user.id)
#             if user.id == 1 and user.is_superuser:  # todo
#                 users = User.objects.all().order_by('-date_joined')
#             else:
#                 users = getUsers(user)
#             context['page_obj'] = users
#         return render(request, 'home/user.html', context)


@login_required(login_url="auth/login/")
def user_delete(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('iocs/page-404.html')
    # bu kullanıcıyı silmek için yetkisi var mı?
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id = request.GET.get('id')
        user = User.objects.get(id=request.user.id)
        ids = getUserCompaniesUsersIds(user.id)
        if id not in ids and not user.is_superuser:
            return redirect('iocs/page-404.html')
        # context = {}
        user = get_object_or_404(User, id=id)
        user.delete()
        message = 'The user named ' + user.username + ' has been successfully deleted.'
        # context['messages'] = messages.get_messages(request)
        # user = User.objects.get(id=request.user.id)
        # if user.id == 1 and user.is_superuser:  # todo
        #     users = User.objects.all().order_by('-date_joined')
        # else:
        #     users = getUsers(user)
        # context['page_obj'] = users
        return JsonResponse({'message': message}, status=200)
    else:
        pass


@login_required(login_url="auth/login/")
def user_companies(request, id):
    message = ''
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('iocs/page-404.html')
    context = {}
    if request.user.is_superuser and request.user.id == 1:
        companies = getCompanies(id)
    else:
        ids = getCompaniesIds(request.user.id)
        uids = UserCompany.objects.filter(companyid__in=ids).values_list('userid', flat=True)
        if id in uids:
            cids = getUserCompaniesIds(id)
            companies = Company.objects.filter(id__in=cids)
        else:
            return redirect('iocs/page-404.html')
        if companies is None or len(companies) == 0:
            mesaj = 'No companies found.'

    context = {
        'message': message,
        'usercompanies': companies,
    }
    return render(request, 'home/usercompanies.html', context)
    # else:
    #     companies = getUserCompanies()
    #     if companies is None or len(companies) == 0:
    #         mesaj = 'No companies found.'
    #     else:
    #         companies = users.filter(id=request.company.id)
    #         if companies is None or len(companies) == 0:
    #             return redirect('home/page-404.html')
    #     context = {
    #         'mesaj': mesaj,
    #         'companyusers': users,
    #         'companyname': companies.name
    #     }
    #     return render(request, 'home/usercompanies.html', context)



@login_required(login_url="auth/login/")
def menus(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == 'POST':
                id = request.POST.get('id')
                if id is None or id == '':
                    form = MenuForm(request.POST or None, request.FILES or None)
                else:
                    menu = get_object_or_404(Menu, pk=id)
                    form = MenuForm(request.POST or None, request.FILES or None, instance=menu)
                # form = MenuForm(request.POST or None)
                if form.is_valid():
                    menu = form.save()
                    if id is None or id == '':
                        form.cleaned_data['id'] = menu.id
                    data = form.cleaned_data
                    if id is None or id == '':
                        message = 'The ' + menu.title + ' has been successfully created.'
                    else:
                        message = 'The  ' + menu.title + ' has been successfully updated.'
                    return JsonResponse({'data': data, 'message': message}, status=200)
                else:
                    data = form.errors.as_json()
                    return JsonResponse({'data': data}, status=400)
            else:
                id = request.GET.get('id')
                menu = Menu.objects.get(id=id)
                ser_menu = serializers.serialize('json', [menu, ])
                # if request.user.is_superuser and request.user.id == 1:
                #     menus = Menu.objects.all().order_by('id')
            return JsonResponse({'instance': ser_menu}, status=200)
        else:
            groupid = request.GET.get('groupid')
            form = MenuForm(request.GET or None)
            if groupid is None:
                groupid = getGroupIdForUserRole()
            context = {
                'form': form,
                'groupid': groupid,
                'menus': getGroupMenuObjects(1),
                'usermenuarr': getUserMenuStrIdsForRole(groupid)
            }
    except Exception as e:
        messages.success(request, e)
        context['messages'] = messages.get_messages(request)
    return render(request, "home/menus.html", context)


@login_required(login_url="auth/login/")
def menu_update(request, id):
    try:
        context = {}
        if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
            return redirect('iocs/page-404.html')
        if request.method == 'POST':
            menu = Menu.objects.get(id=id)
            form = MenuForm(request.POST or None, request.FILES or None, instance=menu)
            if form.is_valid():
                form.save()
                messages.success(request, "The " + menu.title + " has been successfully updated.")
                context['messages'] = messages.get_messages(request)
                form = MenuForm()
            else:
                context['form_error'] = True
                form = MenuForm(request.POST or None)
            context['form'] = form
        else:
            menu = Menu.objects.get(id=id)
            form = MenuForm(request.POST or None, request.FILES or None, instance=menu)
            context['form'] = form
            context['islem'] = 'update'
        user = User.objects.get(id=request.user.id)
        if user.id == 1 and user.is_superuser:
            menus = Menu.objects.all().order_by('id')
        context['page_obj'] = menus
        return render(request, 'home/menu.html', context)
    except Exception as e:
        print(e)
    return render(request, 'home/menu.html', context)


@login_required(login_url="auth/login/")
def menu_delete(request, id):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    return render(request, "home/menus.html", context)


@login_required(login_url="auth/login/")
def role_menu(request):
    if not (request.user.is_authenticated and isUserAuthMenu(request.path, request.user)):
        return redirect('home/page-404.html')
    context = {}
    try:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.method == "POST":
                group_id = request.POST.get('group_id')
                gms = GroupMenu.objects.filter(group_id=group_id)
                # form = GroupMenuForm(request.POST or None, instance=um)
                form = GroupMenuForm(request.POST or None)
                if form.is_valid():
                    if gms is None or len(gms) == 0:
                        menu_ids_str = request.POST.get('usermenu')
                        menu_ids = menu_ids_str.split(',')
                        for menu_id in menu_ids:
                            gm = GroupMenu.objects.create(group_id=group_id, menu_id=menu_id)
                            gm.save()
                        messages.success(request,
                                         "The menu authorization is done successfully.")
                    else:
                        gms.delete()
                        menu_ids_str = request.POST.get('usermenu')
                        menu_ids = menu_ids_str.split(',')
                        for menu_id in menu_ids:
                            gm = GroupMenu.objects.create(group_id=group_id, menu_id=menu_id)
                            gm.save()
                        message = "The menu authorization is done successfully."
                    form = GroupMenuForm()
                    menus = serializers.serialize("json", getGroupMenuObjects(1))
                    usermenuarr = list(getUserMenuStrIdsForRole(group_id))
                    context = {
                        'form': form,
                        'group_id': group_id,
                        'menus': menus,
                        'usermenuarr': usermenuarr,
                        'message': message
                    }
                    return JsonResponse(context, status=400)
                else:
                    context['form_error'] = True
                    form = GroupMenuForm(request.POST or None)
                    context = {
                        'form': form,
                        'group_id': group_id,
                        'menus': getGroupMenuObjects(1),
                        'usermenuarr': getUserMenuStrIdsForRole(group_id)
                    }
            else:
                group_id = request.GET.get('group_id')
                # menus = json.dumps(list(getGroupMenuObjects(1))),
                menus = serializers.serialize("json", getGroupMenuObjects(1))
                usermenuarr = list(getUserMenuStrIdsForRole(group_id))
                # usermenuarr = json.dumps(list(getUserMenuStrIdsForRole(group_id))),
                context = {
                    # 'form': form,
                    'group_id': group_id,
                    'menus': menus,
                    'usermenuarr': usermenuarr
                }
                return JsonResponse(context, status=200)
        else:
            if request.method == 'POST':
                pass
            else:
                group_id = request.GET.get('group_id')
                form = GroupMenuForm(request.GET or None)
                if group_id is None:
                    group_id = getGroupIdForUserRole()
                context = {
                    'form': form,
                    'group_id': group_id,
                    'menus': getGroupMenuObjects(1),
                    'usermenuarr': getUserMenuStrIdsForRole(group_id)
                }
                pass
    except Exception as e:
        print(e)
    return render(request, "home/rolemenu.html", context)


@login_required(login_url="auth/login/")
def index(request):
    try:
        cid = request.GET['id']
        request.session['company_id'] = cid
        company = Company.objects.get(id=cid)
        lastday = company.licenseenddate - datetime.date.today()
        request.session['company_name'] = company.name
        request.session['company_lastday'] = lastday.days
        # request.session['company'] = cid

        context = {'segment': 'index'}
        if request.META['HTTP_REFERER'] is not None:
            return redirect(request.META['HTTP_REFERER'])
        else:
            html_template = loader.get_template('home/dashboard.html')
            return HttpResponse(html_template.render(context, request))
    except MultiValueDictKeyError as me:
        pass
    context = {'segment': 'index'}
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))


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

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def get_user_menu(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "GET":
        userid = request.GET.get("id", None)
        menuhtml = getUserMenu1(int(userid))
        return JsonResponse(menuhtml, status=200, safe=False)
    else:
        return JsonResponse({}, status=400)



