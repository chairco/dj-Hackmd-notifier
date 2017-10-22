# - coding: utf-8 -*-
import os
import sys
import logging
import requests
import django
import diffhtml

from django.shortcuts import render
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from django.contrib.auth.models import User
from hackmds.models import Archive

from bs4 import BeautifulSoup

from concurrent import futures

from markupsafe import Markup


cutoff = 0.6

logger = logging.getLogger(__name__)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# For test
if not settings.configured:
    """setting the Django env()"""
    logger.debug('settings.configured: {0}'.format(settings.configured))
    sys.path.append(BASE)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings.local')
    django.setup()
    logger.debug('settings.configured: {0}'.format(settings.configured))
    from django.contrib.auth.models import User
    from hackmds.models import Archive


def send_mail(email_subject, email_body, to, cc=None, bcc=None, from_email=None):
    if bcc is None:
        bcc = []
    else:
        bcc = bcc

    if cc is None:
        cc = []
    else:
        cc = cc
        cc = list(set(i.lower() for i in cc)) # all email str lower()，remove replicate email

    # all email str lower()，remove replicate email
    to = list(set(i.lower() for i in to))
    
    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=from_email,
        to=to,
        bcc=bcc,
        cc=cc,
        #headers={'Reply-To': from_email}
    )
    email.content_subtype = "html"
    return email.send(fail_silently=False)


def hackmd_notify_email(email_subject, result, *, cc=None):
    t = loader.get_template(
        os.path.join(
            os.path.join(settings.BASE_DIR, 'templates'), 'email/'
        ) + 'hackmds_notify.html'
    )
    email_body = t.render({'result': result})
    email_to = [u.email for u in User.objects.all()]
    from_email = 'chairco@gmail.com'  # 暫時先放 test@gmail.com
    return send_mail(
        email_subject=email_subject,
        email_body=email_body,
        to=email_to,
        from_email=from_email
    )


def hackmd_ck_task(url):
    """@bref open requests to parse information from hackmd.io
    """
    url = url.split('#')[0]  # get the url none anchor
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError('check url')

    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find(
        'div', {'id': 'doc', 'class': 'container markdown-body'})
    content = content.string

    """@bref find keywords to generate notification
    """
    if len(Archive.objects.filter(url=url)):
        compare = Archive.objects.get(url=url)
        email_subject = url
        result = Markup('<br>').join(
            diffhtml.ndiff(compare.content.splitlines(),
                           content.splitlines(), cutoff=cutoff)
        )  # default cutoff = 0.6
        diff_count = str(result).count('<ins>')
        print('上一次內容差異數: {}'.format(diff_count))

        if diff_count > 0:
            Archive.objects.filter(url=url).update(content=content)

        if diff_count > 5:
           # notify by django email alarm by threading
           with futures.ThreadPoolExecutor(max_workers=1) as execute:
               res = execute.submit(hackmd_notify_email, url, result)
           return res
           #hackmd_notify_email(email_subject='test', result=result)
        return
    else:
        print('第一次新增')
        Archive.objects.create(url=url, content=content)
    return
