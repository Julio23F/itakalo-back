import requests
from django.conf import settings


# Skip the authentication expiration error
SKIP_MESSAGES = [
  'Signature has expired',
  'Authentication credentials were not provided',
  '/api/v1/af_setup_3d_object/find/',
  'af_setup_3d_object.views.AFSetup3DObjectFind'
]


def check_in_skip_messages(message):
  for sm in SKIP_MESSAGES:
    if sm in message:
      return True
  return False


def send_error_report(payload):
  if check_in_skip_messages(payload['content']): 
    return False
  return requests.post(settings.DISCORD_CHANNEL_URL, json=payload)


def handle_log(log_record, level_id, from_decorator, raw, colored_message, bot_name="backend"):
  if log_record['level'].name == "ERROR":
    full_msg = "{asctime} | {levelname} | {process} | {filename}:{function}:{lineno} - {message}".format(
      asctime=log_record['time'].strftime('%Y-%m-%d %H:%M:%S'),
      levelname=log_record['level'].name,
      process=log_record['process'].name,
      filename=log_record['name'],
      function=log_record['function'],
      lineno=log_record['line'],
      message=log_record['message'],
    )
    payload = { "username": bot_name, "content": full_msg}
    return send_error_report(payload)
  return None
