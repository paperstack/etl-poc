
# Unable to parse date
import inspect

from typing import List


class Err:
  def __init__(self, code: str, action: str, scope: str = None):
    # The error code.
    self.code = code
    # The resolution of this error. This generally contains the effect that
    # encountering the error resulted in - patient data dropped, data set
    # skipped, placeholder patient created, etc.
    self.action = action

    # If not None, it will tell the user what kind of data this affects. This
    # should be used sparingly, as the error code itself and the action taken
    # should generally be enough for a user to understand the consequences
    # of this error.
    self.scope = scope

  def display(self, message: str, scope: str = None, action: str = None):
    """
    Returns a string to display an error. If scope and action are passed in, they
    will override the scope and action of the Err object that's passed in.
    """
    level = "info"
    if self.code.startswith("E"):
      level = "error"
    elif self.code.startswith("W"):
      level = "warning"

    return _etl_message(level,
                        scope or self.scope,
                        action or self.action,
                        self.code,
                        message)


# -------------------------------------------------------------------
# When picking the next error number, please see the end of this list.

E001_UNABLE_TO_PARSE_DATE = Err("E001_UNABLE_TO_PARSE_DATE", action="data dropped")
E002_CSV_HEADER_INVALID = Err("E002_CSV_HEADER_INVALID", action="data dropped")
E003_TOO_MANY_ERRORS = Err("E003_TOO_MANY_ERRORS", action="skipped rest of file")

E005_PATIENT_UPDATE_ENDPOINT_FAILED = Err("E005_PATIENT_UPDATE_ENDPOINT_FAILED", action="patient data dropped")
E006_ADT_ENDPOINT_FAILED = Err("E006_ADT_ENDPOINT_FAILED", action="adt data dropped")
E036_SUMMARY_ENDPOINT_FAILED = Err("E036_SUMMARY_ENDPOINT_FAILED", action="pcor measure summary data dropped")
E067_APPOINTMENT_ENDPOINT_FAILED = Err("E067_APPOINTMENT_ENDPOINT_FAILED", action="external appointment dropped")

E007_CLAIM_DATA_DROPPED = Err("E007_CLAIM_DATA_DROPPED", action="claim data dropped")

E030_DIAGNOSIS_DATA_DROPPED = Err("E030_DIAGNOSIS_DATA_DROPPED", action="diagnosis data dropped")
E031_PROCEDURE_DATA_DROPPED = Err("E031_PROCEDURE_DATA_DROPPED", action="procedure data dropped")
W037_UNKNOWN_CLAIM_CODE_TYPE = Err("W037_UNKNOWN_CLAIM_CODE_TYPE", action="code dropped")

E025_RX_CLAIM_DATA_DROPPED = Err("E025_RX_CLAIM_DATA_DROPPED", action="claim data dropped")

E004_PATIENT_DATA_DROPPED = Err("E004_PATIENT_DATA_DROPPED", action="patient data dropped")
W011_PATIENT_ADDRESS_MISSING = Err("W011_PATIENT_ADDRESS_MISSING", action="patient added with no address")

E012_PATIENT_SECOND_ROW_SKIPPED = Err("E012_PATIENT_SECOND_ROW_SKIPPED", action="second row skipped")

I039_PATIENT_IMPORTED_AS_PLACEHOLDER = Err("I039_PATIENT_IMPORTED_AS_PLACEHOLDER", action="imported as placeholder")

W033_ROSTER_ORPHANING_SKIPPED = Err("W033_ROSTER_ORPHANING_SKIPPED", action="orphaning skipped")
E034_ORPHANING_FAILED = Err("E034_ORPHANING_FAILED", action="orphaning failed")
I038_ROSTER_USED = Err("I038_ROSTER_USED", action="")

W014_ADT_SECOND_ROW_SKIPPED = Err("W014_ADT_SECOND_ROW_SKIPPED", action="second row skipped")
W018_DUPLICATE_EVENTS = Err("W018_DUPLICATE_EVENTS", action="second row skipped")

E015_ADT_FILE_SKIPPED = Err("E015_ADT_FILE_SKIPPED", action="file skipped")
E068_APPOINTMENTS_FILE_SKIPPED = Err("E068_APPOINTMENTS_FILE_SKIPPED", action="file skipped")

E022_837_LINE_DATA_DROPPED = Err("E022_837_LINE_DATA_DROPPED", action="line data dropped")
E023_837_PARSER_ERROR = Err("E023_837_PARSER_ERROR", action="line data dropped")

