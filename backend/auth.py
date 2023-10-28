import json
from flask import request
from functools import wraps
from urllib.request import urlopen
import jwt
from jwt import PyJWKClient
import os



AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
ALGORITHMS = ['RS256']
API_AUDIENCE = os.environ['AUTH0_AUDIENCE']

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    '''
        Gets jwt token from header's authorization value. Should be in 'bearer' + token format
    '''
    if 'Authorization' not in request.headers:
        raise AuthError('No authorization provided', 401)
    header_parts = request.headers['Authorization'].split(' ')
    if len(header_parts) != 2 or header_parts[0].lower() != 'bearer':
        raise AuthError('Malformed authorization header', 401)
    return header_parts[1]


def check_permissions(permission, payload):
    '''
    Determines if the jwt has a permissions section and that it contains a the specified permission
    Arguments
        permission -- (str) The permission key in the payload we want to verify.
        payload -- the decoded jwt
    '''
    if 'permissions' not in payload:
        raise AuthError('Permissions not included in JWT', 401)
    if permission not in payload['permissions'] and not payload['admin']:
        raise AuthError('Invalid claims', 403)
    return True

def verify_decode_jwt(token):
    '''
        Note to reviewer - I am using a work machine to do this course. I cannot install an earlier version of python and I kept getting errors using the jose package. I am not about to write a patch to get it to work with a new version so I ended up using PyJWKClient as part of the jwt package. It seriously much better, anyways.
        Arguments
            token -- user's jwt auth token
    '''
    url = f'{AUTH0_DOMAIN}.well-known/jwks.json'
    client = PyJWKClient(url)
    key = client.get_signing_key_from_jwt(token)
    payload = {}
    try:
        payload = jwt.decode(jwt=token, key=key.key, verify=True, algorithms=ALGORITHMS, audience=API_AUDIENCE, issuer=AUTH0_DOMAIN)
        payload['user_id'] = payload['sub'].split('|')[1]
        payload['admin'] = 'admin' in payload['permissions']
    except:
        raise AuthError('Token expired or could not be verified', 401)
    finally:
        return payload

def requires_auth(permission=''):
    '''
    Decorator to decode jwt and verify user access to an endpoint
    Arguments
        permission -- (str) The permission key in the payload we want to verify.
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator