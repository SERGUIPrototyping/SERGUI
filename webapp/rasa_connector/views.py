# Create your views here.
import json
import logging

import requests
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def rasa(request):
    data = json.loads(request.body)
    if request.method == 'POST':
        url = 'http://localhost:5005/webhooks/rest/webhook'
        payload = {'sender': data['sender'],
                   'message': data['message']}
        try:
            response = requests.post(url=url, json=payload)
            response_data = json.loads(response.text)
            return JsonResponse(response_data, safe=False)
        except:
            return HttpResponse(status=500)
    return HttpResponseNotFound('<h1>Page not found</h1>')