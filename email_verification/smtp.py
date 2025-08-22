import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def SendMail(subject, text, html, from_email, to_emails, password):
  sender_email = from_email
  receiver_email = to_emails
  password = password
  message = MIMEMultipart("alternative")
  message["Subject"] = subject
  message["From"] = sender_email
  message["To"] = receiver_email
  part1 = MIMEText(text, "plain", _charset="UTF-8")
  part2 = MIMEText(html, "html", _charset="UTF-8")
  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)
  message.attach(part2)
  # Create secure connection with server and send email
  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
      server.login(sender_email, password)
      server.sendmail(
          sender_email, receiver_email, message.as_string()
      )
      server.close()
      