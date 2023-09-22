import re

from django import template
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from apps.home import utilities
from apps.home.models import Menu
from apps.home.utilities import getUserMenuObjects, getUserMenu1, getGroupMenuObjects, getGroupMenuObjectsIds, \
    get_licensetypes

register = template.Library()


# @register.simple_tag(takes_context=True)
@register.simple_tag
def getUserMenu(id):
    html = getUserMenu1(id)
    return mark_safe(html)
    # menus = getUserMenuObjects(id)
    # start = """
    # <nav class="navbar navbar-dark navbar-theme-primary px-4 col-12 d-lg-none">
    # <a class="navbar-brand me-lg-5" href="/">
    #     <img class="navbar-brand-dark" src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC logo" /> <img class="navbar-brand-light" src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC logo" />
    # </a>
    # <div class="d-flex align-items-center">
    #     <button class="navbar-toggler d-lg-none collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
    #         <span class="navbar-toggler-icon"></span>
    #     </button>
    # </div>
    # </nav>
    # <nav id="sidebarMenu" class="sidebar d-lg-block bg-gray-800 text-white collapse" data-simplebar>
    # <div class="sidebar-inner px-4 pt-3">
    #     <div class="user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4">
    #         <div class="d-flex align-items-center">
    #             <div class="avatar-lg me-4">
    #                 <img src="/apps/static/assets/img/team/profile-picture.jpg" class="card-img-top rounded-circle border-white"
    #                      alt="Bonnie Green">
    #             </div>
    #             <div class="d-block">
    #                 <h2 class="h5 mb-3">Hi, Jane</h2>
    #                 <a href="/page-sign-in.html" class="btn btn-secondary btn-sm d-inline-flex align-items-center">
    #                     <svg class="icon icon-xxs me-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
    #                     Sign Out
    #                 </a>
    #             </div>
    #         </div>
    #         <div class="collapse-close d-md-none">
    #             <a href="#sidebarMenu" data-bs-toggle="collapse"
    #                data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="true"
    #                aria-label="Toggle navigation">
    #                 <svg class="icon icon-xs" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
    #             </a>
    #         </div>
    #     </div>
    #     <ul class="sidebar-menu nav flex-column pt-3 pt-md-0">
    #         <li class="nav-item">
    #             <a href="/home/dashboard.html" class="nav-link d-flex align-items-center">
    #               <span class="sidebar-icon">
    #                 <img src="/apps/static/assets/img/cropped-UC_favicon-1.png" alt="UC Logo" class="brand-image img-circle elevation-3"
    #                      style="opacity: .8">
    #               </span>
    #                 <span class="mt-1 ms-1 sidebar-text">UC</span>
    #             </a>
    #         </li>
    #         <li class="nav-item">
    #             <a href="/home/dashboard.html" class="nav-link">
    #               <span class="sidebar-icon">
    #                 <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path><path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path></svg>
    #               </span>
    #                 <span class="sidebar-text">Dashboard</span>
    #             </a>
    #         </li>
    # """
    # ul = '<li class="nav-item">' \
    #      '<span class="nav-link  collapsed  d-flex justify-content-between align-items-center"' \
    #      'data-bs-toggle="collapse" data-bs-target="#submenu-%s">' \
    #      '<span>' \
    #      '<span class="sidebar-icon">' \
    #      '<i class="ion %s"></i>' \
    #      '</span> ' \
    #      '<span class="sidebar-text">%s</span>' \
    #      '</span>' \
    #      '<span class="link-arrow">' \
    #      '<svg class="icon icon-sm" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>' \
    #      '</span>' \
    #      '</span>' \
    #      '<div class="multi-level collapse" role="list"' \
    #      'id="submenu-%s" aria-expanded="false">' \
    #      '<ul class="treeview-menu flex-column nav">'
    #
    # li = '<li class="nav-item">' \
    #      '<a class="nav-link" href="%s">' \
    #      '<span class="sidebar-icon">' \
    #      '<i class="ion %s"></i>' \
    #      '</span> ' \
    #      '<span class="sidebar-text">%s</span>' \
    #      '</a>' \
    #      '</li>'
    # end = """
    #     <li class="nav-item">
    #             <span
    #                     class="nav-link  collapsed  d-flex justify-content-between align-items-center"
    #                     data-bs-toggle="collapse" data-bs-target="#submenu-components">
    #               <span>
    #                 <span class="sidebar-icon">
    #                   <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z"></path><path fill-rule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
    #                 </span>
    #                 <span class="sidebar-text">Components</span>
    #               </span>
    #               <span class="link-arrow">
    #                 <svg class="icon icon-sm" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
    #               </span>
    #             </span>
    #             <div class="multi-level collapse" role="list"
    #                  id="submenu-components" aria-expanded="false">
    #                 <ul class="flex-column nav">
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="/home/components-buttons.html">
    #                             <span class="sidebar-text">Buttons</span>
    #                         </a>
    #                     </li>
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="/home/components-notifications.html">
    #                             <span class="sidebar-text">Notifications</span>
    #                         </a>
    #                     </li>
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="/home/components-forms.html">
    #                             <span class="sidebar-text">Forms</span>
    #                         </a>
    #                     </li>
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="/home/components-modals.html">
    #                             <span class="sidebar-text">Modals</span>
    #                         </a>
    #                     </li>
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="/home/components-typography.html">
    #                             <span class="sidebar-text">Typography</span>
    #                         </a>
    #                     </li>
    #                 </ul>
    #             </div>
    #         </li>
    #         <li role="separator" class="dropdown-divider mt-4 mb-3 border-gray-700"></li>
    #         <li class="nav-item">
    #             <a href="https://appseed.us/admin-dashboards/django-dashboard-volt" target="_blank"
    #                class="nav-link d-flex align-items-center">
    #               <span class="sidebar-icon">
    #                 <svg class="icon icon-xs me-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path></svg>
    #               </span>
    #                 <span class="sidebar-text">Product Page</span>
    #             </a>
    #         </li>
    #     </ul>
    # </div>
    # </nav>
    # """
    # html = start
    # i = 0
    # pid = 0
    # for menu in menus:
    #     # print(menu.title, menu.address)
    #     if menu.has_item and menu.is_active and menu.is_seen:
    #         pre = menu.address.split('/')[1]
    #         html += ul % (pre, menu.icon, menu.title, pre)
    #         smenus = menus.filter(parentid=menu.id).order_by('id')
    #         for smenu in smenus:
    #             if smenu.is_active and smenu.is_seen:
    #                 html += li % (smenu.address, smenu.icon,smenu.title)
    #         html += '</ul></div></li>'
    # if i > 0:
    #     html += '</ul></div></li>'
    # # print(html)
    # html += end


