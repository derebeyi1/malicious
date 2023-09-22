import datetime
import re

from asyncpg.transaction import Transaction
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.db.models import Q, Count

from apps.analyst.models import ContentType, AlarmType
from apps.authentication.models import GroupMenu, UserCompany, MyUser
from apps.home.models import Menu, Company
from core.settings import EMAIL_HOST_USER
from django import template

register = template.Library()
pass_str = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789.,;:@*-+/$#&%=?'


def getUserMenuObjects(id):   #kullanıcının yetkili olduğu menuleri döndürür.
    try:
        user = User.objects.get(id=id)
        group = user.groups.all().first()
        try:
            usermenus = group.mygroup.menus
        except Exception as e:
            usermenus = None
            pass
        # gids = list(groups)
        # for group in groups:
        #     gids.append(group.id)
        if user.is_superuser or user.id == 1:
            # usermenus = GroupMenu.objects.filter(group_id=group.id)
            if usermenus is None or usermenus.count() == 0:
                menus = Menu.objects.exclude(id=1).order_by('id')
                return menus
            elif len(usermenus) == 0:
                menus = Menu.objects.exclude(id=1).order_by('id')
                return menus
            else:
                return usermenus
        else:
            # user = User.objects.get(id=id)
            # groups = user.groups.all()
            # l = list()
            # for g in groups:
            #     l.append(g.id)
            # usermenus = GroupMenu.objects.filter(Q(userid=id) | Q(groupid__in=l))
            # ids = []
            # for usermenu in usermenus:
            #     mids = usermenu.usermenu.split(',')
            #     for mid in mids:
            #         ids.append(int(mid))
            # ids1 = list(sorted(set(ids)))
            # return Menu.objects.filter(id__in=(ids1)).order_by('id')
            return usermenus
        # else:
        #     return Menu.objects.exclude(id=1).order_by('id')
    except Exception as e:
        print(e)


def getUserMenuObjectsIds(id):   #kullanıcının yetkili olduğu menuleri döndürür.
    menus = getUserMenuObjects(id)
    ids = menus.all().values_list('id', flat=True)
    return list(sorted(set(map(int, ids))))


def getGroupMenuObjectsIds(id):   #kullanıcının yetkili olduğu menuleri döndürür.
    ids1 = []
    try:
        umenus = GroupMenu.objects.get(groupid=id)
        ids = umenus.usermenu.split(',')
        ids1 = list(sorted(set(map(int, ids))))
    except Exception as e:
        pass
    return ids1


def getGroupMenuObjects(id):   #kullanıcının yetkili olduğu menuleri döndürür.
    if id != 1:
        ids = getGroupMenuObjectsIds(id)
        return Menu.objects.filter(id__in=ids)
    else:
        return Menu.objects.exclude(id=1).order_by('id')


