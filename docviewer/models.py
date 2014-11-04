from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from model_utils.models import TimeStampedModel, StatusModel
from model_utils import Choices
from autoslug.fields import AutoSlugField
import json
import os
import re
import codecs
import shutil
import uuid

from jsonfield import JSONField
from datetime import datetime

from docviewer.settings import IMAGE_FORMAT, DOCUMENT_ROOT, DOCUMENT_URL
from docviewer.tasks import task_generate_document

from taggit.managers import TaggableManager


RE_PAGE = re.compile(r'^.*_([0-9]+)\.txt')
RE_TS = re.compile(r'^.*([0-9]{20})\.txt')

zeros = '0'*20
nines = '9'*20

#fs = get_storage_class()()

class Document(TimeStampedModel, StatusModel):

    STATUS = Choices(
        'waiting', 'ready', 'running', 'failed', 'starting', 'copied',
    )
    LANGUAGES = Choices(
        ("eng","English"),
        ("spa","Spanish"),
        ("spa_old","Old Spanish"))

    slug = AutoSlugField(
        _('Slug'), max_length=255, unique=True, populate_from='title')
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), null=True, blank=True)
    source_url = models.URLField(
        _('Source URL of the document'), max_length=1024, null=True,
        blank=True)
    language = models.CharField(_('Language'), choices=LANGUAGES,
        default='spa', max_length=7, null=False, blank=False)
    page_count = models.PositiveIntegerField(
        null=True, blank=True, help_text=_('Total page in the document'))
    contributor = models.CharField(
        _('Contributor'), max_length=255, null=True, blank=True)
    contributor_organization = models.CharField(
        _('Contributor organization'),
        max_length=255, null=True, blank=True)
    download = models.BooleanField(
        _('Allow download'), default=True,
        help_text=_('Allow original document download'))
    related_url = models.URLField(
        _('Url where the document can be view'),
        max_length=1024, null=False, blank=True, default='')
    docfile = models.FileField(
        _('PDF Document File'), upload_to='pdfs/%Y/%m/%d', max_length=512,
        null=False, blank =False,)# storage=FileSystemStorage())
    task_id = models.CharField(
        _('Celery task ID'), max_length=50, null=True, blank=True)
    task_error = models.TextField(
        _('Celery error'), null=True, blank=True)
    task_start = models.DateTimeField(
        _('Celery date start'), null=True, blank=True)
    task_end = models.DateTimeField(
        _('Celery date end'), null=True, blank=True)
    
    taggit_tags = TaggableManager()

    @models.permalink
    def get_absolute_url(self):
        return ("docviewer_viewer_view", (), {
            'slug': self.slug, 'pk': self.pk})

    def __unicode__(self):
        return u"%s %s (status:%s)" % (self.pk, self.title, self.status)

    @property
    def text_url(self):
        return "%s/%s.txt" % (self.get_root_url(), self.slug)

    @property
    def thumbnail_url(self):
        return "%s/small/%s_1.%s" % (
            self.get_root_url(), self.slug, IMAGE_FORMAT)

    @property
    def doc_url(self):
        return "%s/%s.pdf" % (self.get_root_url(), self.slug)

    @property
    def text_page_url(self):
        return "%s/%s_%%(page)s.txt" % (self.get_root_url(), self.slug)

    @property
    def image_page_url(self):
        return "%s/%%(size)s/%s_%%(page)s.%s" % (
            self.get_root_url(), self.slug, IMAGE_FORMAT)

    def get_root_path(self):
        return "%s%s" % (DOCUMENT_ROOT, self.id)

    def get_root_url(self):
        return "%s%s" % (DOCUMENT_URL, self.id)

    @property
    def text(self):
        fs = FileSystemStorage()#fs=get_
        f = fs.open(self.text_url, 'r')
        data = f.read()
        f.close()
        return data

#    def save(self, *args, **kwargs):
#        create = self.pk is None
#        super(Document, self).save(*args, **kwargs)
#        if create:
#            os.makedirs(self.get_root_path())
#            self.process_file()

    def get_file_path(self):
        return "%s/%s" % (self.get_root_path(), self.docfile_basename)

    def process_file(self):
        fs1 = FileSystemStorage()
        f1 = fs1.open(os.path.join(settings.MEDIA_ROOT,self.docfile.name), 'r')
        filepath = "%s/%s.%s" % (
            self.get_root_path(),
            self.slug,
            self.docfile_basename.split('.')[-1].lower())
        fs2 = FileSystemStorage()
        f2 = fs2.open(filepath, "w")
        f2.write(f1.read())
        f2.close()
        f1.close()

