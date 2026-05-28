#coding:utf-8
__author__ = "ila"

import threading

_request = threading.local()

def get_current_request():
    return getattr(_request, 'request', None)

def set_current_request(request):
    _request.request = request
