from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api.helpers import error_resp
from login.models import TokenDatabase
import gdax
import logging
import random
import string
import urllib.parse

logger = logging.getLogger('app')
config = settings.CONFIG


def has_success(request):
    """
    # View  /success
    # This is for debugging only
    # You will be redirected back to Alexa
    """
    return render(request, 'success.html')


def has_error(request):
    """
    # View  /error
    # This is for debugging only
    # Error handling does not yet exist
    """
    return render(request, 'error.html')


@require_http_methods(['GET'])
def do_connect(request):
    """
    # View  /connect
    """
    try:
        request.session['client_id'] = request.GET.get('client_id')
        request.session['redirect_uri'] = request.GET.get('redirect_uri')
        request.session['response_type'] = request.GET.get('response_type')
        request.session['state'] = request.GET.get('state')
        if request.session['client_id'] != config.get('API', 'client_id'):
            raise ValueError('Inivalid client_id')
        if request.session['redirect_uri'] not in \
                config.get('API', 'redirect_uris').split(' '):
            raise ValueError('Inivalid redirect_uri')
        if request.session['response_type'] != 'code':
            raise ValueError('Inivalid response_type')
        if not request.session['state']:
            raise ValueError('Inivalid state')
        return render(request, 'login.html')
    except Exception as error:
        logger.exception(error)
        messages.add_message(
            request, messages.WARNING,
            'Invalid Request.',
            extra_tags='danger',
        )
        return redirect('error')


@require_http_methods(['POST'])
def do_login(request):
    """
    # View  /authenticate
    """
    try:
        _key = request.POST.get('key')
        _password = request.POST.get('password')
        _secret = request.POST.get('secret')
        logger.info('post variables parsed')

        auth_client = gdax.AuthenticatedClient(_key, _secret, _password)
        gdax_accounts = auth_client.get_accounts()
        logger.info(gdax_accounts)

        if 'message' in gdax_accounts:
            messages.add_message(
                request, messages.WARNING,
                'Error: {}'.format(gdax_accounts['message']),
                extra_tags='danger',
            )
            return redirect('home')

        try:
            td = TokenDatabase.objects.get(key=_key)
            td.delete()
            logger.info('td.delete executed')
        except:
            pass

        code = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(20)
        )
        logger.info(code)
        td = TokenDatabase(
            key=_key,
            code=code,
            password=_password,
            secret=_secret,
        )
        td.save()
        logger.info('td.save executed')

        messages.add_message(
            request, messages.SUCCESS,
            'Successfully Authenticated GDAX.',
            extra_tags='success',
        )
        get_vars = {
            'code': code, 'state': request.session['state']
        }
        url = request.session['redirect_uri']
        return redirect(url + urllib.parse.urlencode(get_vars))

    except Exception as error:
        logger.exception(error)
        messages.add_message(
            request, messages.SUCCESS,
            'Error: {}'.format(error),
            extra_tags='danger',
        )
        return redirect('home')


@csrf_exempt
@require_http_methods(['POST'])
def get_token(request):
    try:
        _code = request.POST.get('code')
        _client_id = request.POST.get('client_id')
        _client_secret = request.POST.get('client_secret')

        logger.info('code: %s' % _code)
        logger.info('client_id: %s' % _client_id)
        logger.info('client_secret: %s' % _client_secret)

        if _client_id != config.get('API', 'client_id'):
            return JsonResponse(
                error_resp('invalid_client', 'ClientId is Invalid'),
                status=400, safe=False
            )

        if _client_secret != config.get('API', 'client_secret'):
            return JsonResponse(
                error_resp('invalid_secret', 'Secret is Invalid'),
                status=400, safe=False
            )

        try:
            if _code:
                td = TokenDatabase.objects.get(code=_code)
                key = td.key
            else:
                raise ValueError('code null')
        except Exception as error:
            logger.exception(error)
            return JsonResponse(
                error_resp('invalid_code', 'Code is Invalid'),
                status=400, safe=False
            )

        token_resp = {
            'access_token': key,
            'token_type': 'bearer',
        }
        logger.info(token_resp)
        return JsonResponse(token_resp)
    except Exception as error:
        logger.exception(error)
        return JsonResponse(
            error_resp('unknown_error', 'Unknown Error'),
            status=400, safe=False
        )
