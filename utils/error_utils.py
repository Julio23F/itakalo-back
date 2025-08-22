# custom handler
from rest_framework.views import exception_handler
from sentry_sdk import capture_message
# from lib.discord.report import send_error_report
from lib.loguru import logger


# def discord_track_errors(exc, context, level="error"):
#   full_msg = f"{level}: {str(exc)}: {str(context)}"
#   payload = { "username": "apibot", "content": full_msg}
#   response = send_error_report(payload)
#   return response
  


def custom_exception_handler(exc, context):
  response = exception_handler(exc, context)
  capture_message(exc, level="error")
  # discord_track_errors(exc, context)
  logger.error(str(context))
  return response
