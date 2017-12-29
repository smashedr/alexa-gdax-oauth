from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from login.models import TokenDatabase
import gdax
import logging

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
        if request.session['client_id'] != config.get('API', 'client_id'):
            raise ValueError('Inivalid client_id')
        if request.session['redirect_uri'] not in \
                config.get('API', 'redirect_uris').split(' '):
            logger.info(request.session['redirect_uri'])
            logger.info(config.get('API', 'redirect_uris').split(' '))
            raise ValueError('Inivalid redirect_uri')
        if request.session['response_type'] != 'code':
            raise ValueError('Inivalid response_type')
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

        td = TokenDatabase(
            key=_key,
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
        return redirect('success')

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
    return HttpResponse('OK')
