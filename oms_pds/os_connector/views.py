#-*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseBadRequest
import os
import json
import random
import normalize
from oms_pds import settings
from oms_pds.authorization import PDSAuthorization
from oms_pds.pds.models import Profile
from oms_pds.pds.internal import getInternalDataStore

# import pdb


def insert_pds(internalDataStore, token, pds_json):
    internalDataStore.saveData(pds_json)


def data(request):
    '''parse json data and upload them to your PDS'''
    if request.method == 'GET':
        return HttpResponseBadRequest("GET requests disallowed", content_type = 'text/json')

    # get necessary info from outside request
    device_id = request.POST['device_id']
    # flie_hash = request.POST['file_hash']
    token = request.POST['bearer_token']
    data = json.loads(request.POST['data'])
    result = {}

    # use token to authorize writing to the PDS
    authorization = PDSAuthorization("ios_write", audit_enabled=True)
    if (not authorization.is_authorized(request)):
        print "authorization not received"
        return HttpResponse("Unauthorized", status=401)

    # Get the relevant internal data store
    datastore_owner, ds_owner_created = Profile.objects.get_or_create(uuid = device_id)
    internalDataStore = getInternalDataStore(datastore_owner, "Living Lab", "Social Health Tracker", token)

    # write to the datastore
    result = extractAndInsertData(data, internalDataStore, token)

    # let the client know what happened    
    print result
    if result.get('status'):
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponseBadRequest(json.dumps(result), \
            content_type='application/json')


def extractAndInsertData(data, internalDataStore, token):
    result = {}
    print '\n======================\nextractAndInsertData:'
    print data
    print '\n======================\n'
    
    try:
        for json_object in data:
            insert_pds(internalDataStore, token, json_object)
        result = {'status':'ok', 'entries_inserted':len(data)}
    except Exception as e:
        print "\n\nException from os_connector on pds: %s\n" %e
        result = {'success':False, 'error_message':e.message}
    return result


def register(request):
    ''' register a device using the open-sense library'''
    data = request.POST

    if not data.get('datastore_owner__uuid'):
        responseData = {'error': 'Missing datastore_owner__uuid parameter'} 
        return HttpResponseBadRequest(json.dumps(data), content_type='application/json')

    else:
        key = generateKey()
        responseData = {'key': key}
        return HttpResponse(json.dumps(responseData), content_type = 'application/json')


def config(request):
    '''send the config file to open-sense, if it is requested'''
    response = open(os.path.join(settings.STATIC_ROOT, 'img/opensense/config.json')).read()
    return HttpResponse(json.dumps(response), content_type = 'application/json')


def generateKey():
    validCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%'

    sr = random.SystemRandom()
    key = ''

    for i in range(0, 40):
        index = sr.randint(0, 40)
        key += validCharacters[index]

    return key
