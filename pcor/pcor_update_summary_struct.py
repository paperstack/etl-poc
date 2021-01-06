from collections import defaultdict
from typing import List, DefaultDict

from marshmallow import fields, Schema, post_load

from sfe.api_data.pcor.pcor_measure_summary import PcorMeasureSummaryStruct, \
  PcorMeasureSummaryStructSchema
from sfe.api_data.stellar_network_change_struct import \
  StellarNetworkChangeStruct, StellarNetworkChangeStructSchema


class PcorUpdateSummaryStruct:
  """
  Summary of what data would change for a PatientStruct update.

  Whenever a PatientStruct is posted in the /api_data/patient/pcor/update
  endpoint, we summarize all the relevant changes that result from that update
  in this class and return it to the caller of the API.
  """

  def __init__(
      self,
      num_valid_patients: int = 0,
      num_new_patients: int = 0,
      num_existing_patients: int = 0,
      num_dropped_patients: int = 0,
      num_placeholder_patients: int = 0,
      details: List[str] = None,
      network_changes: List[StellarNetworkChangeStruct] = None,
      num_created_suspected_medical_conditions=0,
      num_existing_suspected_medical_conditions=0,
      num_created_medication_adherence_statuses=0,
      num_existing_medication_adherence_statuses=0,
      num_created_pcor_values=0,
      num_existing_pcor_values=0,
      all_member_numbers: List[str] = None,
      orphaned_member_numbers: List[str] = None,
      orphaned_count: int = 0,
      patients_per_plan: DefaultDict[str, int] = None,
      pcor_measure_summaries: List[PcorMeasureSummaryStruct] = None,
      num_created_pcor_measure_summaries: int = 0,
      num_dropped_pcor_measure_summaries: int = 0,
      num_existing_pcor_measure_summaries: int = 0
  ) -> None:
    self.num_valid_patients: int = num_valid_patients
    self.num_new_patients: int = num_new_patients
    self.num_existing_patients: int = num_existing_patients
    self.num_dropped_patients: int = num_dropped_patients
    self.num_placeholder_patients = num_placeholder_patients

    self.details = details or []
    self.network_changes = network_changes or []

    self.num_created_suspected_medical_conditions = num_created_suspected_medical_conditions
    self.num_existing_suspected_medical_conditions = num_existing_suspected_medical_conditions

    self.num_created_medication_adherence_statuses = num_created_medication_adherence_statuses
    self.num_existing_medication_adherence_statuses = num_existing_medication_adherence_statuses

    self.num_created_pcor_values = num_created_pcor_values
    self.num_existing_pcor_values = num_existing_pcor_values

    self.all_member_numbers = all_member_numbers or []
    self.orphaned_member_numbers = orphaned_member_numbers or []
    self.orphaned_count: int = orphaned_count

    self.patients_per_plan = patients_per_plan or defaultdict(int)

    self.pcor_measure_summaries = pcor_measure_summaries or []

    self.num_created_pcor_measure_summaries = num_created_pcor_measure_summaries
    self.num_dropped_pcor_measure_summaries = num_dropped_pcor_measure_summaries
    self.num_existing_pcor_measure_summaries = num_existing_pcor_measure_summaries

  def update_from_roster_summary(self, roster_summary):
    self.all_member_numbers = roster_summary.all_member_numbers
    self.orphaned_member_numbers = roster_summary.orphaned_member_numbers
    self.orphaned_count = roster_summary.orphaned_count
    self.patients_per_plan = roster_summary.patients_per_plan
    self.details.extend(roster_summary.details)


class PcorUpdateSummaryStructSchema(Schema):

  num_valid_patients = fields.Int()
  num_new_patients = fields.Int()
  num_existing_patients = fields.Int()
  num_dropped_patients = fields.Int()
  num_placeholder_patients = fields.Int()

  details = fields.List(fields.Str(), allow_none=True)
  network_changes = fields.Nested(StellarNetworkChangeStructSchema, many=True)

  num_created_suspected_medical_conditions = fields.Int()
  num_existing_suspected_medical_conditions = fields.Int()

  num_created_medication_adherence_statuses = fields.Int()
  num_existing_medication_adherence_statuses = fields.Int()

  num_created_pcor_values = fields.Int()
  num_existing_pcor_values = fields.Int()

  all_member_numbers = fields.List(fields.Str(), allow_none=True)
  orphaned_member_numbers = fields.List(fields.Str(), allow_none=True)

  orphaned_count = fields.Int(allow_none=True)

  patients_per_plan = fields.Dict(keys=fields.Int(), values=fields.Int(),
                                  allow_none=True)

  pcor_measure_summaries = fields.Nested(PcorMeasureSummaryStructSchema, many=True)

  num_created_pcor_measure_summaries = fields.Int()
  num_dropped_pcor_measure_summaries = fields.Int()
  num_existing_pcor_measure_summaries = fields.Int()

  @post_load
  def make_patient_update_summary_struct(self, data):
    return PcorUpdateSummaryStruct(**data)
