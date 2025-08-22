import random
import string
import secrets
import uuid
import hashlib
from member.models import Member

def get_member_model():
  return Member

def get_lab():
  return Member.objects.filter(type=Member.LAB).order_by('id').first()

def get_admin():
  return Member.objects.filter(type=Member.ADMIN).order_by('id').first()

def get_deactive_loyalty_dentists():
  return Member.objects.filter(type=Member.DENTIST, deactive_loyalty=True).order_by('id')

def get_member(member_id):
  return Member.objects.filter(id=member_id).first()

def generate_password():
  symbols = string.punctuation
  password = ""
  for _ in range(9):
    password += secrets.choice(string.ascii_lowercase)
  password += secrets.choice(string.ascii_uppercase)
  password += secrets.choice(string.digits)
  password += secrets.choice(symbols)
  return password

def generate_api_key(member):
  # Generate a unique API key
  unique_key = uuid.uuid4()
  # Use the user's id to make the API key unique to them
  unique_key = f"{member.id}{unique_key}"
  # Hash the key for additional security
  api_key = hashlib.sha256(unique_key.encode('utf-8')).hexdigest()
  return api_key
