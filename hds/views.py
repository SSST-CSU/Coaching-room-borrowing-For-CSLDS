# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from models import *
import xml.etree.ElementTree as ET
from datetime import datetime, date, timedelta
import json
from django.utils import timezone
# Create your views here.


def loginpage(request):
    return render(request, 'login.html')


def login(request):
    try:
        id = request.POST['id']
        pwd = request.POST['pwd']
    except:
        id = request.GET['id']
        pwd = request.GET['pwd']
    reload(sys)
    sys.setdefaultencoding('utf-8')
    user = User.objects.filter(id=id)
    success = False
    isadmin = 0
    if user.count() == 0:
        success = False
        return HttpResponseRedirect("/")
    if user.first().pwd == pwd:
        success = True
    else:
        success = False
    if success:
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + user.first().id + user.first().name + ' 登录'))
        admin = Admin.objects.filter(user=user)
        if admin.count() == 1:
            isadmin = admin.first().level
            f.write(' 管理员级别：%s'%isadmin)
        f.write('\n')
        f.close()
        return render(request, 'index.html', {
            'userid': user.first().id,
            'username': user.first().name,
            'userpwd': user.first().pwd,
            'admin': isadmin,
            'indexpage': True,
        })
    else:
        return HttpResponseRedirect("/")


def userinfo(request):
    id = request.POST['id']
    user = User.objects.filter(id=id)
    name = user.first().name
    pwd = user.first().pwd
    tel = user.first().tel
    mail = user.first().mail
    return render(request, 'userinfo.html', {
        'id': id,
        'name': name,
        'pwd': pwd,
        'tel': tel,
        'mail': mail,
    })


def changeinfo(request):
    id = request.POST['id']
    name = request.POST['name']
    pwd = request.POST['pwd']
    tel = request.POST['tel']
    mail = request.POST['mail']
    user = User.objects.filter(id=id).filter()
    user.update(pwd=pwd, tel=tel, mail=mail)
    adminlevel = 0
    admin = Admin.objects.filter(user__id=id)
    if admin.count() == 1:
        adminlevel = int(admin.first().level)
    f = open('hds/logs/' + str(date.today()) + '.log', 'a')
    f.write(unicode(str(timezone.now()) + ' 用户：' + user.first().id + user.first().name + ' 修改个人信息为：[id=' + id + ', name=' + name + ', pwd=' + pwd + ', tel=' + tel + ', mail=' + mail + ']'))
    f.write('\n')
    f.close()
    return render(request, 'index.html', {
        'userid': id,
        'username': name,
        'userpwd': pwd,
        'admin': adminlevel,
    })


def borrowpage(request):
    id = request.POST['id']
    user = User.objects.get(id=id)
    tree = ET.parse('hds/data.xml')
    root = tree.getroot()
    year = root[0][0].text
    month = root[0][1].text
    day = root[0][2].text
    firstday = date(year=int(year), month=int(month), day=int(day))
    today = date.today()
    #today = date(2017, 10, 29)
    deltaday = (today - firstday).days
    weeknum = deltaday / 7 + 1
    weeks = range(weeknum, 21, 1)
    backcolor = root[1].text
    #print backcolor
    return render(request, 'br.html', {
        'user': user,
        'weeks': weeks,
        'backcolor': backcolor,
    })


def weekchange(request):
    brrcd = BorrowRecord.objects.all()

    weeknum = int(request.POST['week'])

    tree = ET.parse('hds/data.xml')
    root = tree.getroot()
    year = root[0][0].text
    month = root[0][1].text
    day = root[0][2].text
    firstday = date(year=int(year), month=int(month), day=int(day))

    week = []
    deltaday = (weeknum - 1) * 7
    delta = timedelta(days=deltaday)
    weekfirstday = firstday + delta
    for index in range(0, 7):
        t = {}
        br = brrcd.filter(date=weekfirstday)
        for i in range(0, 5):
            b = br.filter(time=i)
            if b.count() == 0:
                t[i] = ""
            elif b.first().stat == "同意申请":
                t[i] = "同意申请"
            else:
                t[i] = ""
        theday = {
            'month': weekfirstday.month,
            'day': weekfirstday.day,
            'time': t,
        }
        week.append(theday)
        weekfirstday += timedelta(days=1)
    ret = {
        'days': week,
    }
    #print ret
    return HttpResponse(json.dumps(ret))


