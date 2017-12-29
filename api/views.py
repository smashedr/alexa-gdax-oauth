from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api.helpers import error_resp
from login.models import TokenDatabase
import gdax
import json
import logging

logger = logging.getLogger('app')
config = settings.CONFIG

def home(request):
    """
    # View  /api/
    """
    return HttpResponse('Online')


@csrf_exempt
@require_http_methods(['POST'])
def testing(request):
    """
    # View  /api/testing
    """
    log_req(request)
    try:
        _key = request.POST.get('key')
        _password = request.POST.get('password')
        _secret = request.POST.get('secret')
        _api_token = request.POST.get('api_token')
        logger.info('post variables parsed')

        if _api_token != config.get('API', 'api_token'):
            return JsonResponse(
                error_resp('invalid_api_token', 'API Token Invalid'),
                status=401,
            )

        if not _key or not _password or not _secret:
            return JsonResponse(
                error_resp('missing_credentials', 'API Credentials Missing'),
                status=401,
            )

        auth_client = gdax.AuthenticatedClient(_key, _secret, _password)
        gdax_accounts = auth_client.get_accounts()
        logger.info(type(gdax_accounts))
        logger.info(gdax_accounts)
        acct_dict = json.dumps(gdax_accounts)

        return JsonResponse(acct_dict)

    except Exception as error:
        logger.exception(error)
        return JsonResponse(
            error_resp('unknown_error', 'Unknown Error'), status=400, safe=False
        )


def log_req(request):
    """
    DEBUGGING ONLY
    """
    data = ''
    if request.method == 'GET':
        logger.debug('GET')
        for key, value in request.GET.items():
            data += '"%s": "%s", ' % (key, value)
    if request.method == 'POST':
        logger.debug('POST')
        for key, value in request.POST.items():
            data += '"%s": "%s", ' % (key, value)
    data = data.strip(', ')
    logger.debug(data)
    json_string = '{%s}' % data
    return json_string
