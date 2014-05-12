from django.conf.urls import patterns, include, url
from mobikwik_wallet_python_kit import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('',
      url(r'^$', views.index, name='index'),
      url(r'^posttomobikwik/$', csrf_exempt(views.posttomobikwik), name='posttomobikwik'),
      url(r'^mobikwik_wallet_response/$', csrf_exempt(views.mobikwik_wallet_response), name='mobikwikwalletresponse'),
)
