from functools import wraps

from django.shortcuts import render, HttpResponse

import firebase_admin
from firebase_admin import credentials, firestore


def FirestoreControlView(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        if not firebase_admin._apps:
            _credentials = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(_credentials)
        return func(request, firestore.client(), *args, **kwargs)
    return wrap


def SignInRequiredView(path):
    def wrapper(func):
        @wraps(func)
        def is_verify_request(request):
            return request.method == 'POST' and 'requestCode' in request.POST and request.POST['requestCode'] == 'verify_sign_in_user_request'

        def decorator(request, *args, **kwargs):
            print(kwargs)
            if is_verify_request(request):
                if request.POST['uid'] != '':
                    return func(request, *args, **kwargs)
                return HttpResponse('This page is accessible only signed in user.', status=500)

            pk = [str(value) + '/' if 'id' in key else None for key, value in kwargs.items()]
            pk = ''.join(pk) if pk else ''
            return render(request, 'verify.html', {'path': path + pk})
        return decorator
    return wrapper