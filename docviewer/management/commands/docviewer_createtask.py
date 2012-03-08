from django.core.management.base import BaseCommand
from docviewer.models import Document
from docviewer.tasks import task_generate_document



class Command(BaseCommand):
    
    
    def handle(self, *args, **options):
        
        doc = Document.objects.get(pk=args[0])
        task = task_generate_document.apply_async(args=[doc.pk, "%s/%s" % (doc.get_root_path(), args[1])], countdown=5)
        doc.task_id = task.task_id
        doc.save()
        