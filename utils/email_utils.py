import json
from json.decoder import JSONDecodeError
from operator import itemgetter
import re
from django.shortcuts import render
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail as SendMail
from django.core.mail import EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string
from django.template.loader import get_template
from mail_tracking.models import MailTracking
from message.models import Message
from .smtp import SendMail as Smtp_SendMail
import locale
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from activity.models import Activity
from invoice.models import Invoice
from af_setup.models import AFSetup
from email_config.models import EmailConfig
from patient.retainer.models import Retainer
from trackingmore.models import Trackingmore
from utils.const_utils import DESCRIPTIONS_FOR_EACH_TYPE
from utils.member_utils import get_lab, get_member
from lib.loguru import logger
from threading import Lock
from patient.prescription.models import Prescription



EMAILING_ACTIVITY_TYPES = [
#   Activity.ACTIVITY_DENTIST_ADDED_PATIENT,
  Activity.ACTIVITY_DENTIST_STARTED_TREATMENT,
  Activity.ACTIVITY_DENTIST_SHPPED_FOOTPRINT,  
  Activity.ACTIVITY_DENTIST_SHIPPED_IMPRINT,
  Activity.ACTIVITY_DENTIST_REQUIRED_AF_SETUP,
  Activity.ACTIVITY_DENTIST_APPROVED_AF_SETUP,  
  Activity.ACTIVITY_DENTIST_REJECTED_AF_SETUP,
  Activity.ACTIVITY_DENTIST_RECEIVED_ALIGNERS,
  Activity.ACTIVITY_DENTIST_GENERATE_RETAINER,
  Activity.ACTIVITY_DENTIST_RQUIRED_RETAINER,
  Activity.ACTIVITY_DENTIST_RECEIVED_RETAINER,
  Activity.ACTIVITY_DENTIST_PAID_RETAINER,
  Activity.ACTIVITY_DENTIST_PAID,
  Activity.ACTIVITY_DENTIST_FINISHED_TREATMENT,
  Activity.ACTIVITY_LAB_APPROVED_PRESCRIPTION,
  Activity.ACTIVITY_LAB_REJECTED_PRESCRIPTION,
  Activity.ACTIVITY_LAB_SENT_AF_SETUP, #1
  Activity.ACTIVITY_LAB_SENT_ALIGNERS,
  Activity.ACTIVITY_LAB_SENT_INVOICE,
  Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION1,
  Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION2,
  Activity.ACTIVITY_LAB_SHIPPING_ALIGNERS,
  Activity.ACTIVITY_LAB_SHIPPED_ALIGNERS, #3
  Activity.ACTIVITY_LAB_DELIVERED_ALIGNERS, #4
  Activity.ACTIVITY_LAB_RECEIVED_RETAINER,
  Activity.ACTIVITY_LAB_SENT_RETAINER_INVOICE,
  Activity.ACTIVITY_LAB_APPROVED_RETAINER_IMPRINT,
  Activity.ACTIVITY_LAB_REJECTED_RETAINER_IMPRINT,
  Activity.ACTIVITY_LAB_SHIPPING_RETAINER,
  Activity.ACTIVITY_LAB_SHIPPED_RETAINER,
  Activity.ACTIVITY_LAB_DELIVERED_RETAINER,
  Activity.ACTIVITY_DENTIST_FINISHED_RETAINER,  
]

EMAILING_CREATED_CUSTOMER = [
    {
        'template': 'EMAIL_CREATED_CUSTOMER',
        'plan': 'EMAIL_CREATED_CUSTOMER_PLAIN',
    }
]

EMAILING_ACTIVITY_TEMPLATES = [
    {
        'template': 'EMAIL_ACTIVITY_MAIL_HTML',
        'plan': 'EMAIL_ACTIVITY_MAIL_PLAIN',
        'activity_types': [
            Activity.ACTIVITY_DENTIST_SHPPED_FOOTPRINT,  
            Activity.ACTIVITY_DENTIST_SHIPPED_IMPRINT,
            Activity.ACTIVITY_DENTIST_REQUIRED_AF_SETUP,
            Activity.ACTIVITY_DENTIST_RECEIVED_ALIGNERS,
            Activity.ACTIVITY_DENTIST_GENERATE_RETAINER,
            Activity.ACTIVITY_DENTIST_RQUIRED_RETAINER,
            Activity.ACTIVITY_DENTIST_RECEIVED_RETAINER,
            Activity.ACTIVITY_DENTIST_PAID_RETAINER,
            Activity.ACTIVITY_DENTIST_PAID,
            Activity.ACTIVITY_LAB_SENT_AF_SETUP,
            Activity.ACTIVITY_LAB_SENT_ALIGNERS,
            Activity.ACTIVITY_LAB_SENT_INVOICE,
            Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION1,
            Activity.ACTIVITY_LAB_SHIPPED_ALIGNERS,
            Activity.ACTIVITY_LAB_DELIVERED_ALIGNERS,
            Activity.ACTIVITY_LAB_RECEIVED_RETAINER,
            Activity.ACTIVITY_LAB_SENT_RETAINER_INVOICE,
            Activity.ACTIVITY_LAB_SHIPPED_RETAINER,
            Activity.ACTIVITY_LAB_DELIVERED_RETAINER,
        ] 
    },
    {
        'template': 'EMAIL_ACTIVITY_MAIL_HTML_1',
        'plan': 'EMAIL_ACTIVITY_MAIL_PLAIN_1',
        'activity_types': [
            Activity.ACTIVITY_DENTIST_STARTED_TREATMENT,
            Activity.ACTIVITY_LAB_APPROVED_PRESCRIPTION,
            Activity.ACTIVITY_LAB_REJECTED_PRESCRIPTION,
            Activity.ACTIVITY_DENTIST_APPROVED_AF_SETUP,
            Activity.ACTIVITY_DENTIST_REJECTED_AF_SETUP,
            Activity.ACTIVITY_LAB_APPROVED_RETAINER_IMPRINT,
            Activity.ACTIVITY_LAB_REJECTED_RETAINER_IMPRINT,
        ]
    },
    {
        'template': 'EMAIL_ACTIVITY_MAIL_HTML_2',
        'plan': 'EMAIL_ACTIVITY_MAIL_PLAIN_2',
        'activity_types': [
            "ACTIVITY_DENTIST_CREATE_PRESCRIPTION",
            "ACTIVITY_REFERENT_DENTIST_REJECTED_AF_SETUP",
            "ACTIVITY_REFERENT_DENTIST_3RD_REJECTED_AF_SETUP",
            "ACTIVITY_REFERENT_DENTIST_CREATE_TREATMENT"
        ]
    },
    {
        'template': 'EMAIL_ACTIVITY_SHIP_MAIL_HTML',
        'plan': 'EMAIL_ACTIVITY_SHIP_MAIL_PLAIN',
        'activity_types': [
            Activity.ACTIVITY_LAB_SHIPPING_ALIGNERS,
            Activity.ACTIVITY_LAB_SHIPPING_RETAINER,
        ]        
    },
    {
        'template': 'EMAIL_ACTIVITY_FINITION2_MAIL_HTML',
        'plan': 'EMAIL_ACTIVITY_MAIL_PLAIN',
        'activity_types': [
            Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION2,
        ] 
    },
    {
        'template': 'EMAIL_ACTIVITY_FINISHED_MAIL_HTML',
        'plan': 'EMAIL_ACTIVITY_MAIL_PLAIN',
        'activity_types': [
            Activity.ACTIVITY_DENTIST_FINISHED_TREATMENT,
            Activity.ACTIVITY_DENTIST_FINISHED_RETAINER,
        ] 
    },
]

