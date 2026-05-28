#coding:utf-8
__author__ = "ila"

import threading

_request = threading.local()

def get_current_request():
    return getattr(_request, 'request', None)

def set_current_request(request):
    _request.request = request

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        return response
