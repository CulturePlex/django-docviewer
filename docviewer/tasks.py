import logging
from celery.task import task
from django.core.exceptions import ObjectDoesNotExist

#logging.basicConfig(filename='/tmp/celery2.log', level=logging.DEBUG)
#logger = logging.getLogger(__name__)

@task(default_retry_delay=10, max_retries=5)
def task_generate_document(doc_id, task_id=None):
    from docviewer.helpers import generate_document
    try:
        generate_document(doc_id, task_id)
    except ObjectDoesNotExist, e:
#        logger.info('asd')
        task_generate_document.retry(exc=e)