class InvalidUserModel(Exception):
    """The member model you provided is invalid"""
    pass

class EmailTemplateNotFound(Exception):
    """No email template found"""
    pass

class NotAllFieldCompiled(Exception):
    """Compile all the fields in the settings"""
    pass

def my_functional_view(request, member):
    # send_email(member)
    return render('/email/verify/')

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

def get_member_password_email_context(member):
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    subject = _get_validated_field('EMAIL_PASSWORD_GENERATE_MAIL_SUBJECT')
    domain += '/' if not domain.endswith('/') else ''
    site_domain = urlparse(domain).netloc
    receiver_name = member.full_name()
    context = {
        'member': member,
        'subject': subject,
        'sender': sender,
        'receiver_name': receiver_name,
        'site_url': domain,
        'site_domain': site_domain
    }
    return context

send_email_member_password_lock = Lock()

def send_email_member_password(member, thread=True):
    with send_email_member_password_lock:
        mail_plain = _get_validated_field('EMAIL_PASSWORD_GENERATE_MAIL_PLAIN')
        mail_html = "../templates/" + _get_validated_field('EMAIL_PASSWORD_GENERATE_MAIL_HTML')
        context = get_member_password_email_context(member)

        args = (member, context['sender'], context['subject'], mail_plain, mail_html, context, "ACCOUNT CREATED")
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)

