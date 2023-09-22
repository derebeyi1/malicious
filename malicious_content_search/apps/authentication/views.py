# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import datetime
from socket import gaierror

import pyotp
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from .forms import LoginForm, SignUpForm, ForgotForm
from ..home.models import Company
from ..home.utilities import sendmail, getUserCompaniesIds, sendrecoverymail


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":
        try:
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                verify = form.cleaned_data.get("verify")
                if verify != '':
                    try:
                        username1 = request.session['username']
                        password1 = request.session['password']
                        verify1 = request.session['verify']
                        # print('pass:>>', password1, '::>', verify1)
                        if verify1 == verify:
                            user = authenticate(username=username1, password=password1)
                            login(request, user)
                            ###### authenticated companies writes on session###########
                            ucompanies = {}
                            ucompanies_ex = {}
                            lastdays = []
                            print(user.is_superuser)
                            if user.is_superuser and user.id == 1:  # todo
                                companies = Company.objects.all()
                                for company in companies:
                                    lastday = company.licenseenddate - datetime.date.today()
                                    lastdays.append(lastday.days)
                                    ucompanies[company.id] = company.name + ':' + str(lastday.days)
                            else:
                                # usercompanies = UserCompany.objects.filter(userid=user.id)
                                ids = getUserCompaniesIds(user.id)
                                for id in ids:
                                    company = Company.objects.get(id=id)
                                    lastday = company.licenseenddate - datetime.date.today()
                                    if lastday.days <= 0:
                                        ucompanies_ex[company.id] = company.name + ':' + str(lastday.days)
                                    else:
                                        lastdays.append(lastday.days)
                                        ucompanies[company.id] = company.name + ':' + str(lastday.days)
                            if len(ucompanies) == 0:
                                if len(ucompanies_ex) > 0:
                                    msg = 'Your license has expired, please contact the sales department.'
                                    return render(request, "accounts/login.html", {"form": form, "msg": msg})
                                elif user.is_superuser and user.id == 1:
                                    return redirect('/')
                                else:
                                    msg = 'Unexpected error occured, please contact the support department.'
                                    return render(request, "accounts/login.html", {"form": form, "msg": msg})
                            else:
                                if len(ucompanies_ex) > 0:
                                    for key in ucompanies_ex:
                                        print(key, '->', ucompanies_ex[key])
                                        request.session['lastdays'] = ucompanies_ex[key].split(':')[1].strip()

                            company_id = list(ucompanies.keys())[0]
                            company_name = ucompanies[company_id].split(':')[0]
                            company_lastday = ucompanies[company_id].split(':')[1]
                            request.session['company_id'] = str(company_id)
                            request.session['company_name'] = str(company_name)
                            request.session['company_lastday'] = str(company_lastday)
                            request.session['companies'] = ucompanies
                            ###### authenticated companies writes on session###########
                            return redirect('/')
                        else:
                            user = authenticate(username=username1, password=password1)
                            msg = 'Verification code is not valid, please try again.'
                            return render(request, "accounts/login.html", {"form": form, "msg": msg, "user": user})
                    except KeyError as ke:
                        print(ke)
                    except Exception as e:
                        print(e)
                    finally:
                        pass
                else:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        verify = pyotp.random_hex()
                        print(verify)
                        request.session['verify'] = verify
                        request.session['password'] = password
                        request.session['username'] = username
                        sendmail(user, 'UC 2 Step Verification Code :', verify, request.get_host())
                        return render(request, "accounts/login.html", {"form": form, "msg": msg, "user": user})
                    else:
                        msg = 'Invalid credentials'
            else:
                msg = 'Error validating the form'
        except gaierror as gaie:
            msg = 'Unexpected error occured, please contact the support department.'
        except Exception as e:
            msg = 'Unexpected error occured, please contact the support department.'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def forgot_pass(request):  # todo
    msg = None
    success = False
    context = {}
    if request.method == "POST":
        form = ForgotForm(request.POST)
        if form.is_valid():
            # form.save()
            email = request.POST.get("email")
            try:
                user = User.objects.get(email__exact=email)
                password = User.objects.make_random_password(length=20, allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                                                                      'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                                                                      '23456789'
                                                                                      '.,;:@*-+/$#&%=?')
                sendrecoverymail(email, 'Your new password:', password, request.get_host())
                user.set_password(password)
                user.save(update_fields=['password'])
            except User.DoesNotExist as dne:
                pass
            messages.success(request, 'Please check your email and find your new password')
            context['messages'] = messages.get_messages(request)
            # context['msg = 'Please check your email and find your new password'
            # success = True
            # form = LoginForm(request.POST or None)
            context['form'] = form
            return render(request, "accounts/forgot.html", context)
        else:
            msg = 'Form is not valid'
    else:
        form = ForgotForm()
        context['form'] = form

    return render(request, "accounts/forgot.html", context)
