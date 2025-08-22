from django.conf import settings
from django.shortcuts import render

from .confirm import verify_token
from .errors import NotAllFieldCompiled

def verify(request, token):
    try:
        template = settings.EMAIL_PAGE_TEMPLATE
        if not isinstance(template, str):
            raise AttributeError
        success, member = verify_token(token)
        return render(request, template, {'success': success, 'member': member, 'request': request})
    except AttributeError:
        raise NotAllFieldCompiled('EMAIL_PAGE_TEMPLATE field not found')


def verify_password_reset(request, token):
    try:
        template = settings.PASSWORD_RESET_CONFIRM_TEMPLATE
        if not isinstance(template, str):
            raise AttributeError
        success, member = verify_token(token)
        return render(request, template, {'success': success, 'member': member, 'request': request})
    except AttributeError:
        raise NotAllFieldCompiled('EMAIL_PAGE_TEMPLATE field not found')

def verify_mailladdress_reset(request, token):
    try:
        template = settings.MAIL_RESET_CONFIRM_TEMPLATE
        if not isinstance(template, str):
            raise AttributeError
        success, member = verify_token(token)
        return render(request, template, {'success': success, 'member': member, 'request': request})
    except AttributeError:
        raise NotAllFieldCompiled('EMAIL_PAGE_TEMPLATE field not found')


def confirm_password_reset(request, member):
    template = settings.PASSWORD_RESET_COMPLETE_TEMPLATE
    return render(request, template, {'success': True, 'member': member, 'request': request})

def complete_password_reset(request, member):
    template = settings.PASSWORD_RESET_COMPLETE_TEMPLATE
    return render(request, template, {'member': member, 'request': request})

def confirm_email_reset(request, member):
    template = settings.MAILADDRESS_RESET_COMPLETE_TEMPLATE
    return render(request, template, {'success': True, 'member': member, 'request': request})

def complete_email_reset(request, member):
    template = settings.MAILADDRESS_RESET_COMPLETE_TEMPLATE
    return render(request, template, {'member': member, 'request': request})