def getUserMenu1(id):
    menus = getUserMenuObjects(id)
    start = """
    <nav class="navbar navbar-dark navbar-theme-primary px-4 col-12 d-lg-none">
    <a class="navbar-brand me-lg-5" href="/">
        <img class="navbar-brand-dark" src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC logo" /> <img class="navbar-brand-light" src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC logo" />
    </a>
    <div class="d-flex align-items-center">
        <button class="navbar-toggler d-lg-none collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
    </div>
    </nav>
    <nav id="sidebarMenu" class="sidebar d-lg-block bg-gray-800 text-white collapse" data-simplebar>
    <div class="sidebar-inner px-4 pt-3">
        <div class="user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4">
            <div class="d-flex align-items-center">
                <div class="avatar-lg me-4">
                    <img src="/apps/static/assets/img/team/profile-picture.jpg" class="card-img-top rounded-circle border-white"
                         alt="Bonnie Green">
                </div>
                <div class="d-block">
                    <h2 class="h5 mb-3">Hi, Jane</h2>
                    <a href="/page-sign-in.html" class="btn btn-secondary btn-sm d-inline-flex align-items-center">
                        <svg class="icon icon-xxs me-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                        Sign Out
                    </a>
                </div>
            </div>
            <div class="collapse-close d-md-none">
                <a href="#sidebarMenu" data-bs-toggle="collapse"
                   data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="true"
                   aria-label="Toggle navigation">
                    <svg class="icon icon-xs" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                </a>
            </div>
        </div>
        <ul class="sidebar-menu nav flex-column pt-3 pt-md-0">
            <li class="nav-item">
                <a href="/home/dashboard.html" class="nav-link d-flex align-items-center">
                  <span class="sidebar-icon">
                    <img src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC Logo" class="brand-image img-circle elevation-3"
                         style="opacity: .8">
                  </span>
                    <span class="mt-1 ms-1 sidebar-text">UC</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="/home/dashboard.html" class="nav-link">
                  <span class="sidebar-icon">
                    <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path><path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path></svg>
                  </span>
                    <span class="sidebar-text">Dashboard</span>
                </a>
            </li>
    """
    ul = '<li class="nav-item">' \
         '<span class="nav-link collapsed d-flex justify-content-between align-items-center"' \
         'data-bs-toggle="collapse" data-bs-target="#submenu-%s">' \
         '<span>' \
         '<span class="sidebar-icon">' \
         '<i class="ion %s"></i>' \
         '</span> ' \
         '<span class="sidebar-text">%s</span>' \
         '</span>' \
         '<span class="link-arrow">' \
         '<svg class="icon icon-sm" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>' \
         '</span>' \
         '</span>' \
         '<div class="multi-level collapse" role="list"' \
         'id="submenu-%s" aria-expanded="false">' \
         '<ul class="treeview-menu flex-column nav">'

    li = '<li class="nav-item">' \
         '<a class="nav-link anchor" href="%s">' \
         '<span class="sidebar-icon">' \
         '<i class="ion %s"></i>' \
         '</span> ' \
         '<span class="sidebar-text">%s</span>' \
         '</a>' \
         '</li>'
    end = """
        <li class="nav-item">
                <span
                        class="nav-link collapsed d-flex justify-content-between align-items-center"
                        data-bs-toggle="collapse" data-bs-target="#submenu-components">
                  <span>
                    <span class="sidebar-icon">
                      <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z"></path><path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
                    </span>
                    <span class="sidebar-text">Components</span>
                  </span>
                  <span class="link-arrow">
                    <svg class="icon icon-sm" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
                  </span>
                </span>
                <div class="multi-level collapse" role="list"
                     id="submenu-components" aria-expanded="false">
                    <ul class="flex-column nav">
                        <li class="nav-item">
                            <a class="nav-link" href="/home/components-buttons.html">
                                <span class="sidebar-text">Buttons</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/home/components-notifications.html">
                                <span class="sidebar-text">Notifications</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/home/components-forms.html">
                                <span class="sidebar-text">Forms</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/home/components-modals.html">
                                <span class="sidebar-text">Modals</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/home/components-typography.html">
                                <span class="sidebar-text">Typography</span>
                            </a>
                        </li>
                    </ul>
                </div>
            </li>
            <li role="separator" class="dropdown-divider mt-4 mb-3 border-gray-700"></li>
            <li class="nav-item">
                <a href="https://appseed.us/admin-dashboards/django-dashboard-volt" target="_blank"
                   class="nav-link d-flex align-items-center">
                  <span class="sidebar-icon">
                    <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path></svg>
                  </span>
                    <span class="sidebar-text">Product Page</span>
                </a>
            </li>
        </ul>
    </div>
    </nav>
    """
    html = start
    i = 0
    pid = 0
    for menu in menus:
        # print(menu.title, menu.address)
        if menu.has_item and menu.is_active and menu.is_seen:
            pre = menu.address.split('/')[1]
            html += ul % (pre, menu.icon, menu.title, pre)
            smenus = menus.filter(parentid=menu.id).order_by('id')
            for smenu in smenus:
                if smenu.is_active and smenu.is_seen:
                    html += li % (smenu.address, smenu.icon,smenu.title)
            html += '</ul></div></li>'
    if i > 0:
        html += '</ul></div></li>'
    # print(html)
    # html += end
    return html


# def getUserMenu1(id):
#     return getUserMenu(id)


def isUserAuthMenu(url, user):  #kullanıcı bu url e yetkilimi?.
    try:
        if user.is_superuser or user.id == 1:
            return True
        else:
            menus = getUserMenuObjects(user.id)
            if bool(re.search(r'\d', url)):
                url = url.rsplit('/', 2)[0]
            result = menus.filter(address__icontains=url)
            if result is not None and len(result) > 0:
                return True
    except Exception as e:
        print(e)
    return False


