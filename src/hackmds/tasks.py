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
from django.contrib.auth.models import User

from bs4 import BeautifulSoup, NavigableString, Tag

from hackmds.models import Archive

from concurrent import futures

from markupsafe import Markup


cutoff = 0.6

logger = logging.getLogger(__name__)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# for test
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

    # all email str lower()，remove replicate email
    to = list(set(i.lower for i in to))
    cc = list(set(i.lower for i in cc))

    email = EmailMessage(
        subject=email_subject,
        body=email_body,
        from_email=from_email,
        to=to,
        bcc=bcc,
        cc=cc,
        headers={'Reply-To': from_email}
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
    email_to = [u.email for u in user.objects.all()]
    from_email = ['test@gmail.com']  # 暫時先放 test@gmail.com
    return send_mail(
        email_subject=email_subject,
        email_body=email_body,
        to=email_to,
        from_email=from_email
    )


def hackmd_ck_task(url='https://hackmd.io/s/ByIn4AYaZ'):
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
        diff_count = str(result).count('<int>')
        print('上一次內容差異數: {}'.format(diff_count))
        
        if diff_count > 0:
            Archive.objects.filter(url=url).update(content=content)

        #if diff_count > 5:
        #    # notify by django email alarm by threading
        #    with futures.ThreadPoolExecutor(workers=1) as execute:
        #        res = execute.submit(hackmd_notify_email, url, result)
        #    return res
        return
    else:
        print('第一次新增')
        Archive.objects.create(url=url, content=content)
    return

if __name__ == '__main__':
    hackmd_ck_task()