#        self.title = self.docfile_basename
        task = task_generate_document.apply_async(args=[self.pk], countdown=5)
        self.task_id = task.task_id
        self.save()

    @property
    def docfile_basename(self):
        return os.path.basename(self.docfile.name)

    def generate(self):
        # concatenate all text files
        ts = datetime.now()
        fs = FileSystemStorage()
        all_txt = fs.open("%s/%s.txt" % (self.get_root_path(), self.slug), "w")
        self.page_count = 0
        self.pages_set.all().delete()
        pages = {}
        for f in os.listdir(self.get_root_path()):
            if f[-4:] == '.txt' and f != "%s.txt" % self.slug:
                m = RE_PAGE.match(f)
                if m:
                    k = int(m.group(1))
                    pages[k] = f
        mod_pags_orig = {}
        mod_pags_curr = {}
        for k in pages:
            f = pages[k]
            self.page_count += 1
            tmp_path = "%s/%s" % (self.get_root_path(), f)
            fs_tmp = FileSystemStorage()
            tmp_file = fs_tmp.open(tmp_path)
            tmp_text = tmp_file.read()
            all_txt.write(tmp_text)
            page = Page(
                document=self,
                page=RE_PAGE.match(f).group(1),
                modified=ts,
            )
            page.save()
            tmp_file.close()
            
            filepath_orig = "%s/%s_%s-%s.txt" % (
                self.document.get_root_path(),
                self.document.slug,
                k,
                zeros
            )
            shutil.copy2(tmp_path, filepath_orig)
            
            text_url = self.document.text_page_url
            mod_pags_orig[self.page_count] = text_url.replace(
                '%(page)s',
                '{}-{}'.format(self.page_count, zeros)
            )
            mod_pags_curr[self.page_count] = text_url.replace(
                '%(page)s',
                '{}'.format(self.page_count)
            )
        Edition.objects.create(
            document=self.document,
            author=self.document.document.owner,
            comment='Original version',
            modified_pages=mod_pags_orig,
            date_string = zeros
        )
        Edition.objects.create(
            document=self.document,
            author=self.document.document.owner,
            comment='Current version',
            modified_pages=mod_pags_curr,
            date_string = nines
        )
        all_txt.close()

    def regenerate(self):
        # reconcatenate all text files
        fs = FileSystemStorage()
        all_txt = fs.open("%s/%s.txt" % (self.get_root_path(), self.slug), "w")
        pages = {}
        for f in os.listdir(self.get_root_path()):
            if f[-4:] == '.txt' and f != "%s.txt" % self.slug:
                m = RE_PAGE.match(f)
                if m:
                    k = int(m.group(1))
                    pages[k] = f
        for k in pages:
            f = pages[k]
            tmp_path = "%s/%s" % (self.get_root_path(), f)
            fs_tmp = FileSystemStorage()
            tmp_file = fs_tmp.open(tmp_path)
            tmp_text = tmp_file.read() +'\n'
            all_txt.write(tmp_text)
            tmp_file.close()
        all_txt.close()

    def regenerate_ts(self, ts='', files=[]):
        # reconcatenate all text files
        fs = FileSystemStorage()
        all_txt = fs.open("%s/%s--%s.txt" % (self.get_root_path(), self.slug, ts), "w")
        for f in files:
            tmp_path = "%s/%s" % (self.get_root_path(), f)
            fs_tmp = FileSystemStorage()
            tmp_file = fs_tmp.open(tmp_path)
            tmp_text = tmp_file.read()
            all_txt.write(tmp_text)
            tmp_file.close()
        all_txt.close()

    def get_thumbnail(self):
        return "%s/%s/%s_%s.%s" % (
            self.get_root_url(), "small", self.slug, 1, IMAGE_FORMAT)
    
    def get_hidden_pages(self):
        return map(lambda x: x.page, self.pages_set.filter(visible=False))

    def get_info(self):
        d = self.get_info_dict()
        info = ''
        for k in d:
            if k == 'cloned':
                info += 'Click on the info icon to see the original document\n'
            else:
                info += d[k] + '\n'
        info = info.strip()
        if not info:
            info = self.task_error
            if not info:
                info = ''
        return info

    def get_info_dict(self):
        try:
            info = json.loads(self.task_error)
        except:
            info = {}
        return info

    def add_info(self, key, value):
        info = self.get_info_dict()
        if self.task_error and not info:
            info['old'] = self.task_error
        info[key] = value
        self.task_error = json.dumps(info)

    class Meta:
        verbose_name = _(u'Document')
        verbose_name_plural = _(u'Document')


