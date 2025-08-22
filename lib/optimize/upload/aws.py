import os
import copy
import json
import boto3
from datetime import datetime
import pprint
import sys
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings

AWS_REGION = 'eu-west-3'
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_S3_ENDPOINT_URL = os.environ.get(
    'AWS_S3_ENDPOINT_URL', 
    'https://s3-eu-west-3.amazonaws.com'
)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'aligneursfrancais-viewer-staging')

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def upload_to_aws(local_file, bucket, s3_file_name):
  try:
    response = s3_client.upload_file(local_file, bucket, s3_file_name, ExtraArgs={'ACL': 'public-read'})
    s3_file_path = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{s3_file_name}'
    return s3_file_path
  except FileNotFoundError:
    print("The file was not found")
  except NoCredentialsError:
    print("Credentials not available")
  except ClientError as e:
    print(f'{str(e)} on {e.__traceback__.tb_lineno} line')
    return None
  return None


def generate_unique_file_name(org_file_name):
  now = datetime.now()
  name, extension = os.path.splitext(org_file_name)
  new_file_name = f'{name}-{now.strftime("%Y%m%d%H%M%S")}{extension}'
  return new_file_name


def upload_aligner_file(af_setup_dir, aligner_info, aligner_path, sub_type, file_name):
  if aligner_path[0] == '/':
    aligner_path = aligner_path[1:]
  if aligner_path[-1] == '/':
    aligner_path = aligner_path[:-1]
  stage_path = os.path.join(af_setup_dir, aligner_path)
  local_file = os.path.join(af_setup_dir, aligner_path, file_name)
  print(f'Uploading file: {local_file}')
  unique_file_name = generate_unique_file_name(file_name)
  s3_file_name = f'{aligner_info["patient_id"]}/{aligner_info["af_setup_name"]}/{aligner_info["aligner_index"]}/{sub_type}/{unique_file_name}'
  s3_url = upload_to_aws(local_file, AWS_STORAGE_BUCKET_NAME, s3_file_name)
  if s3_url:
    print(f'Uploaded file: {s3_url}')
  return s3_url


def upload_stage_files(af_setup_dir, aligner_info, stages, stage_key, file_name_key):
  aligner_index = aligner_info['aligner_index']
  stage = stages[aligner_index]
  file_name = stage[file_name_key]
  aligner_path = stage['path']
  s3_url = upload_aligner_file(af_setup_dir, aligner_info, aligner_path, stage_key, file_name)
  if s3_url:
    stages[aligner_index][file_name_key] = s3_url
  return stages

def upload_upper_files(af_setup_dir, aligner_info, stages, upper_key, uppers):
  aligner_index = aligner_info['aligner_index']
  stage = stages[aligner_index]
  aligner_path = stage['path']
  uploaded_uppers = {}
  upper_index = 0
  for upper in uppers:
    file_name = upper
    s3_url = upload_aligner_file(
      af_setup_dir=af_setup_dir,
      aligner_info=aligner_info,
      aligner_path=aligner_path, 
      sub_type=upper_key,
      file_name=file_name
    )
    if s3_url:
      uploaded_uppers[str(upper_index)] = s3_url
    upper_index += 1
  stages[aligner_index][upper_key] = uploaded_uppers
  return stages

def upload_optimized_files(data_json, base_file_path, patient_id, af_setup_name):
  updated_data = copy.copy(data_json)
  UPPER_TYPE = 'upper'
  LOWER_TYPE = 'lower'
  ATTACH_TYPE = 'attach'
  STAGES_TYPE = 'stages'

  upper = data_json[UPPER_TYPE]
  lower = data_json[LOWER_TYPE]
  attach = data_json[ATTACH_TYPE]
  stages = data_json[STAGES_TYPE]
  
  updated_data["blender_data"] = data_json["blender_data"]

  af_setup_name = os.path.basename(os.path.normpath(base_file_path))
  print(f'Patient ID: {patient_id}, AF Setup: {af_setup_name} ')
  
  # Loop Aligners
  aligner_index = 0
  for stage in stages:
    # Upload stage files
    aligner_info = {
      'patient_id': patient_id,
      'af_setup_name': af_setup_name,
      'aligner_index': aligner_index
    }
    # Upload stage files
    new_stages = upload_stage_files(base_file_path, aligner_info, stages, STAGES_TYPE, 'maxilla')
    new_stages = upload_stage_files(base_file_path, aligner_info, stages, STAGES_TYPE, 'mandible')
    new_stages = upload_stage_files(base_file_path, aligner_info, stages, STAGES_TYPE, 'mouth')
    # Upload upper files
    new_stages = upload_upper_files(base_file_path, aligner_info, stages, UPPER_TYPE, upper)
    # Upload lower files
    new_stages = upload_upper_files(base_file_path, aligner_info, stages, LOWER_TYPE, lower)
    # Upload attach files
    new_stages = upload_upper_files(base_file_path, aligner_info, stages, ATTACH_TYPE, attach)
    # Update stages value
    updated_data[STAGES_TYPE] = new_stages
    aligner_index += 1
    
  return updated_data


