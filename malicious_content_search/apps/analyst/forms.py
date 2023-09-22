import datetime
import os
import tempfile
import uuid

from django import forms
from django_quill.forms import QuillFormField

from apps.analyst.models import AlarmType, ContentType, Alarm, Content
from apps.home.utilities import get_licensetypes, get_contenttypes, get_alarmtypes, \
    get_companies_for_alarm

name = os.path.splitext(os.path.basename(__file__))[0]
temp = tempfile.gettempdir()
tempFolder = os.path.join(temp, name)
if not os.path.exists(tempFolder):
    os.mkdir(tempFolder)


class AlarmTypeForm(forms.ModelForm):
    # license_type_ids = forms.TypedMultipleChoiceField(
    #     choices=get_licensetypes(),
    #     # coerce=int,
    #     label='License Types',
    #     widget=forms.CheckboxSelectMultiple(),
    # )
    # content_type_ids = forms.TypedMultipleChoiceField(
    #     choices=get_contenttypes(),
    #     # coerce=int,
    #     label='Content Types',
    #     widget=forms.CheckboxSelectMultiple(),
    # )
    description = QuillFormField()
    mitigation = QuillFormField()
    # sil = forms.DateField(
    #     widget=forms.widgets.DateTimeInput(attrs={'class': 'datetimepicker', 'format': '%Y-%m-%d %H:%M', 'type': 'datetime-local', 'class': 'form-control'})
    # )
    def __init__(self, *args, **kwargs):
        super(AlarmTypeForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            if name == 'severity':
                self.fields[name].required = True
                # self.fields[name].widget.attrs['class'] = 'form-control ui-autocomplete-input'
                self.fields[name].widget.attrs = {'class': 'form-control ui-autocomplete-input', 'autocomplete': 'off', 'placeholder': 'Severity'}
            # elif name == 'license_type_ids':
            #     pass
            elif name == 'is_manuel' or name == 'monitor':
                pass
            # elif name == 'sil':
            #     self.fields[name].widget.attrs = {'class': 'datetimepicker', 'format': '%Y-%m-%d %H:%M', 'type': 'datetime-local', 'class': 'form-control'}
            #     # self.fields[name].widget.attrs = {'type': 'datetime'}
            elif name == 'license_type_ids' \
                    or name == 'description' or name == 'mitigation':
                self.fields[name].required = True
                self.fields[name].widget.attrs.update({
                    'name': name,
                })
            elif name == 'content_type_ids':
                self.fields[name].required = True
                self.fields[name].choices = get_contenttypes()
                self.fields[name].widget.attrs.update({
                    'name': name,
                })
            elif name == 'explain':
                self.fields[name].required = True
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                    'label': 'Explanation',
                })
            elif name == 'title':
                self.fields[name].required = True
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                })
            elif name == 'description' or name == 'mitigation':
                pass
                # self.fields[name].required = True
                # self.fields[name].widget = forms.Textarea(attrs={'name': name, 'rows': 15, 'cols': 100})
            else:
                self.fields[name].required = False
                self.fields[name].widget.attrs.update({
                    'class': 'form-control',
                })
        # self.fields['severity'] = ChoiceField(choices=get_severities())

    class Meta:
        model = AlarmType
        fields = ("__all__")


