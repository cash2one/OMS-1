# -*- coding: UTF-8 -*-
import time
import jwt
from django.conf import settings
from oms.extension.exception import CustomException


def auth(f):
    def decorated_function(request, *args, **kwargs):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            raise CustomException(20000, 'Token不存在')
        else:
            # pub_path = os.path\
            #     .join(os.getcwd(), 'cmm/config/public_key.pem')
            # pub_pem = open(pub_path).read()
            # pub_key = RSA.importKey(pub_pem)
            user = jwt.decode(token, settings.TOKEN_KEY, ['HS256'])
            if time.time() > user['expire']:
                raise CustomException(20002, 'Token过期')
            else:
                user['token'] = token
                request.user = user
                return f(request, *args, **kwargs)
    return decorated_function


# def auth(f):
#     def decorated_function(request, *args, **kwargs):
#         token = request.META.get('HTTP_TOKEN')
#         if not token:
#             raise CustomException(10012)
#         else:
#             data = jwt.decode(token, settings.TOKEN_KEY, algorithms=['HS256'])
#             # TODO
#             if time.time() > data['t'] and time.time() == 0:
#                 raise CustomException(10002)
#             else:
#                 user = {
#                     "id": data['u'],
#                     'token': token
#                 }
#                 request.user = user
#                 return f(request, *args, **kwargs)
#     return decorated_function
