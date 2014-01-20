from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.detail import BaseDetailView
from django.core.urlresolvers import reverse
from docviewer.models import Document, Page, Annotation, Edition
from django.utils.feedgenerator import rfc2822_date
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.sites.models import Site
from django.views.generic.base import View
from haystack.query import SearchQuerySet

from datetime import datetime
from utils import datetime_to_string, format_datetime_string

SITE = Site.objects.get_current()


def get_absolute_url(relative_url):
    if relative_url and (relative_url[0:7] == 'http://' or relative_url[0:8] == 'https://'):
        return relative_url
    return "http://%s%s" % (SITE.domain, relative_url)


def update_annotation(request, pk):
    """
    Update an annotation
    """
    annotation = Annotation.objects.get(id=request.GET.get('id'))
    if 'title' in request.GET:
        if (request.GET.get('title').strip()) == "":
            annotation.title = "Untitled"
        else:
            annotation.title = request.GET.get('title')
    if 'content' in request.GET:
        annotation.content = request.GET.get('content')
    annotation.save()
    return HttpResponse(
        simplejson.dumps({'status': 'ok'}), content_type="application/json")


def add_annotation(request, pk):
    """
    Add an annotation
    """
    document = Document.objects.get(pk=pk)
    annotation = Annotation(
        document=document, page=request.GET.get('page_id'))
    if 'title' in request.GET:
        if (request.GET.get('title').strip()) == "":
            annotation.title = "Untitled"
        else:
            annotation.title = request.GET.get('title')
    if 'content' in request.GET:
        annotation.content = request.GET.get('content')
    if 'location' in request.GET:
        annotation.location = request.GET.get('location')
    annotation.author = request.user
    annotation.save()
    return HttpResponse(
        simplejson.dumps({
            'status': 'ok',
            'url': document.get_absolute_url() + '#document/p' +
            str(document.pk) + '/a' + str(annotation.pk)}),
        content_type="application/json"
    )


def remove_annotation(request, pk):
    """
    Remove an annotation
    """

    annotation = Annotation.objects.get(id=request.GET.get('id'))

    annotation.delete()

    return HttpResponse(simplejson.dumps(
        {'status': 'ok'}), content_type="application/json")


from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
#@ensure_csrf_cookie
@csrf_exempt
def save_text(request, pk):
    """
    Save the text
    """
    document = Document.objects.get(id=pk)
    edition = Edition.objects.create(
        document=document,
        author=request.user,
        comment=request.POST.get('comment', ''),
        modified_pages={},
#        date=datetime.now(),
    )
    ts = edition.date
    date_string = datetime_to_string(ts)
    edition.date_string = date_string
    text_URI = request.POST.get('textURI', '')
    edition.modified_pages = edition.previous.modified_pages
    for k in request.POST:
        if k != 'comment' and k != 'textURI':
            num_page = int(k)
            page = document.pages_set.get(page=num_page)
            text = request.POST[k]
            page.modified = ts
            page.save_text(text, date_string)
            edition.modified_pages[k] = text_URI.replace(
                '{page}',
                '{}-{}'.format(k, datetime_to_string(ts))
            )
            page.save()
    
    nines = '9'*20
    last_edition = document.editions_set.get(date_string=nines)
    last_edition.modified_pages = edition.modified_pages
    
    edition.save()
    last_edition.save()
    
    document.regenerate()
    
    edit = {}
    edit['id'] = edition.id
    edit['date_string'] = edition.date_string
    edit['modified_pages'] = edition.modified_pages
    edit['comment'] = edition.comment
    edit['author'] = {'username': edition.author.username}
    edit['author__username'] = edition.author.username
    edit['date_string_formatted'] = format_datetime_string(edition.date_string)
    
    return HttpResponse(
        simplejson.dumps(
            {'status': 'ok', 'edition': edit}),
            content_type="application/json",
        )