################################################################
# Upload expert files
################################################################
EXPERT_SUB_DIR = 'objects'

def upload_expert_aligner_file(base_file_path, aligner_info, sub_type, file_name):
  local_file = os.path.join(base_file_path, file_name)
  print(f'Uploading the expert file: {local_file}')
  unique_file_name = generate_unique_file_name(file_name)
  if sub_type is None:
    # maybe this is for Mandible.gld and Maxilla.gld files
    s3_file_name = f'{aligner_info["patient_id"]}/{aligner_info["af_setup_name"]}/{unique_file_name}'
  else:
    s3_file_name = f'{aligner_info["patient_id"]}/{aligner_info["af_setup_name"]}/{EXPERT_SUB_DIR}/{sub_type}/{unique_file_name}'
  print("file : ", s3_file_name)
  s3_url = upload_to_aws(local_file, AWS_STORAGE_BUCKET_NAME, s3_file_name)
  if s3_url:
    print(f'Uploaded the expert file: {s3_url}')
  return s3_url

def upload_expert_upper_files(base_file_path, aligner_info, upper_key, uppers):
  uploaded_uppers = []
  upper_index = 0
  for upper in uppers:
    file_name = upper
    objects_file_path = os.path.join(base_file_path, EXPERT_SUB_DIR)
    s3_url = upload_expert_aligner_file(
      base_file_path=objects_file_path,
      aligner_info=aligner_info,
      sub_type=upper_key,
      file_name=file_name
    )
    uploaded_path = s3_url if s3_url else None
    uploaded_uppers.append(uploaded_path)
    upper_index += 1
  return uploaded_uppers

def upload_expert_files(data_json, base_file_path, patient_id, af_setup_name, blender_data_file):
  updated_data = copy.copy(data_json)
  UPPER_TYPE = 'upper'
  LOWER_TYPE = 'lower'
  ATTACH_TYPE = 'attach'
  MANDIBLE_GLB = 'mandible'
  MAXILLA_GLB = 'maxilla'
  MOUTH_GLB = 'mouth'
  MANDIBLE_GLB_FILE_NAME = 'Mandible.glb'
  MAXILLA_GLB_FILE_NAME = 'Maxilla.glb'
  MOUTH_GLB_FILE_NAME = 'mouth.glb'
  BLENDER_DATA_FILE_NAME = blender_data_file

  # upper = data_json[UPPER_TYPE]
  # lower = data_json[LOWER_TYPE]
  # attach = data_json[ATTACH_TYPE]
  print('=== base_file_path: ', base_file_path)
  print(f'Patient ID: {patient_id}, AF Setup: {af_setup_name} ')
  # Upload stage files
  aligner_info = {
    'patient_id': patient_id,
    'af_setup_name': af_setup_name
  }
  
  # updated_data["blender_data"] = data_json["blender_data"]

  # Upload upper files
  # updated_data[UPPER_TYPE] = upload_expert_upper_files(base_file_path, aligner_info, UPPER_TYPE, upper)
  # # Upload lower files
  # updated_data[LOWER_TYPE] = upload_expert_upper_files(base_file_path, aligner_info, LOWER_TYPE, lower)
  # # Upload attach files
  # updated_data[ATTACH_TYPE] = upload_expert_upper_files(base_file_path, aligner_info, ATTACH_TYPE, attach)
  # Upload Mandible.glb
  # updated_data[MANDIBLE_GLB] = upload_expert_aligner_file(
  #     base_file_path=base_file_path,
  #     aligner_info=aligner_info,
  #     sub_type=None,
  #     file_name=MANDIBLE_GLB_FILE_NAME,
  #   )
  # # Upload Mzxilla.glb
  # updated_data[MAXILLA_GLB] = upload_expert_aligner_file(
  #     base_file_path=base_file_path,
  #     aligner_info=aligner_info,
  #     sub_type=None,
  #     file_name=MAXILLA_GLB_FILE_NAME,
  #   )
  updated_data[MOUTH_GLB] = upload_expert_aligner_file(
      base_file_path=base_file_path,
      aligner_info=aligner_info,
      sub_type=None,
      file_name=MOUTH_GLB_FILE_NAME,
    )
  
  updated_data["blender_data"] = upload_expert_aligner_file(
      base_file_path=base_file_path,
      aligner_info=aligner_info,
      sub_type=None,
      file_name=BLENDER_DATA_FILE_NAME,
    )

  
  return updated_data