I029_PATIENT_PLAN_AUTO_SET = Err("I029_PATIENT_PLAN_AUTO_SET", action="patient plan_id auto set")

E032_DATA_SET_SKIPPED = Err("E032_DATA_SET_SKIPPED", action="data set skipped")
E035_PHARMACY_SHEET_SKIPPED = Err("E035_PHARMACY_SHEET_SKIPPED", action="pharmacy sheet skipped")

E037_837_ROSTER_GENERATION_FAILED = Err("E037_837_ROSTER_GENERATION_FAILED", action="roster file dropped")
E039_ADT_EVENT_DATA_DROPPED = Err("E039_ADT_EVENT_DATA_DROPPED", action="event data dropped")

W040_POTENTIAL_DUPLICATE_MEMBER = Err("W040_POTENTIAL_DUPLICATE_MEMBER", action="create new patient")
W041_MEMBER_NUMBER_CHANGE = Err("W041_MEMBER_NUMBER_CHANGE", action="update member number")

W063_MG_BULK_PCOR_DISABLED = Err("W063_MG_BULK_PCOR_DISABLED", action="change MG bulk pcor flag")

W064_CLAIM_DIAGNOSIS_MISSING = Err("W064_CLAIM_DIAGNOSIS_MISSING", action="claim imported with no diagnosis codes")

W065_ADT_FACILITY_NAME_MISSING = Err("W065_ADT_FACILITY_NAME_MISSING", action="event imported without facility name")

# Attribution warnings feel important enough to separate them into different
# scope, instead of clumping them all in one.
W042_ATTRIBUTION_FROM_PROVIDER_TO_MG = Err("W042_ATTRIBUTION_FROM_PROVIDER_TO_MG", action="attribution updated")
W043_ATTRIBUTION_FROM_MG_TO_PROVIDER = Err("W043_ATTRIBUTION_FROM_MG_TO_PROVIDER", action="attribution updated")
W044_ATTRIBUTION_DE_ORPHAN_TO_MG = Err("W044_ATTRIBUTION_DE_ORPHAN_TO_MG", action="attribution updated")
W045_ATTRIBUTION_DE_ORPHAN = Err("W045_ATTRIBUTION_DE_ORPHAN", action="attribution updated")
W046_ATTRIBUTED_PROVIDER_CHANGED = Err("W046_ATTRIBUTED_PROVIDER_CHANGED", action="attribution updated")

W047_PATIENT_PLAN_CHANGED = Err("W047_PATIENT_PLAN_CHANGED", action="plan updated")
W048_PATIENT_DEMOGRAPHICS_CHANGED = Err("W048_PATIENT_DEMOGRAPHICS_CHANGED", action="demographics updated")

W049_MISSING_SOME_CLAIMS_DATA = Err("W049_MISSING_SOME_CLAIMS_DATA", action="ignoring")

W050_PCOR_VALUES_ADDED_CROSS_PLAN = Err("W050_PCOR_VALUES_ADDED_CROSS_PLAN", action="data added across plan")

W051_MEMBER_NUMBER_CHANGE_IGNORED = Err("W051_MEMBER_NUMBER_CHANGE_IGNORED", action="member number change ignored")
W052_CLAIMS_ADDED_CROSS_PLAN = Err("W052_CLAIMS_ADDED_CROSS_PLAN", action="data added across plan")

W053_UPDATE_ROSTER_SET_TO_FALSE = Err("W053_UPDATE_ROSTER_SET_TO_FALSE", action="skipping roster update")

I054_PCOR_MAPPING_USED = Err("I054_PCOR_MAPPING_USED", action="")

E055_PCOR_HEADER_MEMBERS = Err("E055_PCOR_HEADER_MEMBERS", action="")
E056_PCOR_HEADER_PHARMACY = Err("E056_PCOR_HEADER_PHARMACY", action="")
E057_PCOR_HEADER_GROUP_SUMMARY = Err("E057_PCOR_HEADER_GROUP_SUMMARY", action="")

W058_PCOR_HEADER_MEMBERS = Err("W058_PCOR_HEADER_MEMBERS", action="")
W059_PCOR_HEADER_PHARMACY = Err("W059_PCOR_HEADER_PHARMACY", action="")
W060_PCOR_HEADER_GROUP_SUMMARY = Err("W060_PCOR_HEADER_GROUP_SUMMARY", action="")

E061_UNKNOWN_FILE = Err("E061_UNKNOWN_FILE", action="")

