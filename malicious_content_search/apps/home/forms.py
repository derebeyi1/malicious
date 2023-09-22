import datetime
import os
import tempfile
import uuid

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group

from apps.authentication.models import GroupMenu
from apps.home.models import Company, Menu
from apps.home.utilities import parentsTags, groupsTags, companiesTags

name = os.path.splitext(os.path.basename(__file__))[0]
temp = tempfile.gettempdir()
tempFolder = os.path.join(temp, name)
if not os.path.exists(tempFolder):
    os.mkdir(tempFolder)


class CompanyForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Company Name",
                "class": "form-control"
            }
        ))
    linkedinname = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "LinkedIn Name",
                "class": "form-control"
            }
        ))
    shodanname = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Shodan Name",
                "class": "form-control"
            }
        ))
    licensetype = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "License Type",
                "class": "form-control"
            }
        ))
    licensestartdate = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    licenseenddate = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    licensetype = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "License Type",
                "class": "form-control"
            }
        ))
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Country",
                "class": "form-control ui-autocomplete-input",
                "autocomplete": "off"
            }
        ))
    activityarea = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Activity Area",
                "class": "form-control"
            }
        ))
    securitygrade = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Security Grade",
                "class": "form-control"
            }
        ))
    companysize = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Company Size",
                "class": "form-control"
            }
        ))
    logo = forms.ImageField(help_text="Upload image: ", required=False)
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Company Email",
                "class": "form-control"
            }
        ))
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    apikey = forms.CharField(
        required=True,
        initial=uuid.uuid4,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Api Key",
                "class": "form-control"
            }
        ))
    class Meta:
        model = Company
        fields = ('name', 'linkedinname', 'shodanname', 'licensetype', 'licensestartdate', 'licenseenddate', 'country', 'activityarea', 'securitygrade', 'companysize', 'logo', 'email', 'apikey')


class MyUserChangeForm(UserChangeForm):
    is_superuser = forms.BooleanField(
        required=False,
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Company Email",
                "class": "form-control"
            }
        ))
    is_active = forms.BooleanField(
        initial=True,
        required=False,
    )
    group = forms.ChoiceField(
        choices=groupsTags(),
        initial=[4],
        widget=forms.Select
    )
    companies = forms.MultipleChoiceField(
        choices=companiesTags(),
        widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        # self.base_fields['group'].initial = [1]
        del self.fields['password']

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'group', 'companies')

    def __init__(self, *args, **kwargs):
        super(MyUserChangeForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            if name == 'group':
                self.fields[name].required = True
                self.fields[name].widget.attrs = {'class': 'form-control ui-autocomplete-input', 'autocomplete': 'off', 'placeholder': 'Severity'}


class MenuForm(forms.ModelForm):
    parentid = forms.ChoiceField(
        choices=parentsTags(),
        widget=forms.Select(attrs={
                "class": "form-control"
            })
    )
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Title, Example: Admin",
                "class": "form-control"
            }
        ))
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Address, Example: /home/companies/",
                "class": "form-control"
            }
        ))
    is_active = forms.BooleanField(
        initial=True,
        required=False
    )
    has_item = forms.BooleanField(
        initial=False,
        required=False
    )
    icon = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Icon Name, Example: ion-settings",
                "class": "form-control"
            }
        ))
    is_seen = forms.BooleanField(
        initial=True,
        required=False
    )

    class Meta:
        model = Menu
        fields = ('parentid', 'title', 'address', 'is_active', 'has_item', 'icon', 'is_seen')

    def __init__(self, *args, **kwargs):
        super(MenuForm, self).__init__(*args, **kwargs)
        self.fields['parentid'].choices = parentsTags()


# class FriendForm(forms.ModelForm):
#     ## change the widget of the date field.
#     dob = forms.DateField(
#         label='What is your birth date?',
#         # change the range of the years from 1980 to currentYear - 5
#         widget=forms.SelectDateWidget(years=range(1980, datetime.date.today().year - 5))
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(FriendForm, self).__init__(*args, **kwargs)
#         ## add a "form-control" class to each form input
#         ## for enabling bootstrap
#         for name in self.fields.keys():
#             self.fields[name].widget.attrs.update({
#                 'class': 'form-control',
#             })
#
#     class Meta:
#         model = Friend
#         fields = ("__all__")


class GroupMenuForm(forms.ModelForm):
    # ## change the widget of the date field.
    # userid = forms.IntegerField(
    #     initial=0,
    #     show_hidden_initial=0,
    #     widget=forms.HiddenInput,
    #     required=False,
    #
    # )
    group_id = forms.ChoiceField(
        choices=groupsTags(),
        # initial=[4],
        widget=forms.Select
    )
    # menus = forms.MultipleChoiceField(
    #     choices=getMenusForAuth(),
    #     widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super(GroupMenuForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            if name == 'group' or name == 'menu':
                self.fields[name].required = False
            else:
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                })

    class Meta:
        model = GroupMenu
        fields = ("__all__")