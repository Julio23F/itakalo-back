from django.db.models import Q, Subquery
from patient.models import Patient
from member.models import Member
from clinic.models import Clinic
from dentist_clinic.models import DentistClinic
from dentist_profile.models import DentistProfile
from archived_patient.models import ArchivedPatient
from utils.raw_sql_utils import (
  execute_raw_sql
)
from lib.loguru import logger

PARAM_DENTIST = 'dentist'
PARAM_CLINIC = 'clinic'
PARAM_FILTER_TYPE = 'filter_type'
PARAM_FILTER_TEAM = 'filter_team'

def join_two_queries(first_query, second_query):
  res = first_query
  if second_query:
    if res:
      res = res & second_query
    else:
      res = second_query
  return res

def filter_patients_by_user(request):
  user = request.user
  patients  = Patient.objects.all()
  if user.type == Member.DENTIST:
    patients = patients.filter(dentist=user)
    logger.debug(f'filtered patient by user. {patients.count()}')
  return patients

def get_query_by_dentist(request):
  if PARAM_DENTIST in request.GET:
    dentist_id = request.GET[PARAM_DENTIST]
    query = Q(dentist_id=dentist_id)
    return query
  return None

def get_query_by_dentist_sql(request):
    if PARAM_DENTIST in request.GET:
        dentist_id = request.GET[PARAM_DENTIST]
        query = "p.dentist_id = %s"
        params = [dentist_id]
        return {'sql': query, 'params': params}
    return None

def get_query_by_user(request):
  query = None
  user = request.user
  if hasattr(user, 'type') and (user.type == Member.DENTIST):
    query = Q(dentist=user)
  return query

def get_query_by_user_sql(request):
    user = request.user
    if hasattr(user, 'type') and (user.type == Member.DENTIST):
        query = "p.dentist_id = %s"
        params = [user.id]
        return {'sql': query, 'params': params}
    return None

def get_query_by_clinic(request):
  if PARAM_CLINIC in request.GET:
    clinic_id = request.GET[PARAM_CLINIC]
    # Get the related DentistProfile IDs associated with the clinic
    dentist_profile_ids = DentistClinic.objects.filter(clinic_id=clinic_id).values_list('dentist_profile_id', flat=True)
    # Get the associated dentist (Member) IDs
    dentist_ids = set(DentistProfile.objects.filter(id__in=dentist_profile_ids).values_list('dentist_id', flat=True))
    logger.debug(f'dentist_ids: {dentist_ids}')

    # clinic = Clinic.objects.get(pk=clinic_id)
    # cdps = clinic.clinic_dentist_profiles.all()
    # dentist_ids = list(cdps.values_list('dentist', flat=True))
    query = Q(dentist__in=dentist_ids)
    return query
  return None

def get_query_by_clinic_sql(request):
    if PARAM_CLINIC in request.GET:
        clinic_id = request.GET[PARAM_CLINIC]
        # Get the related DentistProfile IDs associated with the clinic
        dentist_profile_ids = DentistClinic.objects.filter(clinic_id=clinic_id).values_list('dentist_profile_id', flat=True)
        # Get the associated dentist (Member) IDs
        dentist_ids = set(DentistProfile.objects.filter(id__in=dentist_profile_ids).values_list('dentist_id', flat=True))
        
        if dentist_ids:
            placeholders = ','.join(['%s'] * len(dentist_ids))
            query = f"p.dentist_id IN ({placeholders})"
            params = list(dentist_ids)
            return {'sql': query, 'params': params}
    return None

def get_dp_query_by_dentist_name(search_key):
  query = Q(dentist__type=Member.DENTIST) & (
    Q(dentist__first_name__icontains=search_key) | \
    Q(dentist__last_name__icontains=search_key)
  )
  return query

def get_query_by_user(request):
  query = None
  user = request.user
  if hasattr(user, 'type') and (user.type == Member.DENTIST):
    query = Q(dentist=user)
  return query

def get_query_by_archived(request):
  query = None
  user = request.user
  if user is not None:  
    p_ids = list(ArchivedPatient.objects.filter(member=user.id).values_list('patient_id', flat=True))
    query = Q(id__in=p_ids)
  return query

def get_query_by_type_member(request):
  type_member = request.GET.get('type')
  if type_member:
    query = query.filter(dentist__type=type_member)  # Filtrer les dentistes par type de membre

  return query



