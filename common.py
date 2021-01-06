import inspect
import json
from collections import defaultdict
import time
from typing import List, Optional, Any, Tuple, Union, Set, Dict, DefaultDict
from datetime import datetime

import marshmallow
import pandas as pd
import requests

from tenacity import retry
from tenacity.wait import wait_random_exponential
from patient_struct import PatientStruct
from pcor.pcor_patient_struct import PcorPatientStruct
import etl_err



class RosterUpdateSummary:
  """
  Used to pass data around about the results of the roster update.
  """
  def __init__(self):
    self.all_member_numbers: List[str] = []
    self.orphaned_member_numbers: List[str] = []
    self.orphaned_count: int = 0
    self.patients_per_plan: DefaultDict[str, int] = defaultdict(int)
    self.details: List[str] = []


# -------------------------------------------------------------------
# Row extraction utilities.

def row_has_all_the_fields(row, fieldnames):
  for field in fieldnames:
    if field not in row:
      return False, "Expected field [%s], not found" % field
  return True, ""


def strip_all_values_for_row(row):
  for key, value in row.items():
    if value:
      row[key] = value.strip()


def remove_all_none(l: List) -> List:
  return [v for v in l if v is not None]


def is_empty_row(row):
  return all(value == '' for value in row.values())


def row_value(row, key, default=None, na_values: List[str] = None):
  val = row[key] if key else default
  na_values = na_values or []

  if key and pd.isnull(val):
    return default

  if val in na_values:
    return default

  return val


def parse_date(raw: str) -> Optional[datetime]:
  from_date = None

  # We accept any of these formats as valid dates, and we try them one after
  # the other. We assume that if any of them pass there isn't a big risk
  # that we somehow got the wrong date.
  for date_format in ["%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d %H:%M:%S.%f",
                      "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"]:
    try:
      from_date = datetime.strptime(raw, date_format)
    except ValueError:
      pass

  return from_date


def batch(iterable, batch_size=1):
  # If batch size is set to None, don't do batching and return the entire
  # list.
  if batch_size is None:
    yield iterable
    return

  # NOTE(octavian): In practice this seems to work, but I have copy-pasted this
  # from the internet and I currently do not deeply understand it. Python
  # iterables and yield are things that I should dig a bit deeper into.
  iterable_len = len(iterable)
  for ndx in range(0, iterable_len, batch_size):
    yield list(iterable)[ndx:min(ndx + batch_size, iterable_len)]


'''def get_etl(data_set: DataSet) -> Optional[AbstractEtl]:
  """
  Returns the ETL Class that corresponds to the ETL name passed in as a
  parameter. If we do not recognize this name, we return None.

  :param data_set: The data set for which we'd like to get an ETL instance that
      knows how to process this DataSet.

  :return: An instantiation of the ETL Class that corresponds to the name
      passed in as a parameter.
  """
  etl_name = data_set.etl_name

  #log.debug("DataSet.id=%s has etl=%s" % (data_set.id, etl_name))

  for etl_class in installed_etl_classes():
    if etl_class.__name__ == etl_name:
      return etl_class(data_set)

  return None
'''

def _get_etl_class(etl_name: str) -> Any:
  module_path = ".".join(etl_name.split('.')[:-1])
  class_name = etl_name.split('.')[-1]

  module = __import__(module_path, fromlist=[class_name])
  klass = getattr(module, class_name)
  return klass


'''def installed_etl_classes() -> List[Any]:
  """Returns a list of instances for all the ETLs in settings.INSTALLED_ETLS.

  :return: A list of instantiations of the ETL Classes that correspond to the
      classes in the list of installed ETLs.
  """
  return [_get_etl_class(etl_name) for etl_name in settings.INSTALLED_ETLS]
'''

# ------------------------------------------------------------------------
# Methods for posting to the SFE api.

@retry(wait=wait_random_exponential(multiplier=0.5, min=1, max=8))  # seconds
def _requests_post_rate_adapt(sfe_url, json_dict: dict):
  r = requests.post(sfe_url, json=json_dict, timeout=120)
  if r.status_code == 429:  # Too Many Requests
    r.raise_for_status()

  return r


def requests_post(sfe_url, json_dict: dict) -> Tuple[Optional[str], Optional[str]]:
  try:
    r = _requests_post_rate_adapt(sfe_url, json_dict)
    r.raise_for_status()
    #log.info("POST %s success" % sfe_url)

  except requests.exceptions.RequestException as e:
    #log.error("%s" % e)
    return "%s" % e, None

  return None, r.content


def post_to_endpoint(data_set_id: int,
                     json_data: json,
                     update_path: str,
                     summary_schema: marshmallow.Schema = None,
                     commit: bool = False) -> Tuple[Optional[object], List[str]]:
  """
  Wrapper for the function below, just to keep the interface the same for the
  rest of the codebase, it basically just discards the patient
  """
  result, errors, _ = post_to_endpoint_with_patient_struct(data_set_id,
                                                           json_data,
                                                           update_path,
                                                           summary_schema,
                                                           commit)
  return result, errors


