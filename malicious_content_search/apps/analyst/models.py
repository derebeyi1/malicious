import datetime

from django.db import models
from ckeditor.fields import RichTextField

from apps.home.models import Company


class ContentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    form_name = models.CharField(max_length=100)
    type = models.CharField(max_length=10)


class LicenseType(models.Model):
    name = models.CharField(max_length=50, unique=True)


class AlarmType(models.Model):
    title = models.CharField(max_length=100)
    explain = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    is_manuel = models.BooleanField(default=True)
    monitor = models.BooleanField(default=True)
    description = RichTextField()
    mitigation = RichTextField()
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    username = models.CharField(max_length=50, editable=False)
    ip = models.CharField(max_length=40, editable=False)
    contenttypes = models.ManyToManyField(ContentType, through='AlarmTypeContentType')
    licensetypes = models.ManyToManyField(LicenseType, through='AlarmTypeLicenseType')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title'], name='alarmtype_title_unique'),
            # models.UniqueConstraint(fields=['apikey'], name='company_apikey_unique')
        ]


class AlarmTypeContentType(models.Model):
    alarmtype = models.ForeignKey(AlarmType, on_delete=models.CASCADE)
    contenttype = models.ForeignKey(ContentType, on_delete=models.CASCADE)


class AlarmTypeLicenseType(models.Model):
    alarmtype = models.ForeignKey(AlarmType, on_delete=models.CASCADE)
    licensetype = models.ForeignKey(LicenseType, on_delete=models.CASCADE)


class Content(models.Model):
    phishing_url = models.CharField(max_length=200, default='')
    create_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    expire_date = models.DateTimeField(null=True, blank=True)
    registrar_name = models.CharField(max_length=200, default='')
    registrar_company = models.CharField(max_length=200, default='')
    registrant_name = models.CharField(max_length=200, default='')
    registrant_country = models.CharField(max_length=200, default='')
    leak_source = models.CharField(max_length=200, default='')
    screenshot = models.ImageField(blank=True, upload_to='images', default='path/to/my/default/image.jpg')
    port = models.CharField(max_length=200, default='')
    protocol = models.CharField(max_length=200, default='')
    cvss = models.CharField(max_length=200, default='')
    cve = models.CharField(max_length=200, default='')
    url = models.CharField(max_length=200, default='')
    subdomain = models.CharField(max_length=200, default='')
    ns = models.CharField(max_length=200, default='')
    soa = models.CharField(max_length=200, default='')
    txt = models.CharField(max_length=200, default='')
    mx_old_record = models.CharField(max_length=200, default='')
    mx_new_record = models.CharField(max_length=200, default='')
    ns_old_record = models.CharField(max_length=200, default='')
    ns_new_record = models.CharField(max_length=200, default='')
    soa_old_record = models.CharField(max_length=200, default='')
    soa_new_record = models.CharField(max_length=200, default='')
    txt_old_record = models.CharField(max_length=200, default='')
    fqdn = models.CharField(max_length=200, default='')
    ip = models.CharField(max_length=200, default='')
    reverse_dns = models.CharField(max_length=200, default='')
    is_private = models.CharField(max_length=200, default='')
    domain = models.CharField(max_length=200, default='')
    row_data_old = models.CharField(max_length=200, default='')
    row_data_new = models.CharField(max_length=200, default='')
    expiration_days = models.CharField(max_length=200, default='')
    status_code = models.CharField(max_length=200, default='')
    server_header = models.CharField(max_length=200, default='')
    title_old = models.CharField(max_length=200, default='')
    title_new = models.CharField(max_length=200, default='')
    server_header_old = models.CharField(max_length=200, default='')
    server_header_new = models.CharField(max_length=200, default='')
    cert_name = models.CharField(max_length=200, default='')
    grade = models.CharField(max_length=200, default='')
    level = models.CharField(max_length=200, default='')
    name = models.CharField(max_length=200, default='')
    version = models.CharField(max_length=200, default='')
    asset = models.CharField(max_length=200, default='')
    explanation = models.CharField(max_length=200, default='')
    references = models.CharField(max_length=200, default='')
    service = models.CharField(max_length=200, default='')
    summary = models.CharField(max_length=200, default='')
    product = models.CharField(max_length=200, default='')
    dmarc_old_record = models.CharField(max_length=200, default='')
    dmarc_new_record = models.CharField(max_length=200, default='')
    spf_old_record = models.CharField(max_length=200, default='')
    spf_new_record = models.CharField(max_length=200, default='')
    assets = models.CharField(max_length=200, default='')
    username_mail = models.CharField(max_length=200, default='')
    password = models.CharField(max_length=200, default='')
    github_repo_name = models.CharField(max_length=200, default='')
    txt_new_record = models.CharField(max_length=200, default='')


class Alarm(models.Model):
    is_manuel = models.BooleanField()
    alarm_type_id = models.IntegerField()
    title = models.CharField(max_length=200)
    # company_ids = models.CharField(max_length=200)
    severity = models.CharField(max_length=20)
    description = RichTextField()
    mitigation = RichTextField()
    source = models.TextField()
    # content_ids = models.CharField(max_length=200)
    analyst_state = models.IntegerField(editable=False)
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    username = models.CharField(max_length=50, editable=False)
    ip = models.CharField(max_length=40, editable=False)
    companies = models.ManyToManyField(Company, through='AlarmCompany')
    contents = models.ManyToManyField(Content, through='AlarmContent')


class AlarmCompany(models.Model):
    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    company_state = models.IntegerField()
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    username = models.CharField(max_length=50, editable=False)
    ip = models.CharField(max_length=40, editable=False)


class AlarmContent(models.Model):
    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