class AlarmForm(forms.ModelForm):
    alarm_type_id = forms.ChoiceField(
        choices=get_alarmtypes(),
        initial=(0, 'Select an Alarm Type'),
        widget=forms.Select(attrs={'class': 'form-control ui-autocomplete-input',
                                   'autocomplete': 'off'}))
    is_manuel = forms.BooleanField(
        # choices=alarm_type_types(), #1=Manuel 2=Auto
        initial=[True],
        # widget=forms.Select
    )
    companies = forms.MultipleChoiceField(
        choices=get_companies_for_alarm(),
        # coerce=int,
        label='Companies',
        widget=forms.CheckboxSelectMultiple(),
    )
    content_ids = forms.HiddenInput()
    # companies = forms.ChoiceField(
    #     choices=get_companies_for_alarm(),
    #     initial='',
    #     widget=forms.Select(attrs={'class': 'form-control ui-autocomplete-input',
    #                                'autocomplete': 'off'}))
    # companies = forms.MultipleChoiceField(
    #     choices=companiesTags(),
    #     widget=forms.CheckboxSelectMultiple())
    # sil = forms.DateField(
    #     widget=forms.widgets.DateTimeInput(
    #         attrs={'class': 'datetimepicker', 'format': '%Y-%m-%d %H:%M', 'type': 'datetime-local',
    #                'class': 'form-control'})
    # )
    def __init__(self, *args, **kwargs):
        super(AlarmForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        try:
            for name in self.fields.keys():
                if name == 'severity':
                    self.fields[name].required = True
                    self.fields[name].widget.attrs = {'class': 'form-control ui-autocomplete-input', 'autocomplete': 'off',
                                                      'placeholder': 'Severity'}
                elif name == 'alarm_type_id':
                    self.fields[name].required = True
                    self.fields[name].choices = get_alarmtypes()
                elif name == 'companies':
                    self.fields[name].required = True
                    # self.fields[name].widget.attrs.update({
                    #     'name': name,
                    # })
                    self.fields[name].choices = get_companies_for_alarm()
                    # self.fields[name].widget.forms.Select(attrs={'class': 'form-control ui-autocomplete-input', 'autocomplete': 'off',
                    #                                   'placeholder': 'Select an alarm type'})
                elif name == 'is_manuel':
                    self.fields[name].required = True
                # elif name == 'sil':
                #     self.fields[name].widget.attrs = {'class': 'datetimepicker', 'type': 'date', 'format': '%Y-%m-%d %H:%M'}
                elif name == 'description' or name == 'mitigation':
                    pass
                    # self.fields[name].required = True
                    # self.fields[name].widget = forms.Textarea(attrs={'name': name, 'rows': 15, 'cols': 100})
                else:
                    self.fields[name].required = False
                    self.fields[name].widget.attrs.update({
                        'class': 'form-control',
                    })
            # self.fields['severity'] = ChoiceField(choices=get_severities())
        except Exception as e:
            print(e)
    class Meta:
        model = Alarm
        fields = ("__all__")


class ContentTypeForm(forms.ModelForm):
    # license_type_ids = forms.TypedMultipleChoiceField(
    #     choices=get_licensetypes(),
    #     # coerce=int,
    #     label='License Types',
    #     widget=forms.CheckboxSelectMultiple(),
    # )
    # content_type_ids = forms.TypedMultipleChoiceField(
    #     choices=get_contenttypes(),
    #     # coerce=int,
    #     label='Content Types',
    #     widget=forms.CheckboxSelectMultiple(),
    # )

    def __init__(self, *args, **kwargs):
        super(ContentTypeForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            # if name == 'severity':
            #     # self.fields[name].widget.attrs['class'] = 'form-control ui-autocomplete-input'
            #     self.fields[name].widget.attrs = {'class': 'form-control ui-autocomplete-input', 'autocomplete': 'off', 'placeholder': 'Severity'}
            # # elif name == 'license_type_ids':
            # #     pass
            # elif name == 'is_manuel' or name == 'monitor' or name == 'content_type_ids' or name == 'license_type_ids':
            #     pass
            # elif name == 'explain':
            #     self.fields[name].widget.attrs.update({
            #         'class': 'form-control',
            #         'label': 'Explanation',
            #     })
            # else:
            self.fields[name].required = True
            # self.fields[name].widget.attrs['required'] = 'required'
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })
        # self.fields['severity'] = ChoiceField(choices=get_severities())

    class Meta:
        model = ContentType
        fields = ("__all__")


class ContentForm(forms.ModelForm):
    # create_date = forms.DateTimeField(
    #     input_formats=['%Y-%m-%dT%H:%M'],
    #     widget=forms.DateTimeInput(
    #         attrs={
    #             'type': 'datetime',
    #             'class': 'form-control'},
    #         format='%Y-%m-%dT%H:%M')
    # )
    # widgets = {
    #     'request_date': DateTimeInput(attrs={'type': 'datetime-local'}),
    # }


    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            self.fields[name].required = False

    class Meta:
        model = Content
        fields = ("__all__")