def post_to_endpoint_with_patient_struct(
    data_set_id: int,
    json_data: json,
    update_path: str,
    summary_schema: marshmallow.Schema = None,
    commit: bool = False,
    return_patient_struct: Union[PatientStruct, PcorPatientStruct] = None
) -> Tuple[Optional[object], List[str], Union[PatientStruct, PcorPatientStruct]]:
  """Calls the patient update endpoint, and returns a summary.

  If the update struct is None, then the method returns the list of errors
  that happened while trying to update this Patient data.

  :param data_set_id: The ID of the data set that this is part of - used to
      pass into the update endpoint so that we can debug on both sides.
  :param json_data: A serialized structure that will be sent to update.
  :param update_path: The path to post to.
  :param summary_schema: An instantiated schema that will be used to
      deserialize the expected response from the API.
  :param commit: True/False on whether this is just to validate or actually
      to commit the data to the DB.
  :param return_patient_struct: Patient struct, returned as-is, used in async
      requests to be able to map request to a patient.

  :return: A tuple with the first being a SummaryStruct created by the
      serializer, and if this value is None, then a list of errors that caused
      the SummaryStruct to be None. Third returned value is a patient struct.
  """
  #from django.conf import settings

  err, content = requests_post("http://localhost:8000" + update_path, json_dict={
    'json_data': json_data,
    'commit': commit,
    'data_set_id': data_set_id,
    'api_key': "pBSBtzsb3OqTx57W"
  })
  if err:
    return None, [err], return_patient_struct

  response = json.loads(content)
  success = response['success']
  if not success:
    return None, response['errors'], return_patient_struct
  else:
    return response['update_summary'], [], return_patient_struct

  errors = None
  summary = summary_schema.load(response['update_summary'])
  if errors:
    errors = ["%s: %s" % (key, err) for key, err in errors.items()]
    return None, errors, return_patient_struct

  return summary, [], return_patient_struct


'''def update_roster(etl: AbstractEtl,
                  data_set: DataSet,
                  commit: bool = False) -> RosterUpdateSummary:
  """
  Goes through all the member numbers for each of the Plans in the ETL
  that is currently processing the data, and uses that list of member
  numbers as the source of truth of the patients that are currently part of
  the plan.

  In case roster_update is set to False, we return without updating the roster
  """
  roster_summary = RosterUpdateSummary()
  roster_summary.all_member_numbers = []

  if (data_set.is_pcor() or data_set.type == 'part_d') and not data_set.update_roster:
    roster_summary.details.append(etl_err.W053_UPDATE_ROSTER_SET_TO_FALSE.display(
      "update_roster is set to False"
    ))

    return roster_summary

  for condition, plan_id in etl.plan_ids_by_condition.items():
    roster_patients = etl.extract_roster_member_numbers(condition)

    #log.debug("Setting roster for [%s], plan_id=[%s]" % (condition, plan_id),
    #          member_numbers=roster_patients)

    # If this is a claims-only data set, the roster_patients will be None.
    mg_id = data_set.medical_group_id if data_set.medical_group else None

    _post_roster(plan_id=plan_id,
                 roster_member_numbers=roster_patients,
                 roster_summary=roster_summary,
                 restrict_to_medical_group_id=mg_id,
                 commit=commit)

    roster_summary.all_member_numbers += list(roster_patients)

    #plan = Plan.objects.get(id=plan_id)
    #roster_summary.patients_per_plan[plan.name] = len(roster_patients)

  return roster_summary
'''

def _post_roster(plan_id: int,
                 roster_member_numbers: Set[str],
                 roster_summary: RosterUpdateSummary,
                 restrict_to_medical_group_id: Optional[int],
                 commit=False):
  # If we did process a Demographics File, then all_member_numbers will not
  # be none, and as a result we go to orphaning patients.
  #
  # NOTE(octavian): Also very very unlikely that there are empty list of
  # patients, so bail if that's the case - it's likely a bug.
  if not roster_member_numbers:
    return

  orphaned_numbers, count, err = _post_roster_to_endpoint(
    plan_id,
    roster_member_numbers,
    restrict_to_medical_group_id,
    commit=commit)

  if orphaned_numbers:
    roster_summary.orphaned_member_numbers += orphaned_numbers
    roster_summary.orphaned_count += count

  else:
    for e in err:
      err_str = etl_err.E034_ORPHANING_FAILED.display(
        f"return error for all_member_numbers='{roster_member_numbers}' {e}")
      roster_summary.details.append(err_str)
      #log.debug(e, all_member_numbers=roster_member_numbers)
      roster_summary.orphaned_member_numbers = []


def _post_roster_to_endpoint(
    plan_id: int,
    roster_member_numbers: Set[str],
    restrict_to_medical_group_id: Optional[int],
    commit: bool
) -> Tuple[Optional[List[str]], int, List[str]]:
  """
  Posts the roster member numbers, and the medical group restriction for a
  specific plan to the SFE.

  The post will include the value of the commit - which will decide whether
  this is a validation only operation or one that would lead to data updates.
  """
  #from django.conf import settings
  """if restrict_to_medical_group_id:
    url = settings.SFE_URL + reverse('api_plan_set_roster_for_mg', kwargs={
      'medical_group_id': restrict_to_medical_group_id,
      'plan_id': plan_id
    })
  else:
    url = settings.SFE_URL + reverse('api_plan_set_roster', kwargs={
      'plan_id': plan_id
    })

  err, content = requests_post(url, json_dict={
    'all_member_numbers': list(roster_member_numbers),
    'commit': commit,
    'api_key': settings.STELLAR_PATIENT_UPDATE_API_KEY
  })
  if err:
    return None, 0, [err]

  response = json.loads(content)
  success = response['success']
  if not success:
    return None, 0, response['errors']

  orphaned_member_numbers = json.loads(response['orphaned_member_numbers'])
  orphaned_count = int(response['orphaned_count'])

  return orphaned_member_numbers, orphaned_count, []
  """
  return None
