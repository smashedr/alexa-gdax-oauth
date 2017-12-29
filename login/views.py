from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from login.models import TokenDatabase
import gdax
import logging

logger = logging.getLogger('app')


def home(request):
    """
    # View  /
    """
    return render(request, 'login.html')


def success(request):
    """
    # View  /success
    # This is for debugging only
    # You will be redirected back to Alexa
    """
    return render(request, 'success.html')


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
