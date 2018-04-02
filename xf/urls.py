"""xf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from hds.views import *

urlpatterns = [
    url(r'^rootloginpage/', admin.site.urls),
    url(r'^$', loginpage),
    url(r'^login/$', login),
    url(r'^userinfo/$', userinfo),
    url(r'^changeinfo/$', changeinfo),
    url(r'^borrowpage/$', borrowpage),
    url(r'^weekchange/$', weekchange),
    url(r'^borrow/$', borrow),
    url(r'^brrcd/$',brrcd),
    url(r'^lendpage/$',lendpage),
    url(r'^sysmena/$', sysmena),
    url(r'^lend/$', lend),
    url(r'^setday/$', setday),
    url(r'^setcolor/$', setcolor),
    url(r'^deleteAdmin/$', deleteAdmin),
    url(r'^getInfoById/$', getInfoById),
    url(r'^saveadmin/$', saveadmin),
    url(r'^addAdmin/$', addAdmin),
    url(r'^addUser/$', addUser),
    url(r'^resetpwd/$', resetpwd),
    url(r'^deleteUser/$', deleteUser),
    url(r'^updateUser/$', updateUser),
    url(r'^resetsys/$', resetsys),
]