class Page(models.Model):
    " Model used to index pages "
    document = models.ForeignKey(Document, related_name='pages_set')
    page = models.PositiveIntegerField()
    modified = models.DateTimeField()
    visible = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.document.title + '-' + str(self.page)

    @property
    def text(self):
        path = "%s/%s_%s.txt" % (
            self.document.get_root_path(),
            self.document.slug,
            self.page,)
#        f = codecs.open(path, 'r')
        fs = FileSystemStorage()
        f = fs.open(path)
        data = f.read()
        f.close()
        return data.decode('ascii', 'ignore')

    def save_text(self, text, timestamp):
        path = "%s/%s_%s.txt" % (
            self.document.get_root_path(),
            self.document.slug,
            self.page)
#        f = codecs.open(path, 'r')
        fs = FileSystemStorage()
        f = fs.open(path, 'w')
        text = unicode(text).encode('utf-8')
        f.write(text)
        f.close()
        
        path_ts = "%s/%s_%s-%s.txt" % (
            self.document.get_root_path(),
            self.document.slug,
            self.page,
            timestamp)
        shutil.copy2(path, path_ts)

    def get_image(self, size):
        return "%s/%s/%s_%s.%s" % (
            self.document.get_root_url(), size, self.document.slug,
            self.page, IMAGE_FORMAT)

    def get_thumbnail(self):
        return self.get_image("small")


class Section(models.Model):
    document = models.ForeignKey(
        Document, verbose_name=_('Document'), related_name='sections_set')
    title = models.CharField(_('Title'), max_length=255)
    page = models.PositiveIntegerField(_('Page ID'))


class Annotation(models.Model):
    document = models.ForeignKey(Document, related_name='annotations_set')
    title = models.CharField(_('Title'), max_length=255)
    location = models.CommaSeparatedIntegerField(_('Coordinates'), max_length=50)
    page = models.PositiveIntegerField(_('Page ID'))
    content = models.TextField(_('Content'))
    author = models.ForeignKey(User, related_name='annotations')
    
    def __unicode__(self):
        return self.title


class Edition(models.Model):
    document = models.ForeignKey(Document, related_name='editions_set')
    date = models.DateTimeField(_(u'Date'), auto_now_add=True)
    date_string = models.CharField(_('Date string'), max_length=255)
    modified_pages = JSONField(_(u'Modified pages'))
    comment = models.TextField(_('Comment'))
    author = models.ForeignKey(User, related_name='editions')
    
    @property
    def previous(self):
        editions = self.document.editions_set.order_by('-date_string')
        for e in editions:
            if e.date_string < self.date_string:
                prev = e
                break
        else:
            prev = self
        return prev
    
    def delete(self, *args, **kwargs):
#        pages = kwargs['modified_pages']
        other_editions_for_this_document = \
            Edition.objects.filter(document=self.document).exclude(id=self.id)
        pages = self.modified_pages
        for page in pages:
            url = pages[page]
            ts = RE_TS.match(url).group(1)
            if ts != zeros and not self.there_is_pointing_editions(
                other_editions_for_this_document,
                page
            ):
                path = "%s/%s_%s-%s.txt" % (
                    self.document.get_root_path(),
                    self.document.slug,
                    page,
                    ts)
                os.remove(path)
        super(Edition, self).delete()
    
    def there_is_pointing_editions(self, other_editions, page):
        result = False
        this_url = self.modified_pages[page]
        for e in other_editions:
            url = e.modified_pages[page]
            if url == this_url:
                result = True
                break
        return result
    
    def __unicode__(self):
        return '({}) {} -- {}'.format(self.document.docfile_basename, self.document.title, str(self.date))


from django.db.models.signals import post_delete, post_save
from django.dispatch.dispatcher import receiver

@receiver(post_delete, sender=Document)
def document_delete(sender, instance, **kwargs):
    shutil.rmtree(instance.get_root_path(), ignore_errors=True)
    instance.docfile.delete(False)

#receiver(post_save, sender=Document)
def document_save(sender, instance, created, **kwargs):
    if issubclass(sender, Document):
        if instance.status in [Document.STATUS.ready, Document.STATUS.copied]:
            pass
        elif created:
            os.makedirs(instance.get_root_path())
            instance.process_file()

post_save.connect(document_save, dispatch_uid=str(uuid.uuid1()))