FILTER_TYPE_VALUES = [
  'ALL',
  'FINITION', 
  'IMPRINT',
]
finition_patients_sql = """
SELECT c.* from (
  SELECT DISTINCT ON (p.id)
    p.id, t.id AS treatment_id,
    p.type AS patient_type, 
    t.state AS treatment_state, 
    t.updated_at as treatment_updated_at
  FROM patient AS p
  INNER JOIN treatment AS t ON (p.id = t.patient_id) and (t.is_finition = TRUE)
  ORDER BY p.id DESC, t.id DESC
)
AS c
"""

imprint_patients_sql = """
SELECT c.* from (
  SELECT DISTINCT ON (p.id)
    p.id, t.id AS treatment_id,
    p.type AS patient_type, 
    t.state AS treatment_state, 
    t.updated_at as treatment_updated_at
  FROM patient AS p
  INNER JOIN treatment AS t ON p.id = t.patient_id
  INNER JOIN prescription AS pr on (t.id = pr.treatment_id) and (pr.clinic_objects ILIKE '%"impression_type":"PHYSICAL_FOOTPRINT"%')
  ORDER BY p.id DESC, t.id DESC
)
AS c
"""

def get_query_by_filter_type(request):
  from pprint import pprint
  if PARAM_FILTER_TYPE in request.GET:
    filter_type = request.GET[PARAM_FILTER_TYPE]
    str_sql = None
    
    if filter_type == 'FINITION':
      str_sql = finition_patients_sql
    elif filter_type == 'IMPRINT':
      str_sql = imprint_patients_sql
    
    if str_sql:
      items = execute_raw_sql(str_sql)
      patient_ids = list(map(lambda x : x['id'], items))
      queries = Q(id__in=patient_ids)
      return queries
  return None

def get_query_by_filter_team(request):
  if PARAM_FILTER_TEAM in request.GET:
    filter_team = request.GET[PARAM_FILTER_TEAM]
    query = Q(af_setup_team_id=filter_team) 
    return query
  return None

def get_query_by_filter_type_sql(request):
    if PARAM_FILTER_TYPE in request.GET:
        filter_type = request.GET[PARAM_FILTER_TYPE]
        str_sql = None
        
        if filter_type == 'FINITION':
            str_sql = finition_patients_sql
        elif filter_type == 'IMPRINT':
            str_sql = imprint_patients_sql
        
        if str_sql:
            items = execute_raw_sql(str_sql)
            patient_ids = list(map(lambda x: x['id'], items))
            if patient_ids:
                placeholders = ','.join(['%s'] * len(patient_ids))
                query = f"p.id IN ({placeholders})"
                params = patient_ids
                return {'sql': query, 'params': params}
    return None


retainer_imprint_patients_sql = """
SELECT c.* from (
  SELECT DISTINCT ON (p.id)
    p.id, 
    p.type AS patient_type, 
    r.id AS retainer_id,
    r.state AS retainer_state, 
    r.updated_at as retainer_updated_at
  FROM patient AS p
  INNER JOIN retainer AS r ON (p.id = r.patient_id) and (r.impression_type ILIKE '%PHYSICAL%')
  INNER JOIN imprint AS i on r.id = i.retainer_id
  ORDER BY p.id DESC, r.id DESC
)
AS c
"""

def get_query_by_retainer_filter_type(request):
  if PARAM_FILTER_TYPE in request.GET:
    filter_type = request.GET[PARAM_FILTER_TYPE]
    str_sql = None
    if filter_type == 'IMPRINT':
      str_sql = retainer_imprint_patients_sql
    if str_sql:
      items = execute_raw_sql(str_sql)
      patient_ids = list(map(lambda x : x['id'], items))
      queries = Q(id__in=patient_ids)
      return queries
  return None

def get_query_by_clinicManager_OR_dentistManager(request):
  query = None
  user = request.user
  if hasattr(user, 'type') and (user.type == Member.MANAGER):
    # Sous-requête pour les cliniciens (clinic_id)
    # clinic_ids = Clinic.objects.filter(manager=user).values('id')

    # Sous-requête pour les dentistes (dentist_id)
    dentist_ids = DentistProfile.objects.filter(manager=user).values('dentist_id')

    # Combine les deux sous-requêtes avec OR
    # query = Q(clinic__id__in=Subquery(clinic_ids)) | Q(dentist__in=Subquery(dentist_ids))
    
    query = Q(dentist__in=Subquery(dentist_ids))
  return query