@register.simple_tag
def getUserMenuForAdmin(id):
    menus = getUserMenuObjects(id)
    th = '<thead style="background-color: #6C7AE0">' \
         '<tr>' \
         '<th><span class="p-column-title">CRUD</span></th>' \
         '<th><span class="p-column-title">Title</span></th>' \
         '<th><span class="p-column-title">Address</span></th>' \
         '<th><span class="p-column-title">Icon</span></th>' \
         '<th><span class="p-column-title">Show in Menu?</span></th>' \
         '<th><span class="p-column-title">Is Active?</span></th>' \
         '<th><span class="p-column-title">Has Child?</span></th>' \
         '' \
         '</tr>' \
         '</thead>'
    table = '<div style="overflow-x:auto;"><table id="example" class="table table-valign-middle">'+th+'%s</table></div>'

    tr1 = '<tr data-node-id="%s" style="background-color: #ECEAF4">%s</tr>'
    tr2 = '<tr data-node-id="%s" data-node-pid="%s" style="background-color: #FFFFFF">%s</tr>'
    td1 = '<td><span class="simple-tree-table-handler simple-tree-table-icon" style="margin-left: 0px;"></span><a href="#">%s</a></td>'
    td2 = '<td><span class="simple-tree-table-handler simple-tree-table-icon" style="margin-left: 0px;"></span>%s</td>'
    tdb = '<td>%s</td>'
    crud = """<td>
           <a href="#" id="Button1" onclick="showModalPopUp('/home/menus/update/%s/', 1100, 700)">
           <i class="fas fa-pen" style="font-size: 18px; color: #6C7AE0" data-toggle="tooltip" title="" data-bs-original-title="Update Menu" aria-label="Update Menu"></i>
            </a>&nbsp;&nbsp;&nbsp;
            <a href="/home/menus/delete/%s/" onclick="return confirm('Are you sure to delete %s menu?')">
           <i class="fas fa-trash-alt" style="font-size: 18px; color: #ce0f0f;" data-toggle="tooltip" title="" data-bs-original-title="Delete Menu" aria-label="Delete Menu"></i></a></td>
           """
    tr1txt = ''
    tr2txt = ''
    td1txt = ''
    td2txt = ''
    html1 = ''
    html2 = ''

    menus1 = menus.filter(parentid=1).order_by('id')
    for menu in menus1:
        # print(menu.title, menu.address)
        td1txt += crud % (menu.id, menu.id, menu.title)
        td1txt += td1 % menu.title
        td1txt += tdb % menu.address
        td1txt += tdb % menu.icon
        td1txt += tdb % menu.is_seen
        td1txt += tdb % menu.is_active
        td1txt += tdb % menu.has_item
        tr1txt += tr1 % (menu.id, td1txt)
        # print(tr1txt)
        menus2 = menus.filter(parentid=menu.id).order_by('id')
        for menu2 in menus2:
            td2txt = ''
            td2txt += crud % (menu2.id, menu2.id, menu2.title)
            td2txt += td2 % menu2.title
            td2txt += td2 % menu2.address
            td2txt += td2 % menu2.icon
            td2txt += td2 % menu2.is_seen
            td2txt += td2 % menu2.is_active
            td2txt += td2 % menu2.has_item
            tr2txt += tr2 % (menu2.id, menu2.parentid, td2txt)
        html1 += tr1txt + tr2txt
        tr1txt = ''
        tr2txt = ''
        td1txt = ''
    html2 = table % html1
    return mark_safe(html2)