W062_DUPLICATE_ADDRESS_DETECTED = Err("W062_DUPLICATE_ADDRESS_DETECTED", action="")

E066_EXTERNAL_APPOINTMENT_DROPPED = Err("E066_EXTERNAL_APPOINTMENT_DROPPED", action="")

W069_UNCERTAIN_APPOINTMENT_DEMOGRAPHIC_DATA = Err("W069_UNCERTAIN_APPOINTMENT_DEMOGRAPHIC_DATA", action="")

# Next number: 070


# -------------------------------------------------------------------
# A couple of really basic, common, and likely to be removed errors.

def too_many_errors(file_name: str) -> str:
  return E003_TOO_MANY_ERRORS.display("More than 1000 errors", scope=file_name)


def invalid_csv_header(file_name: str, row, message: str) -> str:
  return E002_CSV_HEADER_INVALID.display(f"CSV header invalid {row}, {message}",
                                         scope=file_name)


def unable_to_parse_date(scope: str, row, action: str = None) -> str:
  return E001_UNABLE_TO_PARSE_DATE.display(f"parsing date failed on {row}",
                                           action=action, scope=scope)


def data_set_skipped(message: str) -> str:
  return E032_DATA_SET_SKIPPED.display(message)


def pcor_mapping_used(action: str) -> str:
  return I054_PCOR_MAPPING_USED.display("mapping found", action=action)


def pcor_headers_members(message: str, action: str) -> str:
  return E055_PCOR_HEADER_MEMBERS.display(message, action=action)


def pcor_headers_pharmacy(message: str, action: str) -> str:
  return E056_PCOR_HEADER_PHARMACY.display(message, action=action)


def pcor_headers_group_summary(message: str, action: str) -> str:
  return E057_PCOR_HEADER_GROUP_SUMMARY.display(message, action=action)


def pcor_headers_members_extra_columns(message: str, action: str) -> str:
  return W058_PCOR_HEADER_MEMBERS.display(message, action=action)


def pcor_headers_pharmacy_extra_columns(message: str, action: str) -> str:
  return W059_PCOR_HEADER_PHARMACY.display(message, action=action)


def pcor_headers_group_summary_extra_columns(message: str, action: str) -> str:
  return W060_PCOR_HEADER_GROUP_SUMMARY.display(message, action=action)


# -------------------------------------------------------------------
# Error construction for ETL errors.

def _etl_message(level: str,
                 scope: str,
                 outcome: str,
                 code: str,
                 detail: str) -> str:
  caller_name = "unknown"
  caller_file_path = inspect.stack()[2][1]
  if caller_file_path:
    caller_name = caller_file_path.split('/')[-1].replace('.py', '')

  err = code
  if scope:
    err = f"{code}-{scope}"
  return f"{level} {err}-{caller_name} -- {detail} :: {outcome}"


# -------------------------------------------------------------------
# Fancier logging based on error message

def display(err: Err, message: str, scope: str = None, action: str = None):
  """
  Returns a string to display an error. If scope and action are passed in, they
  will override the scope and action of the Err object that's passed in.
  """
  level = "info"
  if err.code.startswith("E"):
    level = "error"
  elif err.code.startswith("W"):
    level = "warning"

  return _etl_message(level,
                      scope or err.scope,
                      action or err.action,
                      err.code,
                      message)


# -------------------------------------------------------------------
# Auto-commit error handling

AUTO_COMMIT_BLOCKING_ERRORS = {
  "adt": [E015_ADT_FILE_SKIPPED],
  "appointments": [W069_UNCERTAIN_APPOINTMENT_DEMOGRAPHIC_DATA,
                              E068_APPOINTMENTS_FILE_SKIPPED]
}


def get_auto_commit_blocking_errors(
        dataset_type: str,
        details: List[str],
) -> List[str]:
  """
  Returns a list of errors encountered that should prevent the associated
  dataset from being automatically committed.
  """
  blocking_errors = AUTO_COMMIT_BLOCKING_ERRORS.get(dataset_type, None)
  if blocking_errors is None:
    # If no blocking errors have been defined for the dataset type, fail
    # loudly so the operators know that somehow, the dataset has been flagged
    # for auto-commit
    raise NotImplementedError()

  details_concatenated = ', '.join(details)
  blocking_errors_found = []
  for error in blocking_errors:
    if error.code in details_concatenated:
      blocking_errors_found.append(error.code)

  return blocking_errors_found
