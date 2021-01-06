from typing import List, Optional

from datetime import date

from marshmallow import post_load, Schema, fields
from provider_struct import ProviderStruct, ProviderStructSchema
from pcor.suspected_medical_condition_struct import SuspectedMedicalConditionStruct,\
  SuspectedMedicalConditionStructSchema
from pcor.medication_adherence_status import MedicationAdherenceStatusStruct,\
  MedicationAdherenceStatusStructSchema
from pcor.pcor_value import PcorValueStruct, PcorValueStructSchema
from address_struct import AddressStruct, AddressStructSchema




class PcorPatientStruct:
  # TODO(octavian): Unify PatientStruct and PcorPatientStruct and join all the
  #  fields that are and should be similar.

  def __init__(self,
               member_number: str,
               as_of_date: date,
               update_most_recent_pcor_date: bool,
               performance_year: int,
               plan_id: int = 0,
               first_name: str = None,
               last_name: str = None,
               date_of_birth: date = None,
               provider: ProviderStruct = None,
               restrict_to_tin: str = None,
               suspected_medical_conditions: List[SuspectedMedicalConditionStruct] = None,
               medication_adherence_statuses: List[MedicationAdherenceStatusStruct] = None,
               pcor_values: List[PcorValueStruct] = None,
               update_patient_details: bool = True,
               address: AddressStruct = None,
               gender: Optional[str] = None) -> None:

    self.member_number: str = member_number
    self.plan_id: int = plan_id
    self.as_of_date = as_of_date
    self.performance_year = performance_year
    self.update_most_recent_pcor_date = update_most_recent_pcor_date

    self.first_name: str = first_name
    self.last_name: str = last_name
    self.date_of_birth: date = date_of_birth

    self.provider = provider
    self.restrict_to_tin = restrict_to_tin

    self.suspected_medical_conditions: List[SuspectedMedicalConditionStruct] = \
      suspected_medical_conditions or []
    self.medication_adherence_statuses: List[MedicationAdherenceStatusStruct] = \
      medication_adherence_statuses or []
    self.pcor_values: List[PcorValueStruct] = pcor_values or []

    # Legacy PCOR has no gender, but bulk PCOR does. We include it if provided, otherwise set it to GENDER_NONE.
    self.gender = gender if gender is not None else "-"
    self.update_patient_details: bool = update_patient_details

    self.address: AddressStruct = address

  def attributed_tin(self) -> Optional[str]:
    if self.provider and self.provider.medical_group:
      return self.provider.medical_group.tin
    return None

  def attributed_tin_different_than_forced_tin(self) -> bool:
    """
    If 'restrict_to_tin' has been set by an ETL, this method will return True
    if that TIN is different than the TIN that the Provider that this patient
    struct is attributed to is a part of.

    Returns False both if the TINS are the same, but also if either the
    restrict_tin is not set at all, or the patient struct does not have an
    attributed provider set (claims-only patients).
    """
    forced_tin = self.restrict_to_tin
    attributed_tin = self.attributed_tin()
    return attributed_tin and forced_tin and attributed_tin != forced_tin

  def get_medical_group_name(self) -> Optional[str]:
    if self.provider and self.provider.medical_group:
      return self.provider.medical_group.name
    return None

  def get_npi(self):
    return self.provider.npi if self.provider else None

  def get_provider_name(self):
    return self.provider.name if self.provider else None

  def data_complete(self):
    # All the fields are set to non empty values.
    return self.member_number and self.plan_id and self.get_npi() \
           and self.attributed_tin() and self.first_name and self.last_name \
           and self.date_of_birth

  def data_complete_for_medical_group_attribution(self):
    # We do not have this implemented for PCOR data
    return False

  def medical_group_data_complete(self) -> bool:
    if self.provider and self.provider.medical_group:
      return self.provider.medical_group.data_complete()
    return False

  def only_claims(self) -> bool:
    # member_number and plan_id are set, but everything else is empty or
    # missing.
    return self.member_number and self.plan_id and not self.provider and \
           not self.first_name and not self.last_name and not self.date_of_birth

  def missing_some_fields(self) -> List[str]:
    # Claims only struct does not have these, so if we have any at all, validate
    if self.provider or self.first_name or self.last_name or self.date_of_birth:
      wanted_fields = [
        'member_number',
        'plan_id',
        'provider',
        'first_name',
        'last_name',
        'date_of_birth'
      ]

      return [f for f in wanted_fields if not getattr(self, f, None)]

    return []

  def maybe_add_pcor_values(self, pcor_value_structs) -> int:
    # Add pcor values to patient but only if they are not added already as
    # we are now pulling them from both sheets
    num_added = 0
    existing_pcor_keys = [pv.key() for pv in self.pcor_values]

    for pv in pcor_value_structs:
      pv_key = pv.key()
      if pv_key in existing_pcor_keys:
        continue

      self.pcor_values.append(pv)
      existing_pcor_keys.append(pv_key)

      num_added += 1
    return num_added


class PcorPatientStructSchema(Schema):

  member_number = fields.Str(required=True)
  plan_id = fields.Int(required=True)
  performance_year = fields.Int(required=True)
  as_of_date = fields.Date(required=True)
  update_most_recent_pcor_date = fields.Boolean(required=True)

  first_name = fields.Str(allow_none=True)
  last_name = fields.Str(allow_none=True)
  gender = fields.Str(allow_none=True)

  date_of_birth = fields.Date(allow_none=True)

  restrict_to_tin = fields.Str(allow_none=True)
  provider = fields.Nested(ProviderStructSchema, allow_none=True)

  suspected_medical_conditions = fields.Nested(
    SuspectedMedicalConditionStructSchema, many=True)
  medication_adherence_statuses = fields.Nested(
    MedicationAdherenceStatusStructSchema, many=True)

  pcor_values = fields.Nested(PcorValueStructSchema, many=True)

  update_patient_details = fields.Bool(required=True, allow_none=False)

  address = fields.Nested(AddressStructSchema, allow_none=True)

  @post_load
  def make_struct(self, data):
    return PcorPatientStruct(**data)
