from typing import List, Set, DefaultDict
from datetime import datetime
from collections import defaultdict

from marshmallow import fields, Schema, post_load

from sfe.api_data.stellar_network_change_struct import \
  StellarNetworkChangeStruct, StellarNetworkChangeStructSchema


class PatientUpdateSummaryStruct:
  """Summary of what data would change for a PatientStruct update.

  Whenever a PatientStruct is posted in the /api_data/patient/update endpoint,
  we summarize all the relevant changes that result from that update in this
  class and return it to the caller of the API.
  """

  def __init__(
      self,
      num_valid_patients: int = 0,
      num_new_patients: int = 0,
      num_existing_patients: int = 0,
      num_dropped_patients: int = 0,
      num_attributed_to_provider_patients: int = 0,
      num_attributed_to_medical_group_patients: int = 0,
      num_placeholder_patients: int = 0,
      num_changed_member_number: int = 0,
      num_changed_provider: int = 0,
      new_stellar_npis: Set[str] = None,
      new_stellar_tins: Set[str] = None,
      num_changed_demographics: int = 0,
      num_changed_plan: int = 0,
      num_new_claims: int = 0,
      num_patients_with_new_claims: int = 0,
      new_claims_min_date: datetime = None,
      new_claims_max_date: datetime = None,
      num_claims_with_new_procedures: int = 0,
      num_claims_with_new_diagnoses: int = 0,
      num_claims_with_new_drug_fills: int = 0,
      details: List[str] = None,
      network_changes: List[StellarNetworkChangeStruct] = None,
      all_member_numbers: List[str] = None,
      attributed_to_provider_member_numbers: List[str] = None,
      attributed_to_medical_group_member_numbers: List[str] = None,
      orphaned_member_numbers: List[str] = None,
      orphaned_count: int = 0,
      num_icd9_diagnoses: int = 0,
      num_icd10_diagnoses: int = 0,
      num_invalid_diagnoses: int = 0,
      num_uncertain_diagnoses: int = 0,
      invalid_diagnoses: DefaultDict[str, int] = None,
      uncertain_diagnoses: DefaultDict[str, int] = None,
      patients_per_plan: DefaultDict[str, int] = None
  ) -> None:
    self.num_valid_patients: int = num_valid_patients

    self.num_new_patients: int = num_new_patients
    self.num_existing_patients: int = num_existing_patients
    self.num_dropped_patients: int = num_dropped_patients
    self.num_placeholder_patients: int = num_placeholder_patients
    self.num_attributed_to_provider_patients: int = num_attributed_to_provider_patients
    self.num_attributed_to_medical_group_patients: int = num_attributed_to_medical_group_patients

    # A member_number changing is a tricky situation. This shows up for when
    # we find an already existing [name, last_name, gender and date_of_birth]
    # for a patient, but that patient has a different member_number.
    self.num_changed_member_number: int = num_changed_member_number

    # TODO(amar) Change to num_changed_attribution?
    self.num_changed_provider: int = num_changed_provider

    self.new_stellar_npis = new_stellar_npis or []
    self.new_stellar_tins = new_stellar_tins or []

    self.num_changed_demographics: int = num_changed_demographics
    self.num_changed_plan: int = num_changed_plan

    self.num_new_claims: int = num_new_claims
    self.num_patients_with_new_claims: int = num_patients_with_new_claims

    self.new_claims_min_date: datetime = new_claims_min_date
    self.new_claims_max_date: datetime = new_claims_max_date

    self.num_claims_with_new_procedures: int = num_claims_with_new_procedures
    self.num_claims_with_new_diagnoses: int = num_claims_with_new_diagnoses
    self.num_claims_with_new_drug_fills: int = num_claims_with_new_drug_fills

    # Whatever change counters we capture above that should be the summary,
    # and this will hold a list of details that would capture those changes.
    self.details = details or []

    self.network_changes = network_changes or []

    self.all_member_numbers = all_member_numbers or []
    self.attributed_to_provider_member_numbers = attributed_to_provider_member_numbers or []
    self.attributed_to_medical_group_member_numbers = attributed_to_medical_group_member_numbers or []
    self.orphaned_member_numbers = orphaned_member_numbers or []
    self.orphaned_count: int = orphaned_count

    self.num_icd9_diagnoses: int = num_icd9_diagnoses
    self.num_icd10_diagnoses: int = num_icd10_diagnoses
    self.num_invalid_diagnoses: int = num_invalid_diagnoses
    self.num_uncertain_diagnoses: int = num_uncertain_diagnoses
    self.invalid_diagnoses = invalid_diagnoses or defaultdict(int)
    self.uncertain_diagnoses = uncertain_diagnoses or defaultdict(int)

    self.patients_per_plan = patients_per_plan or defaultdict(int)

  def update_from_roster_summary(self, roster_summary):
    self.all_member_numbers = roster_summary.all_member_numbers
    self.orphaned_member_numbers = roster_summary.orphaned_member_numbers
    self.orphaned_count = roster_summary.orphaned_count
    self.patients_per_plan = roster_summary.patients_per_plan
    self.details.extend(roster_summary.details)


class PatientUpdateSummaryStructSchema(Schema):

  num_valid_patients = fields.Int()
  num_new_patients = fields.Int()
  num_existing_patients = fields.Int()
  num_dropped_patients = fields.Int()
  num_placeholder_patients = fields.Int()

  num_attributed_to_provider_patients = fields.Int()
  num_attributed_to_medical_group_patients = fields.Int()

  num_changed_member_number = fields.Int()
  num_changed_provider = fields.Int()

  new_stellar_npis = fields.List(fields.Str())
  new_stellar_tins = fields.List(fields.Str())

  num_changed_demographics = fields.Int()
  num_changed_plan = fields.Int()

  num_new_claims = fields.Int()
  num_patients_with_new_claims = fields.Int()

  new_claims_min_date = fields.DateTime(allow_none=True)
  new_claims_max_date = fields.DateTime(allow_none=True)

  num_claims_with_new_procedures = fields.Int()
  num_claims_with_new_diagnoses = fields.Int()
  num_claims_with_new_drug_fills = fields.Int(allow_none=True)

  details = fields.List(fields.Str(), allow_none=True)

  network_changes = fields.Nested(StellarNetworkChangeStructSchema, many=True)

  # List of all member numbers (valid and invalid) seen during processing of
  # data.
  all_member_numbers = fields.List(fields.Str(), allow_none=True)
  orphaned_member_numbers = fields.List(fields.Str())
  orphaned_count = fields.Int()

  num_icd9_diagnoses = fields.Int()
  num_icd10_diagnoses = fields.Int()
  num_invalid_diagnoses = fields.Int()
  num_uncertain_diagnoses = fields.Int()
  invalid_diagnoses = fields.Dict(keys=fields.Str(), values=fields.Int())
  uncertain_diagnoses = fields.Dict(keys=fields.Str(), values=fields.Int())

  patients_per_plan = fields.Dict(keys=fields.Int(), values=fields.Int(),
                                  allow_none=True)

  @post_load
  def make_patient_update_summary_struct(self, data):
    return PatientUpdateSummaryStruct(**data)