def get_invoice_pdf_file(activity):
    try:
        if (activity.activity_type == Activity.ACTIVITY_LAB_SENT_INVOICE) or \
           (activity.activity_type == Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION1) or \
           (activity.activity_type == Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION2) or \
           (activity.activity_type == Activity.ACTIVITY_LAB_SENT_RETAINER_INVOICE):
            if activity.meta_data:
                json_meta = json.loads(activity.meta_data)
                if ('data' in json_meta) and (json_meta['data']):
                    data = json_meta['data']
                    res = {
                        'title': '',
                        'file': '',
                        'image': ''
                    }
                    if 'pdf_file' in data:
                        res['title'] = data['title']
                    if 'pdf_file' in data:
                        res['file'] = data['pdf_file']
                    if 'pdf_image_file' in data:
                        res['image'] = data['pdf_image_file']
                    return res
    except JSONDecodeError as e:
        logger.error(f'Json Decode Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    except TypeError as e:
        logger.error(f'Json Data Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    return None

def get_finition_index(activity):
    try:
        if activity.activity_type == Activity.ACTIVITY_LAB_SENT_INVOICE_FINITION2:
            if activity.meta_data:
                json_meta = json.loads(activity.meta_data)
                if ('data' in json_meta) and (json_meta['data']):
                    data = json_meta['data']
                    if 'id' in data:
                        invoice_id = data['id']
                        invoice = Invoice.objects.filter(id=invoice_id).first()
                        if invoice and invoice.af_setup:
                            treatment = invoice.af_setup.treatment
                            if treatment.is_finition:
                                return treatment.finition_index
    except JSONDecodeError as e:
        logger.error(f'Json Decode Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    except TypeError as e:
        logger.error(f'Json Data Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    return 0

def get_shipment_carrier_link(activity):
    if activity.activity_type != Activity.ACTIVITY_LAB_SHIPPING_ALIGNERS and \
        activity.activity_type != Activity.ACTIVITY_LAB_SHIPPING_RETAINER:
        return None
    try:
        if activity.meta_data:
            json_meta = json.loads(activity.meta_data)
            if ('data' in json_meta) and (json_meta['data']):
                data = json_meta['data']
                if 'id' in data:
                    obj_id = data['id']
                    logger.debug(f"obj_id: {obj_id}, {activity.activity_type}")
                    tm = None
                    if activity.activity_type == Activity.ACTIVITY_LAB_SHIPPING_ALIGNERS:
                        afs = AFSetup.objects.filter(id=obj_id).first()
                        if afs is None:
                            logger.warning(f"Can't find af_setup #{obj_id} for the activity #{activity.id}")
                            return None
                        tm = Trackingmore.objects.filter(treatment=afs.treatment).first()
                    elif activity.activity_type == Activity.ACTIVITY_LAB_SHIPPING_RETAINER:
                        rt = Retainer.objects.filter(id=obj_id).first()
                        logger.debug(f"rt: {rt}")
                        if rt is None:
                            logger.warning(f"Can't find retainer #{obj_id} for the activity #{activity.id}")
                            return None
                        tm = Trackingmore.objects.filter(retainer=rt).first()
                    if (tm is None) or (tm.carrier is None):
                        logger.warning(f"Can't find a trackingmore for af_setup or retainer #{obj_id} on the activity #{activity.id}")
                        return None
                    logger.debug(f"tm: {tm}, {tm.carrier}, {Trackingmore.CARRIER_SERVICE_LINKS[tm.carrier]}")
                    return Trackingmore.CARRIER_SERVICE_LINKS[tm.carrier] if tm.carrier in Trackingmore.CARRIER_SERVICE_LINKS else None
    except JSONDecodeError as e:
        logger.error(f'Json Decode Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    except TypeError as e:
        logger.error(f'Json Data Error: {str(e)} on {e.__traceback__.tb_lineno} line')
    return None

def get_activity_email_context(activity):
    patient = activity.patient
    source = activity.source
    destination = activity.destination
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    patient_name = patient.full_name()
    patient_image = "https://aligneursfrancais.s3.eu-west-3.amazonaws.com/logos/email/utilisateur.png"
    receiver_name = destination.full_name()
    domain += '/' if not domain.endswith('/') else ''
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    if activity.activity_type == 'LAB_APPROVED_RETAINER_IMPRINT' or \
        activity.activity_type == 'LAB_REJECTED_RETAINER_IMPRINT':
        created_at = activity.created_at.strftime('%d/%m/%Y à %I:%M').rstrip()
    elif activity.activity_type == 'LAB_SHIPPING_RETAINER' or \
        activity.activity_type == 'LAB_DELIVERED_RETAINER':
        created_at = activity.created_at.strftime('%d %B, %Y à %I:%M').rstrip()
    else:
        created_at = activity.created_at.strftime('%d %B, %Y à %I:%M %p').rstrip()
    act_desc =  DESCRIPTIONS_FOR_EACH_TYPE[activity.activity_type]['fr']
    subject = 'Dr. ' + destination.last_name
    if 'email_subject' in act_desc:
        subject += ' ' + act_desc['email_subject']
    user_type = destination.type.lower()
    activity_link = f'{domain}{user_type}/patients/{patient.id}'
    attached_files = []
    pdf_file = get_invoice_pdf_file(activity)
    if pdf_file is not None:
        attached_files.append(pdf_file)
    finition_index = get_finition_index(activity)
    shipment_carrier_link = get_shipment_carrier_link(activity)
    context = {
        'activity': activity,
        'patient': patient,
        'dentist': patient.dentist,
        'site_url': domain,
        'destination': destination,
        'sender': sender,
        'subject': subject,
        'patient_name': patient_name,
        'patient_image': patient_image,
        'receiver_name': receiver_name,
        'act_desc': act_desc,
        'created_at': created_at,
        'user_type': user_type,
        'activity_link': activity_link,
        'attached_files': attached_files,
        'finition_index': finition_index,
        'shipment_carrier_link': shipment_carrier_link
    }
    return context

def get_activity_email_context_direct(activity, third_reject, isContainkit_balance,is_team_email=False):
    patient = activity.patient
    member = patient.dentist
    source = activity.source
    destination = activity.destination
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    patient_name = patient.full_name()
    patient_image = "https://aligneursfrancais.s3.eu-west-3.amazonaws.com/logos/email/utilisateur.png"
    receiver_name = 'Hi there'
    domain += '/' if not domain.endswith('/') else ''
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    if activity.activity_type == 'LAB_APPROVED_RETAINER_IMPRINT' or \
        activity.activity_type == 'LAB_REJECTED_RETAINER_IMPRINT':
        created_at = activity.created_at.strftime('%d/%m/%Y à %I:%M').rstrip()
    elif activity.activity_type == 'LAB_SHIPPING_RETAINER' or \
        activity.activity_type == 'LAB_DELIVERED_RETAINER':
        created_at = activity.created_at.strftime('%d %B, %Y à %I:%M').rstrip()
    else:
        created_at = activity.created_at.strftime('%d %B, %Y à %I:%M %p').rstrip()
    
    subject = 'Dr. ' + destination.last_name
    act_desc = None
    if is_team_email:
        receiver_name = 'Bonjour'
        dentist_name = f"{patient.dentist.first_name} {patient.dentist.last_name}"
        subject = f'AF Setup rejeté pour le Dr. {patient.dentist.first_name} {patient.dentist.last_name} – #{patient.id}'
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_REFERENT_DENTIST_REJECTED_AF_SETUP']['fr']
        act_desc = {key: value.replace('[DENTIST_NAME]', dentist_name) if isinstance(value, str) else value 
            for key, value in act_desc.items()}
    elif third_reject == True:
        receiver_name = f'Bonjour {member.referent.name}'
        dentist_name = f"{patient.dentist.first_name} {patient.dentist.last_name}"
        subject = f'AF Setup rejeté pour la 3ème fois pour le Dr. {patient.dentist.first_name} {patient.dentist.last_name}'
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_REFERENT_DENTIST_3RD_REJECTED_AF_SETUP']['fr']
        act_desc = {key: value.replace('[DENTIST_NAME]', dentist_name) if isinstance(value, str) else value 
            for key, value in act_desc.items()}
    elif activity.activity_type == Activity.ACTIVITY_DENTIST_REJECTED_AF_SETUP:
        receiver_name = f'Bonjour {member.referent.name}'
        dentist_name = f"{patient.dentist.first_name} {patient.dentist.last_name}"
        subject = f'AF Setup rejeté pour le Dr. {patient.dentist.first_name} {patient.dentist.last_name} – #{patient.id}'
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_REFERENT_DENTIST_REJECTED_AF_SETUP']['fr']
        act_desc = {key: value.replace('[DENTIST_NAME]', dentist_name) if isinstance(value, str) else value 
            for key, value in act_desc.items()}
    elif activity.activity_type == Activity.ACTIVITY_DENTIST_STARTED_TREATMENT:
        receiver_name = f'Bonjour {member.referent.name}'
        subject = f"Lancement d'un nouveau traitement pour le Dr. {patient.dentist.last_name} – #{patient.id}"
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_REFERENT_DENTIST_CREATE_TREATMENT']['fr']
    elif activity.activity_type == Activity.ACTIVITY_LAB_SENT_AF_SETUP:
        receiver_name = f'Bonjour {member.referent.name}'
        dentist_name = f"{patient.dentist.first_name} {patient.dentist.last_name}"
        subject = f"Un setup Aligneurs Français a été reçu pour le Dr. {patient.dentist.last_name} – #{patient.id}"
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_REFERENT_LAB_SENT_AF_SETUP']['fr']
        act_desc = {key: value.replace('[DENTIST_NAME]', dentist_name) if isinstance(value, str) else value 
            for key, value in act_desc.items()}
    elif isContainkit_balance:
        receiver_name = 'Bonjour Nathan'
        subject = f'Commande de kit de blanchiment – #{patient.id}'
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE['ACTIVITY_DENTIST_CREATE_PRESCRIPTION']['fr']
    else:
        act_desc = DESCRIPTIONS_FOR_EACH_TYPE[activity.activity_type]['fr']
        
    if 'email_subject' in act_desc:
        subject += ' ' + act_desc['email_subject']
    user_type = destination.type.lower()
    activity_link = f'{domain}{user_type}/patients/{patient.id}'
    attached_files = []
    pdf_file = get_invoice_pdf_file(activity)
    if pdf_file is not None:
        attached_files.append(pdf_file)
    finition_index = get_finition_index(activity)
    shipment_carrier_link = get_shipment_carrier_link(activity)
    context = {
        'activity': activity,
        'patient': patient,
        'dentist': patient.dentist,
        'site_url': domain,
        'destination': destination,
        'sender': sender,
        'subject': subject,
        'patient_name': patient_name,
        'patient_image': patient_image,
        'receiver_name': receiver_name,
        'act_desc': act_desc,
        'created_at': created_at,
        'user_type': user_type,
        'activity_link': activity_link,
        'attached_files': attached_files,
        'finition_index': finition_index,
        'shipment_carrier_link': shipment_carrier_link
    }
    return context

def get_email_activity_template(activity_type):
    for act_temp in EMAILING_ACTIVITY_TEMPLATES:
        if activity_type in act_temp['activity_types']:
            return {
                'template': act_temp['template'],
                'plan': act_temp['plan']
            }
    return None


def send_email_thread(member, sender, subject, mail_plain, mail_html, context, email_type):   
    text = render_to_string(mail_plain, context)
    html = render_to_string(mail_html, context)
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    try:
        Smtp_SendMail(subject, text, html, sender, member.email, password)
    except Exception as ex:
        logger.error(f'Failed to send email: id = {member.id}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
        return False
    logger.info(f'Sent an email successfully: member id = {member.id}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject=subject,
        content=text,
        recipient_email=member.email,
        mail_type=email_type,
        sending_date=datetime.now(),
    )
    return True

def send_email_thread_direct(member, sender, subject, mail_plain, mail_html, context, isContainkit_balance,activity, is_team_email=False):
    text = render_to_string(mail_plain, context)
    html = render_to_string(mail_html, context)
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    email_type = activity.activity_type
    patient = activity.patient

    # if member.referent == 'yasmine_ghedira':
    #     email = 'yasmineg@aligneursfrancais.com'
    # else:
    #     email = 'selim@aligneursfrancais.com'
    
    email_config = None
    email = None

    if is_team_email:
        email_config = EmailConfig.objects.filter(name="AF_SETUP_TEAM", af_setup_team = patient.af_setup_team).first()
        email_type = "AF_SETUP_TEAMS_EMAIL_ORDER_NOTIFICATION"
    else:
        if isContainkit_balance:
            email_config = EmailConfig.objects.filter(name="KIT_BLANC_ONE").first()
            email_type = "KIT_BLANC_ONE_ORDER_NOTIFICATION"
        elif member.referent:
            email_config = EmailConfig.objects.filter(name="REFERENT", referent=member.referent).first()

    email = email_config.email if email_config else None


    if email:
        try:
            Smtp_SendMail(subject, text, html, sender, email, password)
        except Exception as ex:
            logger.error(f'Failed to send email: id = {member.id}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
            return False
        
        logger.info(f'Sent an email successfully: member id = {member.id}')
        if is_html(text):
            text = extract_text_from_html(text)
        MailTracking.objects.create(
            subject=subject,
            content=text,
            recipient_email=email,
            mail_type=email_type,
            sending_date=datetime.now(),
        )
        return True
    else:
        logger.error(f'No email provided for member id = {member.id}')
        return False

def send_reminder_email_STL(patient, thread=True):
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    context = {
        'patient_name': patient.full_name().capitalize(),
    }
    subject = f"Empreintes manquantes - {patient.full_name().capitalize()}"
    mail_html = "../templates/" + _get_validated_field("EMAIL_REMINDER_STL_HTML")
    text = f"Sauf erreur de notre part, nous n’avons toujours pas reçu les STLs pour le patient : {patient.full_name().capitalize()}"
    
    args = (patient.dentist, sender, subject, text, mail_html, context)
    
    try:
        if thread:
            t = Thread(target=send_reminder_email_STL_thread, args=args)
            t.start()
        else:
            send_reminder_email_STL_thread(*args)

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return
    

def send_reminder_email_STL_thread(member, sender, subject, text, mail_html, context):
    html = render_to_string(mail_html, context)
    password = _get_validated_field('EMAIL_HOST_PASSWORD')

    try:
        Smtp_SendMail(subject, text, html, sender, member.email, password)
    except Exception as ex:
        logger.error(f'Failed to send email: id = {member.id}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
        return False
    logger.info(f'Sent an email successfully: member id = {member.id}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject=subject,
        content=text,
        recipient_email=member.email,
        mail_type="REMINDER STL",
        sending_date=datetime.now(),
    )
    return True

def send_email_activity(activity, thread=True):
    if not activity.activity_type in EMAILING_ACTIVITY_TYPES:
        # Skip emailing
        logger.warning(f'send_email_activity: skip emailing because the type is not in emailing list: {activity.activity_type}')
        return
    
    if activity.email_sent:
        logger.info(f'send_email_activity: email already sent for activity {activity.id}')
        return

    destination = activity.destination
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    context = get_activity_email_context(activity)
    subject = context['subject']
    email_template = get_email_activity_template(activity.activity_type)
    if email_template is None:
        return
    mail_plain = _get_validated_field(email_template['plan'])
    mail_html = "../templates/" + _get_validated_field(email_template['template'])

    args = (destination, sender, subject, mail_plain, mail_html, context, activity.activity_type)
    
    try:
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)

        activity.email_sent = True
        activity.save()
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return


def send_email_activity_direct(member, activity, third_reject, thread=True, isContainkit_balance=False, is_team_email=False):
    if not activity.activity_type in EMAILING_ACTIVITY_TYPES:
        # Skip emailing
        logger.warning(f'send_email_activity: skip emailing because the type is not in emailing list: {activity.activity_type}')
        return
		
	# if activity.email_sent:
    #     logger.info(f'send_email_activity: email already sent for activity {activity.id}')
    #     return

    destination = activity.destination
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    context = get_activity_email_context_direct(activity, third_reject, isContainkit_balance,is_team_email)
        
    subject = context['subject']

    
    if third_reject or isContainkit_balance or is_team_email or activity.activity_type in {
        Activity.ACTIVITY_LAB_SENT_AF_SETUP,
        Activity.ACTIVITY_DENTIST_REJECTED_AF_SETUP,
        Activity.ACTIVITY_DENTIST_STARTED_TREATMENT
    }:
        email_template = get_email_activity_template("ACTIVITY_DENTIST_CREATE_PRESCRIPTION")
    else:
        email_template = get_email_activity_template(activity.activity_type)


    if email_template is None:
        return
    mail_plain = _get_validated_field(email_template['plan'])
    mail_html = "../templates/" + _get_validated_field(email_template['template'])
    
    


    args = (member, sender, subject, mail_plain, mail_html, context, isContainkit_balance, activity, is_team_email)

    try:
        if thread:
            t = Thread(target=send_email_thread_direct, args=args)
            t.start()
        else:
            send_email_thread_direct(*args)

        activity.email_sent = True
        activity.save()
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return
    

def send_email_customer_created(client):
    # destination = "nicky.softimad@gmail.com"
    destination = "jane.b@aligneursfrancais.com"
    # destination = "eg@finmanagement.co"
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    context = {
        'client': client,
    }

    subject = 'Nouveau client ajouté'
    mail_html = "../templates/" + _get_validated_field("EMAIL_CREATED_CUSTOMER_HTML")
    html = render_to_string(mail_html, context)
    text = f"Le client {client} a été ajouté avec succès."
    
    try:
        Smtp_SendMail(subject, text, html, sender, destination, password)
    except Exception as ex:
        logger.error(f'Failed to send email: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
    logger.info(f'Sent an email successfully')
    MailTracking.objects.create(
        subject=subject,
        content=text,
        recipient_email=destination,
        mail_type="EMAIL CREATED CUSTOMER",
        sending_date=datetime.now(),
    )
        

def get_approved_afsetup_email_context(activity):
    patient = activity.patient
    destination = patient.dentist
    source = get_lab()
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    patient_name = patient.full_name()
    patient_image = "https://aligneursfrancais.s3.eu-west-3.amazonaws.com/logos/email/utilisateur.png"
    receiver_name = destination.last_name
    domain += '/' if not domain.endswith('/') else ''
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    created_at = activity.created_at.strftime('%d %B, %Y à %I:%M %p').rstrip()
    act_desc =  DESCRIPTIONS_FOR_EACH_TYPE[activity.activity_type]['fr']
    subject = 'Dr. ' + destination.last_name + ' vous avez approuvé votre setup'
    user_type = destination.type.lower()
    invoice_link = f'{domain}{user_type}/invoices'
    invoice_pdf_file = None
    try:
        # Get af_setup and invoice
        meta_data = json.loads(activity.meta_data)
        data = meta_data['data']
        af_setup_id = data['id']
        invoice = Invoice.objects.filter(af_setup_id=af_setup_id).first()
        if invoice:
            invoice_link = f'{domain}{user_type}/payment/{invoice.id}'
            # invoice_pdf_file = {
            #                 'title': f'invoice-{invoice.id}',
            #                 'file': invoice.pdf_file
            #             } 
    except Exception as e:
        logger.error(f'Failed to get invoice id. {e} on {e.__traceback__.tb_lineno} line')
    
    activity_link = f'{domain}{user_type}/patients/{patient.id}'
    attached_files = []
    pdf_file = get_invoice_pdf_file(activity)
    if pdf_file is not None:
        attached_files.append(pdf_file)
    if invoice_pdf_file is not None:
        attached_files.append(invoice_pdf_file)
    logger.debug(f'attached_files: {attached_files}')
    finition_index = get_finition_index(activity)
    context = {
        'activity': activity,
        'patient': patient,
        'dentist': patient.dentist,
        'site_url': domain,
        'destination': destination,
        'sender': sender,
        'subject': subject,
        'patient_name': patient_name,
        'patient_image': patient_image,
        'receiver_name': receiver_name,
        'act_desc': act_desc,
        'created_at': created_at,
        'user_type': user_type,
        'invoice_link': invoice_link,
        'activity_link': activity_link,
        'attached_files': attached_files,
        'finition_index': finition_index,
    }
    return context

send_approved_afsetup_email_lock = Lock()
def send_approved_afsetup_email(activity, thread=True):
    with send_approved_afsetup_email_lock:
        if activity.email_sent:
            logger.info(f'send_email_activity: email already sent for activity {activity.id}')
            return
        destination = activity.source
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')    
        context = get_approved_afsetup_email_context(activity)
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_ACTIVITY_APPROVED_AF_SETUP_MAIL_HTML',
            'plan': 'EMAIL_ACTIVITY_APPROVED_AF_SETUP_MAIL_PLAN'
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (destination, sender, subject, mail_plain, mail_html, context, activity.activity_type)
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)

        activity.email_sent = True
        activity.save()

def get_invoice_email_context(activity):
    patient = activity.patient
    destination = patient.dentist
    source = get_lab()
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    patient_name = patient.full_name()
    patient_image = "https://aligneursfrancais.s3.eu-west-3.amazonaws.com/logos/email/utilisateur.png"
    receiver_name = destination.last_name
    domain += '/' if not domain.endswith('/') else ''
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    created_at = activity.created_at.strftime('%d %B, %Y à %I:%M %p').rstrip()
    act_desc =  DESCRIPTIONS_FOR_EACH_TYPE[activity.activity_type]['fr']
    subject = 'Dr. ' + destination.last_name + ' vous avez approuvé votre setup'
    user_type = destination.type.lower()
    invoice_link = f'{domain}{user_type}/invoices'
    invoice_pdf_file = None
    try:
        meta_data = json.loads(activity.meta_data)
        data = meta_data['data']
        invoice_id = data['id']
        invoice_link = f'{domain}{user_type}/payment/{invoice_id}'            
    except Exception as e:
        logger.error(f'Failed to get invoice id. {e} on {e.__traceback__.tb_lineno} line')
    
    activity_link = f'{domain}{user_type}/patients/{patient.id}'
    attached_files = []
    pdf_file = get_invoice_pdf_file(activity)
    if pdf_file is not None:
        attached_files.append(pdf_file)
    if invoice_pdf_file is not None:
        attached_files.append(invoice_pdf_file)
    logger.debug(f'attached_files: {attached_files}')
    finition_index = get_finition_index(activity)
    context = {
        'activity': activity,
        'patient': patient,
        'dentist': patient.dentist,
        'site_url': domain,
        'destination': destination,
        'sender': sender,
        'subject': subject,
        'patient_name': patient_name,
        'patient_image': patient_image,
        'receiver_name': receiver_name,
        'act_desc': act_desc,
        'created_at': created_at,
        'user_type': user_type,
        'invoice_link': invoice_link,
        'activity_link': activity_link,
        'attached_files': attached_files,
        'finition_index': finition_index,
    }
    return context


send_invoice_email_lock = Lock()
def send_invoice_email(activity, thread=True):
    with send_invoice_email_lock:
        if activity.email_sent:
            logger.info(f'send_email_activity: email already sent for activity {activity.id}')
            return
        destination = activity.destination
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')    
        context = get_invoice_email_context(activity)
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_ACTIVITY_INVOICE_MAIL_HTML',
            'plan': 'EMAIL_ACTIVITY_INVOICE_MAIL_PLAN'
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (destination, sender, subject, mail_plain, mail_html, context, activity.activity_type)
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)
        
        activity.email_sent = True
        activity.save()

def get_invoice_30days_email_context(invoice):
    af_setup = invoice.af_setup
    treatment = af_setup.treatment
    dentist = treatment.dentist
    patient = treatment.patient
    destination = dentist
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    patient_name = patient.full_name()
    patient_image = "https://aligneursfrancais.s3.eu-west-3.amazonaws.com/logos/email/utilisateur.png"
    receiver_name = 'Bonjour Dr ' + destination.last_name
    domain += '/' if not domain.endswith('/') else ''
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    created_at = invoice.created_at.strftime('%d %B, %Y à %I:%M %p').rstrip()
    subject = 'Dr. ' + destination.last_name + " nous n'avons pas reçu le paiement de votre facture"
    attached_files = []
    pdf_file = invoice.pdf_file
    if pdf_file is not None:
        attached_files.append({
            'title': invoice.title,
            'file': invoice.pdf_file,
            'image': invoice.pdf_image_file
        })
    context = {
        'invoice': invoice,
        'patient': patient,
        'site_url': domain,
        'destination': destination,
        'sender': sender,
        'subject': subject,
        'patient_name': patient_name,
        'patient_image': patient_image,
        'receiver_name': receiver_name,
        'created_at': created_at,
        'attached_files': attached_files
    }
    return context

def get_invoice_30days_email_template(invoice):
    return {
        'template': _get_validated_field('EMAIL_INVOICE_30DAYS_MAIL_HTML'),
        'plan': _get_validated_field('EMAIL_INVOICE_30DAYS_MAIL_PLAIN')
    }

def need_to_send_email(invoice):
    INTERVAL_EMAILING_DAYS = 30
    created_at = invoice.created_at.replace(tzinfo=None)
    if created_at < datetime(year=2022, month=3, day=1):
        return False
    iss = list(map(itemgetter(0), Invoice.INVOICE_STATUS_CHOICE))
    if iss.index(invoice.status) >= iss.index(Invoice.PAID):
        return False
    if invoice.amount == 0:
        return False
    diff = datetime.today() - created_at
    if (diff.days >= INTERVAL_EMAILING_DAYS) and ((diff.days % INTERVAL_EMAILING_DAYS) == 0) :
        return True
    return False

send_invoice_30days_email_lock = Lock()
def send_invoice_30days_email(invoice, thread=True):
    with send_invoice_30days_email_lock:
        logger.info(f'Invoice ID: #{invoice.id}')
        if not need_to_send_email(invoice):
            logger.info(f"Skip to send invoice email for 30days because it's match to condition.")
            return False
        af_setup = invoice.af_setup
        treatment = af_setup.treatment
        dentist = treatment.dentist
        
        destination = dentist
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        context = get_invoice_30days_email_context(invoice)
        subject = context['subject']
        email_template = get_invoice_30days_email_template(invoice)
        if email_template is None:
            return False
        mail_plain = email_template['plan']
        mail_html = "../templates/" + email_template['template']
        args = (destination, sender, subject, mail_plain, mail_html, context, "INVOICE 30 DAYS")
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)
        return True

send_email_message_lock = Lock()
def send_email_message(message, thread=True):
    with send_email_message_lock:
        sender = message.sender
        receiver = message.receiver
        patient = message.conversation.patient
        from_email = _get_validated_field('EMAIL_FROM_ADDRESS')
        domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
        description = ''
        subject = sender.full_name() + ' sent '
        if message.type == Message.MESSAGE_TEXT:
            subject += ' a message.'
            mt = message.message_text
            if mt:
                description = mt.text
        else:
            subject += ' a file.'
            mfs = message.message_files
            for mf in mfs:
                description = mf.file + '\n'

        mail_plain = _get_validated_field('EMAIL_ACTIVITY_MAIL_PLAIN')
        mail_html = "../templates/" + _get_validated_field('EMAIL_MESSAGE_MAIL_HTML')

        domain += '/' if not domain.endswith('/') else ''
        created_at = message.created_at.strftime('%d %B, %Y %I:%M %p')
        
        context = {
            'activity': message,
            'patient': patient,
            'site_url': domain,
            'title': subject,
            'description': description,
            'created_at': created_at,
        }

        args = (receiver, from_email, 'Message', mail_plain, mail_html, context, "EMAIL MESSAGE")
        if thread:
            t = Thread(target=send_email_thread, args=args)
            t.start()
        else:
            send_email_thread(*args)

def get_contact_context(member, message):
    dentist_name = member.full_name()
    dentist_email = member.email
    context = {
        'member': member,
        'dentist_name': dentist_name, 
        'dentist_email': dentist_email,
        'message': message,
    }
    return context
    
send_email_contact_lock = Lock()
def send_email_contact(member, receiver, subject, message, thread=True):
    with send_email_contact_lock:
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        context = get_contact_context(member, message)
        subject = subject
        email_template = {
            'template': _get_validated_field('EMAIL_CONTACT_MAIL_HTML'),
            'plan': _get_validated_field('EMAIL_CONTACT_MAIL_PLAIN')
        }
        mail_plain = email_template['plan']
        mail_html = "../templates/" + email_template['template']
        args = (member, receiver, sender, subject, mail_plain, mail_html, context)
        if thread:
            t = Thread(target=send_contact_email_thread, args=args)
            t.start()
        else:
            send_contact_email_thread(*args)
        return True


def send_contact_email_thread(member, receiver, sender, subject, mail_plain, mail_html, context):   
    text = render_to_string(mail_plain, context)
    html = render_to_string(mail_html, context)
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    try:
        Smtp_SendMail(subject, text, html, sender, receiver, password)
    except Exception as ex:
        logger.error(f'Failed to send a contact email: id = {member.id}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
        return False
    logger.info(f'Sent a contact email successfully from member: member id = {member.id}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject=subject,
        content=text,
        recipient_email=receiver,
        mail_type="CONTACT EMAIL",
        sending_date=datetime.now(),
    )
    return True

send_email_csv_lock = Lock()
def send_email_csv(email_address, file_url, title='', thread=True):
    with send_email_csv_lock:
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        attached_files = [{
            'title': title,
            'file': file_url
        }]
        context = {
            'subject': f'Download the {title} csv file.',
            'message': f'We attached the {title} csv file. You can download it by clicking the linked file.',
            'attached_files': attached_files
        }
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_CSV_MAIL_HTML',
            'plan': 'EMAIL_CSV_MAIL_PLAN',
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (email_address, sender, subject, mail_plain, mail_html, context, "EMAIL CSV")
        if thread:
            t = Thread(target=raw_send_email_thread, args=args)
            t.start()
        else:
            raw_send_email_thread(*args)

send_email_refered_generate_promo_code_lock = Lock()
def send_email_refered_generate_promo_code(refered_dentist, referer_dentist, promo_code, title='', thread=True):
    with send_email_refered_generate_promo_code_lock:
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        attached_files = []
        subject = f"Profitez-en ! Vous avez reçu une réduction de -50%"
        message = f"""
            Bonjour Dr {refered_dentist.last_name}
            <br>
            <br>
            Le DR {referer_dentist.last_name} est désormais votre parrain Aligneurs Français. 
            <br>
            Vous pouvez désormais bénéficier de <b>-50%</b> sur l'un de vos prochains traitements. 
            <br>
            <br>
            Pour ce faire, il vous suffira d'entrer le code promotionnel ci-joint lors de l'ajout de votre patient : 
            <br>
            <br>
            <b>{promo_code}</b>
        """
        context = {
            'subject': subject,
            'message': message,
            'attached_files': attached_files
        }
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_REFERED_GENERATE_PROMO_CODE_MAIL_HTML',
            'plan': 'EMAIL_REFERED_GENERATE_PROMO_CODE_MAIL_PLAN',
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (refered_dentist.email, sender, subject, mail_plain, mail_html, context, "REFERRED GENERATE PROMO CODE")
        if thread:
            t = Thread(target=raw_send_email_thread, args=args)
            t.start()
        else:
            raw_send_email_thread(*args)

send_email_referer_first_email_lock = Lock()
def send_email_referer_first_email(refered_dentist, referer_dentist, title='', thread=True):
    with send_email_referer_first_email_lock:
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        attached_files = []
        subject = f"Bonjour Dr {referer_dentist.last_name}, merci d'avoir parrainé l'un de vos confrères !"
        message = f"""
            Bonjour Dr {referer_dentist.last_name}
            <br>
            <br>
            Le parrainage du DR {refered_dentist.last_name} a bien été noté par nos équipes. 
            <br>
            <br>
            Nous tenions à vous remercier pour votre soutient.
            <br> 
            Et pour ce faire, vous recevrez une <b>réduction de -50%</b> sur l'un de vos prochains traitements dès lors que le DR {refered_dentist.last_name} aura débuté son premier traitement. 
        """
        context = {
            'subject': subject,
            'message': message,
            'attached_files': attached_files
        }
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_REFERER_FIRST_MAIL_HTML',
            'plan': 'EMAIL_REFERER_FIRST_MAIL_PLAN',
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (referer_dentist.email, sender, subject, mail_plain, mail_html, context, "REFERER FIRST EMAIL")
        if thread:
            t = Thread(target=raw_send_email_thread, args=args)
            t.start()
        else:
            raw_send_email_thread(*args)

send_email_referer_second_email_lock = Lock()
def send_email_referer_second_email(refered_dentist, referer_dentist, promo_code, title='', thread=True):
    with send_email_referer_second_email_lock:
        sender = _get_validated_field('EMAIL_FROM_ADDRESS')
        attached_files = []
        subject = f"Bonjour Dr {referer_dentist.last_name}, merci d'avoir parrainé l'un de vos confrères !"
        message = f"""
            Bonjour Dr {referer_dentist.last_name}
            <br>
            <br>
            Le DR {refered_dentist.last_name} que vous avez parrainé il y a peu a commencé son premier traitement Aligneurs Français. 
            <br>
            <br>
            Vous pouvez désormais bénéficier de <b>-50%</b> sur l'un de vos prochains traitements. 
            <br>
            <br>
            Pour ce faire, il vous suffira d'entrer le code promotionnel ci-joint lors de l'ajout de votre patient :
            <br>
            <br>
            <b>{promo_code}</b> 
        """
        context = {
            'subject': subject,
            'message': message,
            'attached_files': attached_files
        }
        subject = context['subject']
        email_template = {
            'template': 'EMAIL_REFERER_SECOND_MAIL_HTML',
            'plan': 'EMAIL_REFERER_SECOND_MAIL_PLAN',
        }
        mail_plain = _get_validated_field(email_template['plan'])
        mail_html = "../templates/" + _get_validated_field(email_template['template'])
        args = (referer_dentist.email, sender, subject, mail_plain, mail_html, context, "REFERER SECOND EMAIL")
        if thread:
            t = Thread(target=raw_send_email_thread, args=args)
            t.start()
        else:
            raw_send_email_thread(*args)


def raw_send_email_thread(email_address, sender, subject, mail_plain, mail_html, context, email_type):   
    text = render_to_string(mail_plain, context)
    html = render_to_string(mail_html, context)
    password = _get_validated_field('EMAIL_HOST_PASSWORD')
    try:
        Smtp_SendMail(subject, text, html, sender, email_address, password)
    except Exception as ex:
        logger.error(f'Failed to send email: address = {email_address}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
        return False
    logger.info(f'Sent an email successfully: address = {email_address}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject=subject,
        content=text,
        recipient_email=email_address,
        mail_type=email_type,
        sending_date=datetime.now(),
    )
    return True


def dentist_promotion_email(dentist_profile, discount_percentage, remaining_treatments):
    template = get_template("dentist_promotion_mail_body.html")
    params = {
        "dentist_name": dentist_profile.dentist.full_name(),
        "dentist_status": dentist_profile.dentist_status,
        "discount": discount_percentage,
        "remaining_treatments": remaining_treatments
    }
    message = template.render(params)

    mail = EmailMessage(
        subject="Félicitations Dr " + dentist_profile.dentist.last_name + "! Vous avez atteint un nouveau statut Aligneurs Français",
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[dentist_profile.dentist.email, ],
        headers = {'Reply-To':  dentist_profile.dentist.email}
    )
    mail.content_subtype = "html"
    
    try:
        mail.send()
    except Exception as ex:
        logger.error(f'Failed to send email: address = {dentist_profile.dentist.email}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
    logger.info(f'Sent an email successfully: address = {dentist_profile.dentist.email}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject="Félicitations Dr " + dentist_profile.dentist.last_name + "! Vous avez atteint un nouveau statut Aligneurs Français",
        content=message,
        recipient_email=dentist_profile.dentist.email,
        mail_type="DENTIST PROMOTION",
        sending_date=datetime.now(),
    )


def dentist_demotion_email(dentist_profile):
    dentist = dentist_profile.dentist
    template = get_template("dentist_demotion_mail_body.html")
    params = {
        "dentist_name": dentist.full_name(),
    }
    message = template.render(params)

    mail = EmailMessage(
        subject="Bonjour Dr " + dentist.last_name + ", votre statut Aligneurs Français a changé..",
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[dentist.email, ],
        headers = {'Reply-To':  dentist.email}
    )
    mail.content_subtype = "html"

    try:
        mail.send()
    except Exception as ex:
        logger.error(f'Failed to send email: address = {dentist.email}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
    logger.info(f'Sent an email successfully: address = {dentist.email}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject="Bonjour Dr " + dentist.last_name + ", votre statut Aligneurs Français a changé..",
        content=message,
        recipient_email=dentist.email,
        mail_type="DENTIST DEMOTION",
        sending_date=datetime.now(),
    )


def dentist_remaining_treatment_email(dentist_profile):
    dentist = dentist_profile.dentist
    template = get_template("dentist_remaining_treatments_mail_body.html")
    params = {
        "dentist_name": dentist.full_name(),
    }
    message = template.render(params)

    mail = EmailMessage(
        subject="BONJOUR DR " + dentist.last_name + ", IL NE VOUS RESTE PLUS QU'UN TRAITEMENT AVANT LE PROCHAIN PALIER DE FIDÉLITÉ !",
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[dentist_profile.dentist.email, ],
        headers = {'Reply-To':  dentist.email}
    )
    mail.content_subtype = "html"
    mail.send()
    try:
        mail.send()
    except Exception as ex:
        logger.error(f'Failed to send email: address = {dentist_profile.dentist.email}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
    logger.info(f'Sent an email successfully: address = {dentist_profile.dentist.email}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject="BONJOUR DR " + dentist.last_name + ", IL NE VOUS RESTE PLUS QU'UN TRAITEMENT AVANT LE PROCHAIN PALIER DE FIDÉLITÉ !",
        content=message,
        recipient_email=dentist_profile.dentist.email,
        mail_type="DENTIST REMAINING TREATMENT",
        sending_date=datetime.now(),
    )


def get_af_setup_reminder_email_context(af_setup):
    treatment = af_setup.treatment
    patient = treatment.patient
    dentist = patient.dentist
    patient_name = patient.full_name()
    sender = _get_validated_field('EMAIL_FROM_ADDRESS')
    domain = _get_validated_field('EMAIL_PAGE_DOMAIN')
    domain += '/' if not domain.endswith('/') else ''
    user_type = 'dentist'
    patient_link = f'{domain}{user_type}/patients/{patient.id}'
    if treatment.is_finition:
        patient_link = f'{patient_link}/finition/{treatment.finition_index}'
    subject="Bonjour Dr " + dentist.last_name + ","
    created_at = af_setup.created_at.strftime('%d %B, %Y à %I:%M').rstrip()
    context = {
        "af_setup": af_setup,
        "patient": patient,
        "dentist": dentist,
        "sender": sender,
        "subject": subject,
        "patient_name": patient_name,
        "dentist_name": dentist.full_name(),
        "af_setup_name": af_setup.name,
        "patient_link": patient_link,
        "created_at": created_at
    }
    return context


def send_af_setup_reminder_email(af_setup, template_name):
    context = get_af_setup_reminder_email_context(af_setup)
    template = get_template(template_name)
    message = template.render(context)
    mail = EmailMessage(
        subject=context["subject"],
        body=message,
        from_email=context["sender"],
        to=[context["dentist"].email],
        headers={'Reply-To': context["dentist"].email}
    )
    mail.content_subtype = "html"
    
    try:
        mail.send()
    except Exception as ex:
        logger.error(f'Failed to send email: address = {context["dentist"].email}: {str(ex)} ({type(ex)}) on {ex.__traceback__.tb_lineno} line')
    logger.info(f'Sent an email successfully: address = {context["dentist"].email}')
    if is_html(text):
        text = extract_text_from_html(text)
    MailTracking.objects.create(
        subject=context["subject"],
        content=message,
        recipient_email=context["dentist"].email,
        mail_type="AF SETUP REMINDER",
        sending_date=datetime.now(),
    )


def send_af_setup_reminders():
    # Helper function for querying AFSetup records
    def get_af_setup_records(days_ago):
        target_date = datetime.now() - timedelta(days=days_ago)
        queries = Q(state=AFSetup.AF_SETUP_GENERATED) & Q(af_setup_date__date=target_date.date())
        return AFSetup.objects.filter(queries).all()

    # Send 1 week reminder emails
    # for raf in get_af_setup_records(7):  # 1 week is 7 days
    #     send_af_setup_reminder_email(raf, "af_setup_remainder_one_week.html")
    #     time.sleep(5)

    # Send 45 days reminder emails
    for raf in get_af_setup_records(45):
        send_af_setup_reminder_email(raf, "af_setup_remainder_45_days.html")
        time.sleep(5)
    
    return True

def is_html(content):
    return bool(re.search(r'<[^>]+>', content))

def extract_text_from_html(html_content):
    # Enlever les balises <style> et leur contenu
    html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL)
    
    # Enlever les balises <script> et leur contenu
    html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL)

    # Extraire le titre
    title_match = re.search(r'<title>(.*?)</title>', html_content)
    title = title_match.group(1) if title_match else ''

    # Supprimer la balise <title> du contenu HTML
    html_content = re.sub(r'<title>.*?</title>', '', html_content)

    # Extraire le contenu de la balise <body>
    body_match = re.search(r'<body.*?>(.*?)</body>', html_content, flags=re.DOTALL)
    body_content = body_match.group(1) if body_match else ''
    
    # Nettoyer le contenu du <body> en supprimant toutes les autres balises HTML
    body_cleaned = re.sub(r'<[^>]+>', ' ', body_content).strip()

    # Extraire tous les contenus des <div> (en incluant le contenu à l'intérieur)
    divs = re.findall(r'<div[^>]*>(.*?)</div>', html_content, flags=re.DOTALL)

    # Concaténer le titre + le contenu du <body> + chaque div avec un retour à la ligne après chaque
    extracted_text = f"{title}\n{body_cleaned}\n"

    return extracted_text