def getUserCompaniesUsersIds(id):  #kullanıcının yetkili olduğu firmaların kullanıcılarının id lerini döndürür.
    ids = list()
    users = getUserCompaniesUsers(id)
    for uc in users:
        ids.append(uc.id)
    return list(sorted(set(ids)))


def getUserCompaniesUsers(userid):  #kullanıcının yetkili olduğu firmaların kullanıcılarını döndürür.
    uids = getUserCompaniesIds(userid)
    ids = []
    ucompanies = UserCompany.objects.filter(companyid__in=uids)
    for uc in ucompanies:
        ids.append(uc.userid)
    users = User.objects.filter(id__in=ids)
    return users


def getUserCompaniesIds(userid):  #kullanıcının yetkili olduğu firmaların id lerini döndürür.
    ids = []
    ucompanies = getUserCompanies(userid)
    for ucompany in ucompanies:
        ids.append(ucompany.companyid)
    return list(sorted(set(ids)))


def getUserCompanies(userid): #kullanıcının yetkili olduğu firmaları döndürür.
    ucompanies = UserCompany.objects.filter(userid=userid)
    return ucompanies


def getCompaniesIds(userid):
    ids = getCompanies(userid).values_list('id', flat=True)
    return ids


def getCompanies(userid):
    ids = UserCompany.objects.filter(user_id=userid).values_list('company_id', flat=True)
    companies = Company.objects.filter(id__in=ids)
    return companies


def getUsers(user): #kullanıcının yetkili olduğu kullanıcıları döndürür.
    ugroups = user.groups.all()
    groups = list()
    for g in ugroups:
        groups.append(g.id)
    #     todo
    if 1 in groups or user.is_superuser or user.id == 1:
        ucompanies = UserCompany.objects.filter(userid=user.id)
        # todo
        cl = list()
        for ucompany in ucompanies:
            cl.append(ucompany.companyid)
        print(cl)
        ucompanies = UserCompany.objects.filter(companyid__in=cl)
        userl = list()
        for uc in ucompanies:
            userl.append(uc.userid)
    return User.objects.filter(Q(id=user.id) | Q(id__in=userl))


def getUsersIds(user): #kullanıcının yetkili olduğu kullanıcıların id lerini döndürür.
    ids = []
    users = getUsers(user)
    for user in users:
        ids.append(user.id)
    return list(sorted(set(ids)))


def getCompanyUsers(companyid): #kullanıcının yetkili olduğu firmaları döndürür.
    ids = UserCompany.objects.filter(company_id=companyid).values_list('user_id', flat=True)
    users = User.objects.filter(id__in=ids)
    return users


def sendmail(user, subject, verify, link):
    try:
        name = user.first_name.strip() + ' ' + user.last_name
        from_email = 'dene9876543210@gmail.com'
        # subject = 'UC 2 Step Verification Code :'
        message = subject + '\n\n' + verify + '\n\n' + link

        send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        raise(e)


def sendrecoverymail(email, subject, password,link):
    try:
        # name = user.first_name.strip() + ' ' + user.last_name
        from_email = 'dene9876543210@gmail.com'
        # subject = 'UC 2 Step Verification Code :'
        message = subject + '\n\n' + password + '\n\n' + link

        send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        raise(e)


def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        # domain=settings.SESSION_COOKIE_DOMAIN,
        # secure=settings.SESSION_COOKIE_SECURE or None,
    )
    return response


def companysizeTags():
    companysizeTags = ['1-20', '21-100', '101-500', '501-1000', 'more than 1001']
    return companysizeTags


def activityareaTags():
    activityareaTags = ['E-Trade', 'Digital Marketing', 'Cyber Security', 'Tourism', 'Catering', 'Insurance', 'Education']
    return activityareaTags


def securitygradeTags():
    securitygradeTags = ['Basic', 'Medium', 'High', 'Expert', 'Master']
    return securitygradeTags


def licensetypeTags():
    licensetypeTags = ['Trial License', 'Project-based License',
                              'Perpetual License', 'Floating License',
                              'Subscription License', 'Metered License',
                              'Use-Time License']
    return licensetypeTags