def borrow(request):
    reload(sys)
    sys.setdefaultencoding('utf8')
    userid = request.POST['userid']
    weeknum = int(request.POST['week'])
    time = request.POST['time']
    date0 = request.POST['date']
    num = request.POST['num']
    use = request.POST['use']
    com = request.POST['com']
    deltaday = (weeknum - 1) * 7
    delta = timedelta(days=deltaday)

    tree = ET.parse('hds/data.xml')
    root = tree.getroot()
    year = root[0][0].text
    month = root[0][1].text
    day = root[0][2].text
    firstday = date(year=int(year), month=int(month), day=int(day))
    weekfirstday = firstday + delta
    selectday = weekfirstday + timedelta(days=int(date0))
    try:
        BorrowRecord.objects.create(
            applydatetime = timezone.now(),
            date=selectday,
            time=int(time),
            user=User.objects.get(id=userid),
            num=num,
            com=com,
            usereason=use,
            stat="申请中"
        )
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(('%s 用户：%s%s 申请借用 %s %s活动室，人数：%s')%(str(timezone.now()), id, User.objects.get(id=userid).name, str(selectday), str(time), str(num))))
        f.write('\n')
        f.close()
    except Exception, e:
        print e
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def brrcd(request):
    id = request.POST['id']
    admin = Admin.objects.filter(user__id=id)
    if admin.count() == 0:
        br = BorrowRecord.objects.filter(user__id=id)
    else:
        br = BorrowRecord.objects.all().order_by('date')
    return render(request, 'brrcd.html',{
        'brrcd': br,
    })


def lendpage(request):
    id = request.POST['id']
    br = BorrowRecord.objects.all()
    return render(request, 'lend.html',{
        'brrcd': br,
        'myid': id,
    })


def lend(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    id = request.POST['userid']
    date = request.POST['date']
    time = request.POST['time']
    stat = request.POST['stat']
    adminid = request.POST['adminid']
    adminname = Admin.objects.get(user__id=adminid).user.name
    date = datetime.strptime(date, "%Y年%m月%d日").date()
    br = BorrowRecord.objects.filter(date=date, time=time, user__id=id)
    try:
        br.update(stat=stat)
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + adminname + ' 同意 ' + id + str(User.objects.get(id=id).name) + ' ' + str(date) + ' ' + time + ' 的申请'))
        f.write('\n')
        f.close()
    except:
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def sysmena(request):
    id = request.POST['id']
    reload(sys)
    sys.setdefaultencoding('utf-8')
    tree = ET.parse('hds/data.xml')
    root = tree.getroot()
    year = root[0][0].text
    month = str(root[0][1].text).zfill(2)
    day = str(root[0][2].text).zfill(2)
    backcolor = root[1].text
    admin = Admin.objects.all().order_by('level', 'user_id')
    user = User.objects.all().order_by('id')
    alluser = []
    for u in user:
        level = 0
        a = Admin.objects.filter(user=u).first()
        if a == None:
            pass
        else:
            level = a.level
        info = {
            'user': u,
            'level': level
        }
        alluser.append(info)
    mylevel = Admin.objects.get(user__id=id).level
    myself = User.objects.get(id=id)
    f = open('hds/logs/' + str(date.today()) + '.log', 'a')
    f.write(unicode(str(timezone.now()) + ' 用户：' + id + str(myself.name) + ' 进入系统管理页面 管理员级别：' + str(mylevel)))
    f.write('\n')
    f.close()
    f = open('hds/logs/' + str(date.today()) + '.log')
    log = f.read()
    f.close()
    return render(request, 'sysmena.html', {
        'year': year,
        'month': month,
        'day': day,
        'admin': admin,
        'backcolor': backcolor,
        'user': user,
        'mylevel': mylevel,
        'myself': myself,
        'alluser': alluser,
        'log': log,
    })


