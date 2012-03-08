import os
from subprocess import Popen, PIPE
from docviewer.settings import IMAGE_FORMAT
from docviewer.models import Document
from docviewer.tasks import task_generate_document
from datetime import datetime

def docsplit(path):
    
    output = '/'.join(path.split('/')[:-1])
    
    commands = ["/usr/bin/docsplit images --size 700x,1000x,180x --format %s --output %s %s" % (IMAGE_FORMAT,output, path), 
                "/usr/bin/docsplit text --pages all --output %s %s" % (output, path)]
    
    for command in commands:
        result = Popen(command, shell=True, stdout=PIPE).stdout.read()
        
        if len(result) > 0:
            raise Exception(result)
        
    # rename directories
    os.rename("%s/%s" % (output, "1000x"), "%s/%s" % (output, "large"))
    os.rename("%s/%s" % (output, "700x"), "%s/%s" % (output, "normal"))
    os.rename("%s/%s" % (output, "180x"), "%s/%s" % (output, "small"))    
        
def create_document(filepath, doc_attributes):
    
    d = Document(**doc_attributes)
    d.save()
    
    d.set_file(filepath)
    
    task = task_generate_document.apply_async(args=[d.pk], countdown=5)
    
    d.task_id = task.task_id
    d.save()
    
    return d


def generate_document(doc_id,  task_id=None):
    
    document = Document.objects.get(pk=doc_id)
        
    if task_id is not None and document.task_id != task_id:
        raise Exception("Celery task ID doesn't match")
    
    document.status = Document.STATUS.running
    document.task_start = datetime.now()
    document.save()
    
    try:
        docsplit(document.get_file_path())
    
        document.generate()
        document.status = document.STATUS.ready
        document.task_id = None
        document.task_error = None
        document.save()
    except Exception, e:
        
        try:
            document.task_error = str(e)
            document.status = document.STATUS.failed
            document.save()
        except:
            pass
        
        raise