#@ensure_csrf_cookie
@csrf_exempt
def restore_version(request, pk):
    """
    Restore a document version
    """
    nines = '9'*20
    ts = request.POST.get('ts', nines)
    document = Document.objects.get(id=pk)
    edition = document.editions_set.get(date_string=ts)
    return HttpResponse(
        simplejson.dumps(
            {'status': 'ok', 'id': edition.id, 'comment': edition.comment, 'modified_pages': edition.modified_pages}),
            content_type="application/json",
        )


#@ensure_csrf_cookie
@csrf_exempt
def delete_version(request, pk):
    """
    Delete a document version
    """
    ts = request.POST.get('ts')
    modified_pages = request.POST.getlist('modified_pages[]')
    document = Document.objects.get(id=pk)
    edition = document.editions_set.get(date_string=ts)
    edition_id = edition.id
    edition.delete(modified_pages=modified_pages)
    return HttpResponse(
        simplejson.dumps(
            {'status': 'ok', 'id': edition_id,}),
            content_type="application/json",
        )


class SearchDocumentView(View):

    def get(self, request, **kwargs):

        query = request.GET.get('q')

        results = SearchQuerySet().models(Page).narrow(
            'document_id:%s' % kwargs.get('pk')).auto_query(query)\
            .order_by('document_id')

        json = {
            'matches': results.count(),
            'results': [p.page for p in results],
            'query': query}

        return HttpResponse(simplejson.dumps(json), content_type="application/json")


class JsonDocumentView(BaseDetailView):

    model = Document

    def get(self, request, **kwargs):
        document = self.get_object()
        json = {}
        json['id'] = "doc-%s" % (document.id,)
        json['title'] = document.title
        json['pages'] = document.page_count
        json['description'] = document.description
        json['source'] = document.source_url
        json['created_at'] = rfc2822_date(document.created)
        json['updated_at'] = rfc2822_date(document.modified)
        json['canonical_url'] = get_absolute_url(reverse(
            "docviewer_viewer_view", kwargs={
            'pk': document.pk, 'slug': document.slug}))
        json['contributor'] = document.contributor
        json['contributor_organization'] = document.contributor_organization
        json['resources'] = {}
        if document.download is True:
            json['resources']['pdf'] = get_absolute_url(document.doc_url)
        json['resources']['text'] = get_absolute_url(document.text_url)
        json['resources']['thumbnail'] = get_absolute_url(document.thumbnail_url)
        json['resources']['search'] = get_absolute_url(
            reverse("docviewer_search_view", kwargs={
                'pk': document.pk, 'slug': document.slug})) + '?q={query}'
        json['resources']['print_annotations'] = get_absolute_url(
            reverse("docviewer_printannotations_view", kwargs={
                'pk': document.pk, 'slug': document.slug}))
        json['resources']['page'] = {}
        json['resources']['page']['text'] = get_absolute_url(
            document.text_page_url % {'page': '{page}'})
        json['resources']['page']['image'] = get_absolute_url(
            document.image_page_url % {'page': '{page}', 'size': '{size}'})
        json['resources']['related_article'] = get_absolute_url(document.related_url)
        json['resources']['published_url'] = json['canonical_url']

        json['sections'] = list(document.sections_set.all().values('title', 'page'))

        annotations_all = document.annotations_set.all()
#        annotations_public = annotations_all.exclude(Q(private=True)
#                                                 & ~Q(author=request.user))
#        json['annotations'] = list(annotations_public.values('location', 'title', 'id', 'page', 'content', 'author', 'author__username'))
        json['annotations'] = list(annotations_all.values('location', 'title', 'id', 'page', 'content', 'author', 'author__username'))

        for annotation in json['annotations']:
            annotation['location'] = {"image": annotation['location']}
            annotation['author'] = {'username': annotation['author__username']}

        zeros = '0'*20
        nines = '9'*20
        editions_all = document.editions_set.exclude(date_string=zeros).exclude(date_string=nines)
        json['editions'] = list(editions_all.values('id', 'date_string', 'modified_pages', 'comment', 'author', 'author__username'))

        for edition in json['editions']:
            edition['author'] = {'username': edition['author__username']}
            edition['date_string_formatted'] = format_datetime_string(edition['date_string'])

        return HttpResponse(simplejson.dumps(json), content_type="application/json")