@register.simple_tag
def getGroupMenusForAuth(id):
    menus = getGroupMenuObjects(1)
    ids = getGroupMenuObjectsIds(id)
    th = '<thead style="background-color: #6C7AE0">' \
         '<tr>' \
         '<th><span class="p-column-title">Select</span></th>' \
         '<th><span class="p-column-title">Title</span></th>' \
         '</tr>' \
         '</thead>'
    table = '<div style="overflow-x:auto;"><table id="example" class="table table-valign-middle">'+th+'%s</table></div>'

    tr1 = '<tr data-node-id="%s" style="background-color: #ECEAF4">%s</tr>'
    tr2 = '<tr data-node-id="%s" data-node-pid="%s" style="background-color: #FFFFFF">%s</tr>'
    td1 = '<td><span class="simple-tree-table-handler simple-tree-table-icon" style="margin-left: 0px;"></span><a href="#">%s</a></td>'
    td2 = '<td><span class="simple-tree-table-handler simple-tree-table-icon" style="margin-left: 0px;"></span>%s</td>'
    tdb = '<td>%s</td>'
    crud = """<td>
               <a href="#" id="Button1" onclick="showModalPopUp('/home/menus/update/%s/', 1100, 700)">
               <i class="fas fa-pen" style="font-size: 18px; color: #6C7AE0" data-toggle="tooltip" title="" data-bs-original-title="Update Menu" aria-label="Update Menu"></i>
                </a>&nbsp;&nbsp;&nbsp;
                <a href="/home/menus/delete/%s/" onclick="return confirm('Are you sure to delete %s menu?')">
               <i class="fas fa-trash-alt" style="font-size: 18px; color: #ce0f0f;" data-toggle="tooltip" title="" data-bs-original-title="Delete Menu" aria-label="Delete Menu"></i></a></td>
               """
    check1 = '<td><input type="checkbox" name="menus%s" value="%s" id="id_menus_%s" %s></td>'
    check2 = '<td><input type="checkbox" name="menus%s" value="%s" id="id_menus_%s"></td>'
    checkp1 = '<td><input type="checkbox" name="menus%s" value="%s" id="id_menus_%s" parentid="%s" %s></td>'
    checkp2 = '<td><input type="checkbox" name="menus%s" value="%s" id="id_menus_%s" parentid="%s"></td>'
    tr1txt = ''
    tr2txt = ''
    td1txt = ''
    td2txt = ''
    html1 = ''
    html2 = ''

    menus1 = menus.filter(parentid=1).order_by('id')
    for menu in menus1:
        # print(menu.title, menu.address)
        if menu.id in ids:
            td1txt += check1 % (menu.id, menu.id, menu.id, 'checked')
        else:
            td1txt += check2 % (menu.id, menu.id, menu.id)
        td1txt += td1 % menu.title
        tr1txt += tr1 % (menu.id, td1txt)
        # print(tr1txt)
        menus2 = menus.filter(parentid=menu.id).order_by('id')
        for menu2 in menus2:
            td2txt = ''
            if menu.id in ids:
                td2txt += checkp1 % (menu2.id, menu2.id, menu2.id, menu2.parentid, 'checked')
            else:
                td2txt += checkp2 % (menu2.id, menu2.id, menu2.id, menu2.parentid)
            td2txt += td2 % ('&nbsp;&nbsp;&nbsp;&nbsp;' + menu2.title)
            tr2txt += tr2 % (menu2.id, menu2.parentid, td2txt)
        html1 += tr1txt + tr2txt
        tr1txt = ''
        tr2txt = ''
        td1txt = ''
    html2 = table % html1
    return mark_safe(html2)


@register.simple_tag(takes_context=True)
def cookie(context, cookie_name):  # could feed in additional argument to use as default value
    request = context['request']
    result = request.COOKIES.get(cookie_name, '')  # I use blank as default value
    return mark_safe(result)


@register.filter(name='split')
def split(value, key):
    """
      Returns the value turned into a list.
    """
    return value.split(key)


@register.filter(name='get_item')
def get_item(dictionary, key):
    try:
        value = dictionary.get(key)
        if value is None:
            value = dictionary.get(str(key))
    except KeyError as ke:
        value = dictionary.get(int(key))
    if value is None:
        value = ":"
    return value


@register.filter
def in_category(menus, parentid):
    if menus is None:
        return None
    menus1 = menus.filter(parentid=parentid)
    return menus1


@register.simple_tag
def get_licensetypes():
    licensetypes = utilities.get_licensetypes()
    str = ''
    for i in licensetypes:
        str += i[1] + ','
    return str[:-1]


@register.simple_tag
def get_licensetypes_str(ids):
    ids = re.findall('(\d+)', ids)
    str = ''
    for i in utilities.get_licensetypes():
        for j in ids:
            if int(j) in i:
                str += i[1] + ','
    return str[:-1]