def setday(request):
    year = request.POST['year']
    month = request.POST['month']
    day = request.POST['day']
    anyday = datetime(int(year), int(month), int(day)).strftime("%w")
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    if anyday != '0':
        ret = {
            'msg': -1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 设置开学时间失败，原因：日期非星期日'))
        f.write('\n')
        f.close()
    else:
        try:
            tree = ET.parse('hds/data.xml')
            root = tree.getroot()
            root[0][0].text = year
            root[0][1].text = month
            root[0][2].text = day
            tree.write('hds/data.xml')
            ret = {
                'msg': 1,
            }
            f = open('hds/logs/' + str(date.today()) + '.log', 'a')
            f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 设置开学时间成功：' + str(year) + '年' + str(month) + '月' + str(day) + '日'))
            f.write('\n')
            f.close()
        except Exception,e:
            print e
            ret = {
                'msg': 0,
            }
            f = open('hds/logs/' + str(date.today()) + '.log', 'a')
            f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 设置开学时间失败，原因：' + e))
            f.write('\n')
            f.close()
    return HttpResponse(json.dumps(ret))


def setcolor(request):
    color = request.POST['color']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        tree = ET.parse('hds/data.xml')
        root = tree.getroot()
        root[1].text = color
        tree.write('hds/data.xml')
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 设置背景颜色为：' + color))
        f.write('\n')
        f.close()
    except Exception, e:
        print e
        ret = {
            'msg': 0,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 设置背景颜色失败，原因：' + e))
        f.write('\n')
        f.close()
    return HttpResponse(json.dumps(ret))


def deleteAdmin(request):
    id = request.POST['id']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        Admin.objects.get(user__id=id).delete()
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 删除管理员：' + adminid + admin.user.id))
        f.write('\n')
        f.close()
    except Exception, e:
        print e
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def getInfoById(request):
    id = request.POST['id']
    msg = 0
    try:
        user = User.objects.get(id=id)
        msg = 1
    except:
        pass
    if msg == 1:
        try:
            admin = Admin.objects.get(user__id=id)
            msg = 2
        except:
            pass
    if msg == 0:
        ret = {
            'msg': 0,
        }
    elif msg == 1:
        ret = {
            'msg': 1,
            'name': user.name,
        }
    else:
        ret = {
            'msg': 2,
            'level': admin.level,
            'name': user.name,
        }
    return HttpResponse(json.dumps(ret))


def saveadmin(request):
    id = request.POST['id']
    level = request.POST['level']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        admin1 = Admin.objects.filter(user__id=id)
        admin1.update(level=level)
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 修改管理员信息：' + id + str(admin.user.name) + ' 级别：' + str(level)))
        f.write('\n')
        f.close()
    except:
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def addAdmin(request):
    id = request.POST['id']
    level = request.POST['level']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        admin1 = Admin.objects.filter(user__id=id)
        if admin1.count() == 0:
            user = User.objects.get(id=id)
            Admin.objects.create(user=user, level=int(level))
            ret = {
                'msg': 1,
                'name': user.name,
            }
            f = open('hds/logs/' + str(date.today()) + '.log', 'a')
            f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 增加管理员信息：' + id + str(
                admin.user.name) + ' 级别：' + str(level)))
            f.write('\n')
            f.close()
        else:
            admin.update(level=level)
            ret = {
                'msg': 2,
            }
    except:
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def addUser(request):
    ret = {
        'msg': 0,
    }
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    id = request.POST['id']
    name = request.POST['name']
    tel = request.POST['tel']
    mail = request.POST['mail']
    try:
        u = User.objects.get(id=id)
        User.objects.filter(id=id).update(name=name, tel=tel, mail=mail)
        ret = {
            'msg': 1,
        }
    except:
        User.objects.create(id=id, pwd=id, name=name, tel=tel, mail=mail)
        ret = {
            'msg': 1,
        }
    f = open('hds/logs/' + str(date.today()) + '.log', 'a')
    f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 增加用户：' + id + name))
    f.write('\n')
    f.close()
    return HttpResponse(json.dumps(ret))


def resetpwd(request):
    id = request.POST['id']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        User.objects.filter(id=id).update(pwd=id)
        ret = {
            'msg': 1,
        }
    except:
        ret = {
            'msg': 0,
        }
    f = open('hds/logs/' + str(date.today()) + '.log', 'a')
    f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 重置' + id + str(User.objects.get(id=id).name) + '密码'))
    f.write('\n')
    f.close()
    return HttpResponse(json.dumps(ret))


def deleteUser(request):
    id = request.POST['id']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        name = User.objects.get(id=id).name
        Admin.objects.filter(user__id=id).delete()
        User.objects.filter(id=id).delete()
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 删除用户' + id + name))
        f.write('\n')
        f.close()
    except:
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def updateUser(request):
    reload(sys)
    sys.setdefaultencoding('utf8')
    id = request.POST['id']
    nid = request.POST['nid']
    name = request.POST['name']
    tel = request.POST['tel']
    mail = request.POST['mail']
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        User.objects.filter(id=id).update(id=nid, name=name, tel=tel, mail=mail)
        ret = {
            'msg': 1,
        }
        f = open('hds/logs/' + str(date.today()) + '.log', 'a')
        f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 修改用户信息' + str(id) + str(name)))
        f.write('\n')
        f.close()
    except Exception, e:
        print e
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))


def resetsys(request):
    reload(sys)
    sys.setdefaultencoding('utf8')
    adminid = request.POST['adminid']
    admin = Admin.objects.get(user__id=adminid)
    try:
        user = User.objects.get(id=adminid)
        admin1 = Admin.objects.get(user=user)
        if admin1.level >= 2:
            BorrowRecord.objects.all().delete()
            tree = ET.parse('hds/data.xml')
            root = tree.getroot()
            root[0][0].text = '2000'
            root[0][1].text = '1'
            root[0][2].text = '1'
            root[1].text = '#000'
            tree.write('hds/data.xml')
            ret = {
                'msg': 1,
            }
            f = open('hds/logs/' + str(date.today()) + '.log', 'a')
            f.write(unicode(str(timezone.now()) + ' 用户：' + adminid + str(admin.user.name) + ' 重置系统'))
            f.write('\n')
            f.close()
    except Exception, e:
        print e
        ret = {
            'msg': 0,
        }
    return HttpResponse(json.dumps(ret))
