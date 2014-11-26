from django.conf.urls.defaults import patterns
from docviewer.views import JsonDocumentView, SearchDocumentView
from django.views.generic import DetailView
from docviewer.models import Document
from django.contrib.auth.decorators import login_required


urlpatterns = patterns(
    '',
    (r'^doc-(?P<pk>\d+)\.json$', JsonDocumentView.as_view(), {}, "docviewer_json_view"),
    (r'^(?P<pk>\d+)/(?P<slug>.+)\.html$', login_required(DetailView.as_view(context_object_name='document', model=Document)), {}, "docviewer_viewer_view"),
    (r'^search/(?P<pk>\d+)/(?P<slug>.+)\.json$', SearchDocumentView.as_view(), {}, "docviewer_search_view"),
    (r'^print-annotations/(?P<pk>\d+)/(?P<slug>.+)\.html$', JsonDocumentView.as_view(), {}, "docviewer_printannotations_view"),
    (r'^(?P<pk>\d+)/update_annotation/$', 'docviewer.views.update_annotation', {}, "docviewer_annotation"),
    (r'^(?P<pk>\d+)/add_annotation/$', 'docviewer.views.add_annotation', {}, "docviewer_add_annotation"),
    (r'^(?P<pk>\d+)/remove_annotation/$', 'docviewer.views.remove_annotation', {}, "docviewer_remove_annotation"),
    (r'^(?P<pk>\d+)/save_text/$', 'docviewer.views.save_text', {}, 'docviewer_save_text'),
    (r'^(?P<pk>\d+)/save_specific_text/$', 'docviewer.views.save_specific_text', {}, 'docviewer_save_specific_text'),
    (r'^(?P<pk>\d+)/restore_version/$', 'docviewer.views.restore_version', {}, 'docviewer_restore_version'),
    (r'^(?P<pk>\d+)/delete_version/$', 'docviewer.views.delete_version', {}, 'docviewer_delete_version'),
    (r'^(?P<pk>\d+)/add_sharer/$', 'docviewer.views.add_sharer', {}, 'docviewer_add_sharer'),
    (r'^(?P<pk>\d+)/remove_sharer/$', 'docviewer.views.remove_sharer', {}, 'docviewer_remove_sharer'),
    (r'^(?P<pk>\d+)/add_taggit_tag/$', 'docviewer.views.add_taggit_tag', {}, 'docviewer_add_taggit_tag'),
    (r'^(?P<pk>\d+)/remove_taggit_tag/$', 'docviewer.views.remove_taggit_tag', {}, 'docviewer_remove_taggit_tag'),
    (r'^(?P<pk>\d+)/autocomplete_users/$', 'docviewer.views.autocomplete_users', {}, 'docviewer_autocomplete_users'),
    (r'^(?P<pk>\d+)/autocomplete_taggit_tags/$', 'docviewer.views.autocomplete_taggit_tags', {}, 'docviewer_autocomplete_taggit_tags'),
    (r'^(?P<pk>\d+)/change_visibility_page/$', 'docviewer.views.change_visibility_page', {}, "docviewer_change_visibility_page"),
    (r'^(?P<pk>\d+)/(?P<type>\w+)/regenerate_document/$', 'docviewer.views.regenerate_document', {}, "docviewer_regenerate_document"),
)
