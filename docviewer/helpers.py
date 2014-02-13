import os
from subprocess import Popen, PIPE
from docviewer.settings import IMAGE_FORMAT
from docviewer.models import Document, Edition
from datetime import datetime
import shutil

from django.core.mail import send_mail
import smtplib
from django.template import Context, loader
import utils
from django.utils.timezone import utc
from views import get_absolute_url
from django.core.urlresolvers import reverse
#import pyPdf
from documents.utils import count_total_pages
from django.conf import settings


def docsplit(document):

    path = document.get_root_path()
    commands = [
        "/usr/bin/docsplit images --size 700x,1000x,180x --format %s --output %s %s/%s.pdf" % (IMAGE_FORMAT, path, path, document.slug),
        "/usr/bin/docsplit text --pages all -l %s --no-clean --output %s %s/%s.pdf" % (
            document.language, path, path, document.slug)]

    print "/usr/bin/docsplit text --pages all -l %s --no-clean--output %s %s/%s.pdf" % (
            document.language, path, path, document.slug)

    if document.docfile_basename.split('.')[-1].lower() != 'pdf':
        cmd = "/usr/bin/docsplit pdf --output %s %s" % (path, document.get_file_path())
        commands.insert(0, cmd)

    for command in commands:
        result = Popen(command, shell=True, stdout=PIPE).stdout.read()

        if len(result) > 0:
            raise Exception(result)

    # rename directories
    shutil.rmtree("%s/%s" % (path, "large"), ignore_errors=True)
    os.rename("%s/%s" % (path, "1000x"), "%s/%s" % (path, "large"))

    shutil.rmtree("%s/%s" % (path, "normal"), ignore_errors=True)
    os.rename("%s/%s" % (path, "700x"), "%s/%s" % (path, "normal"))

    shutil.rmtree("%s/%s" % (path, "small"), ignore_errors=True)
    os.rename("%s/%s" % (path, "180x"), "%s/%s" % (path, "small"))


def create_document(filepath, doc_attributes):
    d = Document(**doc_attributes)
    d.save()
    return d


def generate_document(doc_id, task_id=None):
    CELERY_ID = 0
    PROC_INIT = 1
    PROC_PROC = 2
    FILE_CREA = 3
    PROC_FINA = 4
    MAIL_DATA = 5
    MAIL_SEND = 6
    
    try:
        document = Document.objects.get(pk=doc_id)
        if task_id is not None and document.task_id != task_id:
            raise Exception(CELERY_ID)
        
        try:
            document.status = Document.STATUS.starting
            document.task_start = datetime.utcnow().replace(tzinfo=utc)
            document.save()
        except Exception as e:
            raise Exception(PROC_INIT, e.message)
        
        try:
            docsplit(document)
        except Exception as e:
            raise Exception(PROC_PROC, e.message)
        
        try:
            document.generate()
        except Exception as e:
            raise Exception(FILE_CREA, e.message)
        
        try:
            document.status = document.STATUS.ready
            document.task_error = None
            document.task_end = datetime.utcnow().replace(tzinfo=utc)
#            document.save()
        except Exception as e:
            raise Exception(PROC_FINA, e.message)
        
        try:
            email = create_email(document)
        except Exception as e:
            raise Exception(MAIL_DATA, e.message)
        
        try:
            send_mail(
                prod_settings.PROJECT_NAME,
                email['message'],
                prod_settings.DEFAULT_FROM_EMAIL,
                email['recipient_list'],
                fail_silently=False
            )
        except Exception as e:
            raise Exception(MAIL_SEND, e.message)
        
    except Exception as e:
        if e.args[0] == MAIL_DATA:
            document.task_error = 'Error in email data: ' + e.args[1]
        elif e.args[0] == MAIL_SEND:
            document.task_error = 'Email could not be sent: ' + e.args[1]
        else:
            document.status = document.STATUS.failed
            if e.args[0] == CELERY_ID:
                document.task_error = \
                    'Celery task ID does not match'
            elif e.args[0] == PROC_INIT:
                document.task_error = \
                    'Process could not be initialized: ' + e.args[1]
            elif e.args[0] == PROC_PROC:
                document.task_error = \
                    'Document could not be processed: ' + e.args[1]
            elif e.args[0] == FILE_CREA:
                document.task_error = \
                    'File system could not be created: ' + e.args[1]
            elif e.args[0] == PROC_FINA:
                document.task_error = \
                    'Process could not be finalized: ' + e.args[1]
            else:
                document.task_error = \
                    'Unknown error: ' + e.args[1]
    
    finally:
        document.save()

def create_email(document):
    email = {}
    
    docu = document.document
    
    status = document.status
    username = docu.owner.username
    title = document.title
    filename = document.docfile_basename
    string_start_datetime = utils.datetime_to_string(document.task_start)
    start_time = utils.format_datetime_string(string_start_datetime)
    string_end_datetime = utils.datetime_to_string(document.task_end)
    end_time = utils.format_datetime_string(string_end_datetime)
    diff_time = document.task_end - document.task_start
    total_time = utils.format_datetimediff(diff_time)
    doc_url = get_absolute_url(reverse(
        "docviewer_viewer_view",
        kwargs={'pk': document.pk, 'slug': document.slug}
    ))
    festos_url = get_absolute_url(document.related_url)
    template = loader.get_template('docviewer/email.html')
    context = Context({
        'status': status,
        'username': username,
        'document': '{} - {}'.format(title, filename),
        'start_time': start_time,
        'end_time': end_time,
        'total_time': total_time,
        'doc_url': doc_url,
        'festos_url': festos_url,
    })
    message = template.render(context)
    
    contributors = docu.get_users_with_perms()
    recipient_list = [docu.owner.email] + [c.email for c in contributors]
    
    email['message'] = message
    email['recipient_list'] = recipient_list
    return email