def get_severities():
    severities = ['Low', 'Medium', 'High', 'Critical']
    return severities


def get_alarmtypes():
    # alarmtypes = [(1, 'title')]
    alarmtypes = AlarmType.objects.order_by('-id').values_list('id', 'title')
    at_list = list(alarmtypes)
    at_list.append((0, 'Select an Alarm Type'))
    return at_list


def get_content_type_types():
    #todo
    types = ['String', 'Date', 'File']
    aa = ContentType.objects.values('type').annotate(total=Count('type')).order_by('-total')
    return types


def get_licensetypes():
    # [(4, 'User'), (3, 'Analyst'), (1, 'Admin')]
    licensetypes = [(1, 'Basic'), (2, 'Pro'), (3, 'Ent')]
    return licensetypes


def get_contenttypes():
    contenttypes = ContentType.objects.order_by('-id').values_list('id', 'form_name')
    return contenttypes


def getGroupIdForUserRole():
    id = Group.objects.filter(name='User').order_by('-id').values_list('id', flat=True)
    id1 = id[0]
    return id[0]


def getUserMenuStrIdsForRole(id):
    # usermenustrids = []
    if id != 1:
        menu_ids = GroupMenu.objects.filter(group_id=id).values_list('menu_id', flat=True)
        # usermenustr = GroupMenu.objects.filter(groupid=id).values_list('usermenu', flat=True)
        # if usermenustr and usermenustr[0] != '':
        #     usermenustrids = usermenustr[0].split(',')
        # else:
        #     usermenustrids = []
    else:
        menu_ids = Menu.objects.exclude(id=1).order_by('id').values_list('id', flat='True')
    # if menu_ids:
    return menu_ids
        # return list(sorted(set(map(int, usermenustrids))))
    # else:
    #     return usermenustrids


def getMenuObjectsByParentId(parentid):
    return Menu.objects.filter(parentid=parentid).order_by('id')


def groupsTags():
    try:
        # groups = [(1,'Admin')]
        groups = Group.objects.order_by('-id').values_list('id', 'name')
    except Exception as e:
        pass
    return list(groups)


def parentsTags():
    try:
        # parents = [(1, 'menu title')]
        parents = Menu.objects.filter(parentid__in=(0, 1)).order_by('id').values_list('id', 'title')
    except Exception as e:
        pass
    return list(parents)


def companiesTags():
    try:
        # companies = [(1, 'c name')]
        companies = Company.objects.order_by('name').values_list('id', 'name')
    except Exception as e:
        pass
    return list(companies)


def get_companies_for_alarm():
    try:
        # companies = [(1, 'name')]
        companies = Company.objects.order_by('name').values_list('id', 'name')
    except Exception as e:
        pass
    list_companies = list(companies)
    # list_companies.insert(0, (0, 'All Companies'))
    # list_companies.insert(0, ('', 'Select a company/companies'))
    return list_companies


def alarm_type_types():
    types = [(1, 'Manuel'), (0, 'Auto')]
    return types


