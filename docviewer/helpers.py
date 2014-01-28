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

    document = Document.objects.get(pk=doc_id)

    if task_id is not None and document.task_id != task_id:
        raise Exception("Celery task ID doesn't match")
    
    document.status = Document.STATUS.running
#    document.task_start = datetime.now()
    document.task_start = datetime.utcnow().replace(tzinfo=utc)
    document.save()

    try:
        docsplit(document)
        
#        try:
#            path = document.docfile.file.name
#            pdf = pyPdf.PdfFileReader(open(path, 'r'))
#            if pdf.getIsEncrypted():
#                pdf.decrypt('')
#            document.page_count = pdf.getNumPages()
#        except:
#            pass
        
        document.generate()
        document.status = document.STATUS.ready
        document.task_id = None
        document.task_error = None
        document.task_end = datetime.utcnow().replace(tzinfo=utc)
        document.save()
        
#        try:
        email = create_email(document)
        send_mail(
            'Festos',
            email['message'],
            'noreply@festos.cultureplex.ca',
            email['recipient_list'],
            fail_silently=True
        )
#        except smtplib.SMTPException as e:
#        except:
#            pass
    except Exception, e:

        try:
            document.task_error = "error - it can't save " + str(e)
            document.status = document.STATUS.failed
            document.save()

        except:
            pass

        raise


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
