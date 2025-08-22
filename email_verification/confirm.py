from threading import Thread
from typing import Callable

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail as SendMail
from django.template.loader import render_to_string
from django.urls import get_resolver
from django.utils import timezone

from .errors import InvalidUserModel, NotAllFieldCompiled
from .token import default_token_generator
from .smtp import SendMail as Smtp_SendMail

def send_email(member, thread=True, **kwargs):
    try:
        member.save()

        if kwargs.get('custom_salt'):
            default_token_generator.key_salt = kwargs['custom_salt']

        expiry_ = kwargs.get('expiry')
        token, expiry = default_token_generator.make_token(member, expiry_)

        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
        subject = _get_validated_field('EMAIL_MAIL_SUBJECT')
        mail_plain = _get_validated_field('EMAIL_MAIL_PLAIN')
        mail_html = _get_validated_field('EMAIL_MAIL_HTML')

        args = (member, token, expiry, sender, domain, subject, mail_plain, mail_html)
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)
    except AttributeError:
        raise InvalidUserModel('The member model you provided is invalid')


def send_email_thread(member, token, expiry, sender, domain, subject, mail_plain, mail_html, is_forget_password_request=False):
    domain += '/' if not domain.endswith('/') else ''
    from .views import verify
    link = ''
    for k, v in get_resolver(None).reverse_dict.items():
        if k is verify and v[0][0][1][0]:
            addr = str(v[0][0][0])
            if is_forget_password_request:
                link = settings.SITE_URL  + "/reset-password-form?token=" + token
            else:
                link = domain + addr[0: addr.index('%')] + token
    context = {'link': link, 'expiry': expiry, 'member': member}

    text = render_to_string(mail_plain, context)

    html = render_to_string(mail_html, context)

    # msg = EmailMultiAlternatives(subject, text, sender, [member.email])
    # msg.attach_alternative(html, 'text/html')
    # msg.send()
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    res = Smtp_SendMail(subject, text, html, sender, member.email, password)

def send_email_password_thread(member, token, expiry, sender, domain, subject, mail_plain, mail_html):
    domain += '/' if not domain.endswith('/') else ''

    from .views import verify
    addr = str('password/%(token)s')
    link = domain + addr[0: addr.index('%')] + token
    context = {'link': link, 'expiry': expiry, 'member': member}

    text = render_to_string(mail_plain, context)

    html = render_to_string(mail_html, context)

    # msg = EmailMultiAlternatives(subject, text, sender, [member.email])
    # msg.attach_alternative(html, 'text/html')
    # msg.send()
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    res = Smtp_SendMail(subject, text, html, sender, member.email, password)

def _get_validated_field(field, default_type=None):
    if default_type is None:
        default_type = str
    try:
        d = getattr(settings, field)
        if d == "" or d is None or not isinstance(d, default_type):
            raise AttributeError
        return d
    except AttributeError:
        raise NotAllFieldCompiled(f"Field {field} missing or invalid")


def verify_token(token):
    valid, member = default_token_generator.check_token(token)
    if valid:
        callback = _get_validated_field('EMAIL_VERIFIED_CALLBACK', default_type=Callable)
        callback(member)
        member.login_date = timezone.now()
        member.save()
        return valid, member
    return False, None


def send_email_password_reset(member, is_forget_password_request=False,thread=True, **kwargs):
    try:
        member.save()

        if kwargs.get('custom_salt'):
            default_token_generator.key_salt = kwargs['custom_salt']

        expiry_ = kwargs.get('expiry')
        token, expiry = default_token_generator.make_token(member, expiry_)

        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        domain = _get_validated_field('EMAIL_PAGE_DOMAIN') + 'forget_password/'
        subject = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_SUBJECT')
        mail_plain = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_PLAIN')
        mail_html = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_HTML')

        args = (member, token, expiry, sender, domain, subject, mail_plain, mail_html, is_forget_password_request)
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)
    except AttributeError:
        raise InvalidUserModel('The member model you provided is invalid')

def send_email_reset(member, new_email, thread=True, **kwargs):
    try:
        member.new_email = new_email
        member.save()

        if kwargs.get('custom_salt'):
            default_token_generator.key_salt = kwargs['custom_salt']

        expiry_ = kwargs.get('expiry')
        token, expiry = default_token_generator.make_token(member, expiry_)

        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        domain = _get_validated_field('EMAIL_PAGE_DOMAIN') + 'change_user_info/'
        subject = _get_validated_field('EMAIL_RESET_MAIL_SUBJECT')
        mail_plain = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_PLAIN')
        mail_html = "../templates/" + _get_validated_field('MAILADDRESS_RESET_MAIL_HTML')

        args = (member, token, expiry, sender, domain, subject, mail_plain, mail_html)
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)
    except AttributeError:
        raise InvalidUserModel('The member model you provided is invalid')

def send_password_reset(member, new_password, thread=True, **kwargs):
    try:
        member.new_password = new_password
        member.save()

        if kwargs.get('custom_salt'):
            default_token_generator.key_salt = kwargs['custom_salt']

        expiry_ = kwargs.get('expiry')
        token, expiry = default_token_generator.make_token(member, expiry_)

        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        domain = _get_validated_field('EMAIL_PAGE_DOMAIN') + 'change_user_info/'
        subject = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_SUBJECT')
        mail_plain = _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_PLAIN')
        mail_html = "../templates/" + _get_validated_field('EMAIL_PASSWORD_RESET_MAIL_HTML')

        args = (member, token, expiry, sender, domain, subject, mail_plain, mail_html)
        if thread:
            t = Thread(target=send_email_password_thread, args=args)
            t.start()
        else:
            send_email_password_thread(*args)
    except AttributeError:
        raise InvalidUserModel('The member model you provided is invalid')