def get_countries():
    COUNTRIES = [('', ''), ('TURKEY', 'TURKEY'), ('CANADA', 'CANADA'), ('GERMANY', 'GERMANY')]

    COUNTRIES = [
        ('', ''),
        ('AD', 'Andorra'),
        ('AE', 'United Arab Emirates'),
        ('AF', 'Afghanistan'),
        ('AG', 'Antigua & Barbuda'),
        ('AI', 'Anguilla'),
        ('AL', 'Albania'),
        ('AM', 'Armenia'),
        ('AN', 'Netherlands Antilles'),
        ('AO', 'Angola'),
        ('AQ', 'Antarctica'),
        ('AR', 'Argentina'),
        ('AS', 'American Samoa'),
        ('AT', 'Austria'),
        ('AU', 'Australia'),
        ('AW', 'Aruba'),
        ('AZ', 'Azerbaijan'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BB', 'Barbados'),
        ('BD', 'Bangladesh'),
        ('BE', 'Belgium'),
        ('BF', 'Burkina Faso'),
        ('BG', 'Bulgaria'),
        ('BH', 'Bahrain'),
        ('BI', 'Burundi'),
        ('BJ', 'Benin'),
        ('BM', 'Bermuda'),
        ('BN', 'Brunei Darussalam'),
        ('BO', 'Bolivia'),
        ('BR', 'Brazil'),
        ('BS', 'Bahama'),
        ('BT', 'Bhutan'),
        ('BV', 'Bouvet Island'),
        ('BW', 'Botswana'),
        ('BY', 'Belarus'),
        ('BZ', 'Belize'),
        ('CA', 'Canada'),
        ('CC', 'Cocos (Keeling) Islands'),
        ('CF', 'Central African Republic'),
        ('CG', 'Congo'),
        ('CH', 'Switzerland'),
        ('CI', 'Ivory Coast'),
        ('CK', 'Cook Iislands'),
        ('CL', 'Chile'),
        ('CM', 'Cameroon'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('CR', 'Costa Rica'),
        ('CU', 'Cuba'),
        ('CV', 'Cape Verde'),
        ('CX', 'Christmas Island'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DE', 'Germany'),
        ('DJ', 'Djibouti'),
        ('DK', 'Denmark'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('DZ', 'Algeria'),
        ('EC', 'Ecuador'),
        ('EE', 'Estonia'),
        ('EG', 'Egypt'),
        ('EH', 'Western Sahara'),
        ('ER', 'Eritrea'),
        ('ES', 'Spain'),
        ('ET', 'Ethiopia'),
        ('FI', 'Finland'),
        ('FJ', 'Fiji'),
        ('FK', 'Falkland Islands (Malvinas)'),
        ('FM', 'Micronesia'),
        ('FO', 'Faroe Islands'),
        ('FR', 'France'),
        ('FX', 'France, Metropolitan'),
        ('GA', 'Gabon'),
        ('GB', 'United Kingdom (Great Britain)'),
        ('GD', 'Grenada'),
        ('GE', 'Georgia'),
        ('GF', 'French Guiana'),
        ('GH', 'Ghana'),
        ('GI', 'Gibraltar'),
        ('GL', 'Greenland'),
        ('GM', 'Gambia'),
        ('GN', 'Guinea'),
        ('GP', 'Guadeloupe'),
        ('GQ', 'Equatorial Guinea'),
        ('GR', 'Greece'),
        ('GS', 'South Georgia/South Sandwich Islands'),
        ('GT', 'Guatemala'),
        ('GU', 'Guam'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HK', 'Hong Kong'),
        ('HM', 'Heard & McDonald Islands'),
        ('HN', 'Honduras'),
        ('HR', 'Croatia'),
        ('HT', 'Haiti'),
        ('HU', 'Hungary'),
        ('ID', 'Indonesia'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IN', 'India'),
        ('IO', 'British Indian Ocean Territory'),
        ('IQ', 'Iraq'),
        ('IR', 'Islamic Republic of Iran'),
        ('IS', 'Iceland'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JO', 'Jordan'),
        ('JP', 'Japan'),
        ('KE', 'Kenya'),
        ('KG', 'Kyrgyzstan'),
        ('KH', 'Cambodia'),
        ('KI', 'Kiribati'),
        ('KM', 'Comoros'),
        ('KN', 'St. Kitts and Nevis'),
        ('KP', 'Korea, Democratic People\'s Rep. of'),
        ('KR', 'Korea, Republic of'),
        ('KW', 'Kuwait'),
        ('KY', 'Cayman Islands'),
        ('KZ', 'Kazakhstan'),
        ('LA', 'Lao People\'s Democratic Republic'),
        ('LB', 'Lebanon'),
        ('LC', 'Saint Lucia'),
        ('LI', 'Liechtenstein'),
        ('LK', 'Sri Lanka'),
        ('LR', 'Liberia'),
        ('LS', 'Lesotho'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('LV', 'Latvia'),
        ('LY', 'Libyan Arab Jamahiriya'),
        ('MA', 'Morocco'),
        ('MC', 'Monaco'),
        ('MD', 'Moldova, Republic of'),
        ('MG', 'Madagascar'),
        ('MH', 'Marshall Islands'),
        ('ML', 'Mali'),
        ('MN', 'Mongolia'),
        ('MM', 'Myanmar'),
        ('MO', 'Macau'),
        ('MP', 'Northern Mariana Islands'),
        ('MQ', 'Martinique'),
        ('MR', 'Mauritania'),
        ('MS', 'Monserrat'),
        ('MT', 'Malta'),
        ('MU', 'Mauritius'),
        ('MV', 'Maldives'),
        ('MW', 'Malawi'),
        ('MX', 'Mexico'),
        ('MY', 'Malaysia'),
        ('MZ', 'Mozambique'),
        ('NA', 'Namibia'),
        ('NC', 'New Caledonia'),
        ('NE', 'Niger'),
        ('NF', 'Norfolk Island'),
        ('NG', 'Nigeria'),
        ('NI', 'Nicaragua'),
        ('NL', 'Netherlands'),
        ('NO', 'Norway'),
        ('NP', 'Nepal'),
        ('NR', 'Nauru'),
        ('NU', 'Niue'),
        ('NZ', 'New Zealand'),
        ('OM', 'Oman'),
        ('PA', 'Panama'),
        ('PE', 'Peru'),
        ('PF', 'French Polynesia'),
        ('PG', 'Papua New Guinea'),
        ('PH', 'Philippines'),
        ('PK', 'Pakistan'),
        ('PL', 'Poland'),
        ('PM', 'St. Pierre & Miquelon'),
        ('PN', 'Pitcairn'),
        ('PR', 'Puerto Rico'),
        ('PT', 'Portugal'),
        ('PW', 'Palau'),
        ('PY', 'Paraguay'),
        ('QA', 'Qatar'),
        ('RE', 'Reunion'),
        ('RO', 'Romania'),
        ('RU', 'Russian Federation'),
        ('RW', 'Rwanda'),
        ('SA', 'Saudi Arabia'),
        ('SB', 'Solomon Islands'),
        ('SC', 'Seychelles'),
        ('SD', 'Sudan'),
        ('SE', 'Sweden'),
        ('SG', 'Singapore'),
        ('SH', 'St. Helena'),
        ('SI', 'Slovenia'),
        ('SJ', 'Svalbard & Jan Mayen Islands'),
        ('SK', 'Slovakia'),
        ('SL', 'Sierra Leone'),
        ('SM', 'San Marino'),
        ('SN', 'Senegal'),
        ('SO', 'Somalia'),
        ('SR', 'Suriname'),
        ('ST', 'Sao Tome & Principe'),
        ('SV', 'El Salvador'),
        ('SY', 'Syrian Arab Republic'),
        ('SZ', 'Swaziland'),
        ('TC', 'Turks & Caicos Islands'),
        ('TD', 'Chad'),
        ('TF', 'French Southern Territories'),
        ('TG', 'Togo'),
        ('TH', 'Thailand'),
        ('TJ', 'Tajikistan'),
        ('TK', 'Tokelau'),
        ('TM', 'Turkmenistan'),
        ('TN', 'Tunisia'),
        ('TO', 'Tonga'),
        ('TP', 'East Timor'),
        ('TR', 'Turkey'),
        ('TT', 'Trinidad & Tobago'),
        ('TV', 'Tuvalu'),
        ('TW', 'Taiwan, Province of China'),
        ('TZ', 'Tanzania, United Republic of'),
        ('UA', 'Ukraine'),
        ('UG', 'Uganda'),
        ('UM', 'United States Minor Outlying Islands'),
        ('US', 'United States of America'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VA', 'Vatican City State (Holy See)'),
        ('VC', 'St. Vincent & the Grenadines'),
        ('VE', 'Venezuela'),
        ('VG', 'British Virgin Islands'),
        ('VI', 'United States Virgin Islands'),
        ('VN', 'Viet Nam'),
        ('VU', 'Vanuatu'),
        ('WF', 'Wallis & Futuna Islands'),
        ('WS', 'Samoa'),
        ('YE', 'Yemen'),
        ('YT', 'Mayotte'),
        ('YU', 'Yugoslavia'),
        ('ZA', 'South Africa'),
        ('ZM', 'Zambia'),
        ('ZR', 'Zaire'),
        ('ZW', 'Zimbabwe'),
        ('ZZ', 'Unknown or unspecified country'),
    ]
    return COUNTRIES
