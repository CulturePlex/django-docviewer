import documents

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.detail import BaseDetailView
from django.core.urlresolvers import reverse
from docviewer.models import Document, Page, Annotation, Edition
from django.utils.feedgenerator import rfc2822_date
from django.http import HttpResponse
#from django.utils import simplejson
import json
from django.contrib.sites.models import Site
from django.views.generic.base import View
from django.conf import settings
from haystack.query import SearchQuerySet

from datetime import datetime
from utils import datetime_to_string, format_datetime_string, format_datetime_from_stringts, check_mentions
from django.conf import settings


zeros = '0'*20
nines = '9'*20


def get_absolute_url(relative_url):
    SITE = Site.objects.get_current()
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
        json.dumps({'status': 'ok'}), content_type="application/json")


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
    
    check_mentions(annotation.content, annotation.author.username, document)
    
    return HttpResponse(
        json.dumps({
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

    return HttpResponse(json.dumps(
        {'status': 'ok'}), content_type="application/json")


from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
#@ensure_csrf_cookie
@csrf_exempt
def save_specific_text(request, pk):
    """
    Save the specific text
    """
    document = Document.objects.get(id=pk)
    ts=request.POST['ts']
    edition = document.editions_set.get(date_string=ts)
#    formated_ts = format_datetime_from_stringts(ts)
    aux = {}
    for k in edition.modified_pages:
        aux[int(k)] = edition.modified_pages[k]
    files = map(lambda x: x.split('/')[-1], aux.values())
    document.regenerate_ts(ts, files)
    
    return HttpResponse(
        json.dumps(
            {'status': 'ok',}),
            content_type="application/json",
        )
#@ensure_csrf_cookie
@csrf_exempt
def save_text(request, pk):
    """
    Save the text
    """
    document = Document.objects.get(id=pk)
    author = request.user
    comment = request.POST.get('comment', '')
    edition = Edition.objects.create(
        document=document,
        author=author,
        comment=comment,
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
    
#    last_edition = document.editions_set.get(date_string=nines)
#    last_edition.modified_pages = edition.modified_pages
    
    edition.save()
#    last_edition.save()
    
    document.regenerate()
    
    edit = {}
    edit['id'] = edition.id
    edit['date_string'] = edition.date_string
    edit['modified_pages'] = edition.modified_pages
    edit['comment'] = edition.comment
    edit['author'] = {'username': edition.author.username}
    edit['author__username'] = edition.author.username
    edit['date_string_formatted'] = format_datetime_string(edition.date_string)
    edit['user_url'] = settings.USER_URL + edition.author.username
    
    check_mentions(comment, author.username, document)
    
    return HttpResponse(
        json.dumps(
            {'status': 'ok', 'edition': edit}),
            content_type="application/json",
        )


#@ensure_csrf_cookie
@csrf_exempt
def restore_version(request, pk):
    """
    Restore a document version
    """
    ts = request.POST.get('ts', nines)
    document = Document.objects.get(id=pk)
    edition = document.editions_set.get(date_string=ts)
    return HttpResponse(
        json.dumps(
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
        json.dumps(
            {'status': 'ok', 'id': edition_id,}),
            content_type="application/json",
        )


@csrf_exempt
def add_sharer(request, pk):
    """ Add a user that shares the document """
    post_copy = request.POST.copy()
    post_copy['doc_id'] = pk
    request.POST = post_copy
    return documents.views.add_sharer(request)


@csrf_exempt
def remove_sharer(request, pk):
    """ Removes a user that shares the document """
    post_copy = request.POST.copy()
    post_copy['doc_id'] = pk
    request.POST = post_copy
    return documents.views.remove_sharer(request)


@csrf_exempt
def add_taggit_tag(request, pk):
    """ Add a taggit_tag to the document """
    post_copy = request.POST.copy()
    post_copy['doc_id'] = pk
    request.POST = post_copy
    return documents.views.add_taggit_tag(request)


@csrf_exempt
def remove_taggit_tag(request, pk):
    """ Removes a taggit_tag from the document """
    post_copy = request.POST.copy()
    post_copy['doc_id'] = pk
    request.POST = post_copy
    return documents.views.remove_taggit_tag(request)


@csrf_exempt
def autocomplete_users(request, pk):
    """ Autocomplete for adding sharers """
    return documents.views.autocomplete_users(request, pk)


@csrf_exempt
def autocomplete_taggit_tags(request, pk):
    """ Autocomplete for adding taggit_tags """
    return documents.views.autocomplete_taggit_tags(request, pk)


@csrf_exempt
def change_visibility_page(request, pk):
    """ Change the visibility of a page """
    page_n = request.POST['page']
    doc = documents.models.Document.objects.get(pk=pk)
    page = doc.pages_set.get(page=page_n)
    page.visible = not page.visible
    page.save()

    return HttpResponse(
        json.dumps({'status': 'ok', 'page': page_n}),
        content_type="application/json"
    )


@csrf_exempt
def regenerate_document(request, pk, type):
    """ Regenerate a document based on its visible pages """
    doc = documents.models.Document.objects.get(pk=pk)
    txt, pdf = doc.generate_visible()
    if type == 'txt':
        result = txt
    else: # typ == 'pdf'
        result = pdf

    return HttpResponseRedirect(
        result,
#        content_type="plain/text"
    )


class SearchDocumentView(View):

    def get(self, request, **kwargs):

        query = request.GET.get('q')

        results = SearchQuerySet().models(Page).narrow(
            'document_id:%s' % kwargs.get('pk')).auto_query(query)\
            .order_by('document_id')

        myjson = {
            'matches': results.count(),
            'results': [p.page for p in results],
            'query': query}

        return HttpResponse(json.dumps(myjson), content_type="application/json")


class JsonDocumentView(BaseDetailView):

    model = Document

    def get(self, request, **kwargs):
        document = self.get_object()
        myjson = {}
        myjson['id'] = "doc-%s" % (document.id,)
        myjson['title'] = document.title
        myjson['pages'] = document.page_count
        myjson['description'] = document.description
        myjson['source'] = document.source_url
        myjson['created_at'] = rfc2822_date(document.created)
        myjson['updated_at'] = rfc2822_date(document.modified)
        myjson['canonical_url'] = get_absolute_url(reverse(
            "docviewer_viewer_view", kwargs={
            'pk': document.pk, 'slug': document.slug}))
        myjson['contributor'] = document.contributor
        myjson['contributor_organization'] = document.contributor_organization
        myjson['resources'] = {}
        if document.download is True:
            myjson['resources']['pdf'] = get_absolute_url(document.doc_url)
        myjson['resources']['text'] = get_absolute_url(document.text_url)
        myjson['resources']['thumbnail'] = get_absolute_url(document.thumbnail_url)
        myjson['resources']['search'] = get_absolute_url(
            reverse("docviewer_search_view", kwargs={
                'pk': document.pk, 'slug': document.slug})) + '?q={query}'
        myjson['resources']['print_annotations'] = get_absolute_url(
            reverse("docviewer_printannotations_view", kwargs={
                'pk': document.pk, 'slug': document.slug}))
        myjson['resources']['page'] = {}
        myjson['resources']['page']['text'] = get_absolute_url(
            document.text_page_url % {'page': '{page}'})
        myjson['resources']['page']['image'] = get_absolute_url(
            document.image_page_url % {'page': '{page}', 'size': '{size}'})
        myjson['resources']['related_article'] = get_absolute_url(document.related_url)
        myjson['resources']['published_url'] = myjson['canonical_url']
        myjson['resources']['collaborators'] = map(lambda x: x.username, document.document.get_users_with_perms())
        myjson['resources']['tags'] = map(lambda x: x, document.document.taggit_tags.names())
        myjson['resources']['doc_id'] = document.id
        myjson['resources']['static_url'] = settings.STATIC_URL
        myjson['resources']['add_tag_url'] = 'TODO'
        myjson['resources']['remove_tag_url'] = reverse('remove_taggit_tag')
        myjson['resources']['add_collaborator_url'] = 'TODO'
        myjson['resources']['remove_collaborator_url'] = reverse('remove_sharer')
        myjson['resources']['pdf_visible'] = reverse(
            'docviewer_regenerate_document',
            kwargs={'pk': document.pk, 'type': 'pdf'}
        )
        myjson['resources']['txt_visible'] = reverse(
            'docviewer_regenerate_document',
            kwargs={'pk': document.pk, 'type': 'txt'}
        )

        myjson['sections'] = list(document.sections_set.all().values('title', 'page'))
        
        myjson['hidden_pages'] = document.get_hidden_pages()

        annotations_all = document.annotations_set.all()
#        annotations_public = annotations_all.exclude(Q(private=True)
#                                                 & ~Q(author=request.user))
#        myjson['annotations'] = list(annotations_public.values('location', 'title', 'id', 'page', 'content', 'author', 'author__username'))
        myjson['annotations'] = list(annotations_all.values('location', 'title', 'id', 'page', 'content', 'author', 'author__username'))

        for annotation in myjson['annotations']:
            annotation['location'] = {"image": annotation['location']}
            annotation['author'] = {'username': annotation['author__username']}
            annotation['user_url'] = settings.USER_URL + annotation['author__username']

        editions_all = document.editions_set.exclude(date_string=zeros).exclude(date_string=nines)
        myjson['editions'] = list(editions_all.values('id', 'date_string', 'modified_pages', 'comment', 'author', 'author__username'))

        for edition in myjson['editions']:
            edition['author'] = {'username': edition['author__username']}
            edition['date_string_formatted'] = format_datetime_string(edition['date_string'])
            edition['user_url'] = settings.USER_URL + edition['author__username']

        return HttpResponse(json.dumps(myjson), content_type="application/myjson")

