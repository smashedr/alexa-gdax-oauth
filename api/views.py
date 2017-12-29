from django.shortcuts import redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from login.models import TokenDatabase
import gdax
import logging

logger = logging.getLogger('app')


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
    try:
        _key = request.POST.get('key')
        _password = request.POST.get('password')
        _secret = request.POST.get('secret')
        logger.info('post variables parsed')

        # auth_client = gdax.AuthenticatedClient(_key, _secret, _password)
        # gdax_accounts = auth_client.get_accounts()
        # logger.info(gdax_accounts)
        return HttpResponse('OK')
    except Exception as error:
        logger.exception(error)
        return redirect('error')
