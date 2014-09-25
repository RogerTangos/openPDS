#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
import logging, random, hashlib, string

urlpatterns = patterns('oms_pds.os_connector.views',
    (r'^upload$',                 'data'),
    (r'^register$',				'register'),
    (r'^config$',				'config'),

)
