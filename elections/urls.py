from django.conf import settings
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from haystack.views import SearchView
from elections.forms import ElectionForm
from django.views.generic import DetailView
from elections.views import ElectionsSearchByTagView, HomeView, ElectionDetailView,\
							CandidateDetailView, SoulMateDetailView, ElectionAskCreateView,\
							AnswerWebHook, ElectionRankingView, QuestionsPerCandidateView, MessageDetailView, FaceToFaceView
from elections.models import VotaInteligenteMessage
from sitemaps import *

from django.conf import settings
from django.views.decorators.cache import cache_page

media_root = getattr(settings, 'MEDIA_ROOT', '/') 

new_answer_endpoint = r"^new_answer/%s/?$" % (settings.NEW_ANSWER_ENDPOINT)

sitemaps = {
    'elections': ElectionsSitemap,
    'candidates': CandidatesSitemap,
}

urlpatterns = patterns('',
	url(new_answer_endpoint,AnswerWebHook.as_view(), name='new_answer_endpoint' ),
	url(r'^/?$', cache_page(HomeView.as_view(template_name='elections/home.html'), 60 * settings.CACHE_MINUTES), name='home' ),
	url(r'^buscar/?$', SearchView(
	        template='search.html',
	        form_class=ElectionForm
	    ), name='search' ),
	url(r'^busqueda_tags/?$', ElectionsSearchByTagView.as_view(), name='tags_search' ),
	url(r'^election/(?P<slug>[-\w]+)/?$', 
		cache_page(ElectionDetailView.as_view(template_name='elections/election_detail.html'), 60 * settings.CACHE_MINUTES),
		name='election_view' ),
	url(r'^election/(?P<slug>[-\w]+)/questionary/?$',
		cache_page(ElectionDetailView.as_view(template_name='elections/election_questionary.html'), 60 * settings.CACHE_MINUTES), 
		name='questionary_detail_view'),
	#compare two candidates
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/(?P<slug_candidate_two>[-\w]+)/?$',
		cache_page(FaceToFaceView.as_view(template_name='elections/compare_candidates.html'), 60 * settings.CACHE_MINUTES),
		name='face_to_face_two_candidates_detail_view'),
	#one candidate for compare
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/(?P<slug_candidate_one>[-\w]+)/?$',
		cache_page(ElectionDetailView.as_view(template_name='elections/compare_candidates.html'), 60 * settings.CACHE_MINUTES),
		name='face_to_face_one_candidate_detail_view'),
	#no one candidate
	url(r'^election/(?P<slug>[-\w]+)/face-to-face/?$',
		cache_page(ElectionDetailView.as_view(template_name='elections/compare_candidates.html'), 60 * settings.CACHE_MINUTES),
		name='face_to_face_no_candidate_detail_view'),
	#soulmate
	url(r'^election/(?P<slug>[-\w]+)/soul-mate/?$',
		SoulMateDetailView.as_view(template_name='elections/soulmate_candidate.html'),
		name='soul_mate_detail_view'),
	#ask
	url(r'^election/(?P<slug>[-\w]+)/ask/?$',
		ElectionAskCreateView.as_view(template_name='elections/ask_candidate.html'), 
		name='ask_detail_view'),
	#ranking
	url(r'^election/(?P<slug>[-\w]+)/ranking/?$',
		cache_page(ElectionRankingView.as_view(template_name='elections/ranking_candidates.html'), 60 * settings.CACHE_MINUTES),
		name='ranking_detail_view'),
	#message_detail
	url(r'^election/(?P<election_slug>[-\w]+)/messages/(?P<pk>\d+)/?$',
		MessageDetailView.as_view(template_name='elections/message_detail.html'), 
		name='message_detail'),
	url(r'^election/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/?$', 
		cache_page(CandidateDetailView.as_view(template_name='elections/candidate_detail.html'), 60 * settings.CACHE_MINUTES),
		name='candidate_detail_view'
		),
	url(r'^election/(?P<election_slug>[-\w]+)/(?P<slug>[-\w]+)/questions?$', 
		QuestionsPerCandidateView.as_view(template_name='elections/questions_per_candidate.html'),
		name='questions_per_candidate'
		),
	url(r'^election/(?P<slug>[-\w]+)/extra_info.html$',
		ElectionDetailView.as_view(template_name='elections/extra_info.html'), 
		name='election_extra_info'),
	
	url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

urlpatterns += patterns('', 
	url(r'^cache/(?P<path>.*)$','django.views.static.serve',
    	{'document_root': media_root})
)