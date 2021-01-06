from typing import List, Optional

from datetime import date

from marshmallow import Schema, fields, post_load, validate

from provider_struct import ProviderStruct, ProviderStructSchema
from claim_struct import ClaimStruct, ClaimStructSchema
from address_struct import AddressStruct, AddressStructSchema
from medical_group_struct import MedicalGroupStruct, MedicalGroupStructSchema



class PatientStruct:

  def __init__(self,
               member_number: str,
               plan_id: int = 0,
               first_name: str = None,
               last_name: str = None,
               gender: str = None,
               date_of_birth: date = None,
               address: AddressStruct = None,
               line_of_business: str = None,
               provider: ProviderStruct = None,
               attributed_medical_group: MedicalGroupStruct = None,
               restrict_to_tin: str = None,
               claims: List[ClaimStruct] = None,
               date_of_death: date = None,
               medicare_status_code: str = None,
               dual_status_code: str = None,
               original_entitlement_status_code: str = None) -> None:
    """
    Creates a Patient Struct to be passed into the /api/patient/update api as
    json.

    There are two types of data that we accept: Patient With Demographics, or
    claims-only data. Both will have a PatientStruct.

    For a Patient With Demographics data update, we assume that:
    + The following fields are required to be present:
      + member_number
      + plan_id
      + first_name
      + last_name
      + gender
      + date of birth
      + provider.npi
      + provider.medical_group.tin
      + claims

    Note that patients which are attributed to Medical Group have no provider
    but have all the other demographics data

    + The following fields could be present or missing:
      + address (and if present, could have only ZIP and STATE)
      + provider.first_name
      + provider.last_name
      + provider.medical_group.name
      + line_of_business

    For a Claims-Only data structure, we assume that:
    + The following fields are required to be present:
      + member_number
      + plan_id
      + claims

    A PatientStruct that is neither PatientWithDemographics nor ClaimsOnly is
    considered invalid by the API endpoint and will be rejected.
    """
    self.member_number: str = member_number
    self.plan_id: int = plan_id

    self.first_name: str = first_name
    self.last_name: str = last_name
    self.gender: str = gender
    self.date_of_birth: date = date_of_birth
    self.date_of_death: date = date_of_death

    self.provider: ProviderStruct = provider
    self.attributed_medical_group: MedicalGroupStruct = attributed_medical_group

    # If the MedicalGroupTin is present this patient struct must belong to
    # the Medical Group when it is imported.
    self.restrict_to_tin: str = restrict_to_tin

    # The line of business under which the this patient was assigned to this
    # doctor.
    self.line_of_business: str = line_of_business

    self.claims: List[ClaimStruct] = claims or []

    self.address: AddressStruct = address

    self.medicare_status_code: str = medicare_status_code
    self.dual_status_code: str = dual_status_code
    self.original_entitlement_status_code: str = original_entitlement_status_code

  def data_complete(self):
    # All the fields are set to non empty values.
    return self.member_number and self.plan_id and \
           self.provider and self.plan_id and \
           self.first_name and self.last_name and self.gender and \
           self.date_of_birth

  def data_complete_for_medical_group_attribution(self):
    # All the fields are set to non empty values.
    # This is pretty much the same as data_complete but replaces the provider
    # with medical group
    return self.member_number and self.plan_id and \
           self.attributed_medical_group and self.plan_id and \
           self.first_name and self.last_name and self.gender and \
           self.date_of_birth

  def only_claims(self):
    # member_number and plan_id are set, but everything else is empty or
    # missing.
    return self.member_number and self.plan_id and \
           not self.provider and not self.line_of_business and \
           not self.first_name and not self.last_name and \
           not self.gender and not self.date_of_birth and not self.address

  def missing_some_fields(self) -> List[str]:
    # member_number and plan_id are set, but one of the other fields is
    # missing.
    missing_fields = []

    if not self.member_number:
      missing_fields.append("member_number")
    if not self.plan_id:
      missing_fields.append("plan_id")

    if self.provider or self.first_name or \
        self.last_name or self.gender or self.date_of_birth:
      # There are only two ways we accept data for a PatientStruct to be
      # valid:
      # + either all the Patient Demographics are present - it's a part
      #   of a patient-centric data set
      # + none of the Patient Demographics are present - it's part of a claims
      #   centric data set where all we have is a member_number and a plan_id.
      # TODO(vivi): Move this into a Validation step for the serializer.
      wanted_fields = ['first_name', 'last_name', 'gender',
                       'date_of_birth']

      # Patients attributed to medical group have no provider but have an MG
      if self.data_complete_for_medical_group_attribution():
        wanted_fields.append('attributed_medical_group')
      else:
        wanted_fields.append('provider')

      missing_fields = missing_fields + [
        f for f in wanted_fields if not getattr(self, f, None)
      ]

    return missing_fields

  def attributed_tin(self) -> Optional[str]:
    if not self.provider or not self.provider.medical_group:
      return None

    return self.provider.medical_group.tin

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

  def attributed_to_medical_group_unchanged(self, patient):
    # For patients that are attributed to medical group we skip the provider
    # check as they do not have a provider, but this would classify them as
    # orhpans. This only applies to the patients:
    # - Have no provider in db or incoming data
    # - Have attributed medical group in db and incoming data
    # - Attributed medical groups match
    return (patient.provider is None and self.provider is None
      and patient.attributed_medical_group is not None
      and self.attributed_medical_group is not None
      and patient.attributed_medical_group.tin == self.attributed_medical_group.tin)

  def moved_from_provider_to_medical_group(self, patient):
    # For ETLs that do not use attributed_medical_group it will always be None
    # so this will never be satisfied
    return (patient.provider and not self.provider  # Had provider before
            # Did not have an attributed MG
            and not patient.attributed_medical_group
            # But now there is one now
            and self.attributed_medical_group)

  def moved_from_medical_group_to_provider(self, patient):
    # For ETLs that do not use attributed_medical_group it will always be None
    # so this will never be satisfied
    return (patient.attributed_medical_group and not self.attributed_medical_group  # Had MG before
            # Did not have an attributed provider
            and not patient.provider
            # But there is one now
            and self.provider)

  def deorphaned_to_medical_group(self, patient):
    # For ETLs that do not use attributed_medical_group it will always be None
    # so this will never be satisfied
    return (patient.is_orphan()  # No provider
            and not patient.attributed_medical_group  # No medical group
            and self.provider is None  # Not being attributed to provider
            and self.attributed_medical_group)  # But being attributed to MG

  def deorphaned_to_provider(self, patient):
    # For ETLs that do not use attributed_medical_group it will always be None
    # so this will work correctly to detect de-orphaning
    return (patient.is_orphan()  # No provider
            and not patient.attributed_medical_group  # No medical group
            and not self.attributed_medical_group  # Not being attributed to medical group
            and self.provider)  # But being attributed to provider

  def provider_changed_and_same_attributed_medical_group(self, patient):
    current_tin = patient.attributed_medical_group.tin if patient.attributed_medical_group else None
    struct_tin = self.attributed_medical_group.tin if self.attributed_medical_group else None
    tin_unchanged = current_tin == struct_tin
    return tin_unchanged and patient.get_npi() != self.get_npi()

  def get_medical_group_name(self) -> Optional[str]:
    if not self.provider or not self.provider.medical_group:
      return None

    return self.provider.medical_group.name

  def get_npi(self):
    if not self.provider:
      return None

    return self.provider.npi

  def get_provider_name(self):
    if not self.provider:
      return None

    return self.provider.name()

  def make_orphan(self):
    """
    Clears the provider field, but also clears a range of other fields until
    we implement the API to create orphaned patients that also have demographics
    data.
    """
    # TODO(octavian): Our API currently expects either all the data to be
    #   present, or none of it. It does not support importing orphaned
    #   patients that do have demographics information.
    #
    #   Until we fix that, we will drop the demographics data for this ETL
    #   for placeholder patients, even though we do have it.
    self.provider = None
    self.first_name = None
    self.last_name = None
    self.gender = None
    self.date_of_birth = None
    self.address = None
    self.line_of_business = None


class PatientStructSchema(Schema):
  """
  A marshmallow serializer / deserializer to replace the rest framework
  serializers.
  """
  member_number = fields.Str(required=True, validate=validate.Length(max=200))
  plan_id = fields.Int(required=True)

  first_name = fields.Str(allow_none=True, validate=validate.Length(max=200))
  last_name = fields.Str(allow_none=True, validate=validate.Length(max=200))
  gender = fields.Str(allow_none=True, validate=validate.Length(max=10))

  date_of_birth = fields.Date(allow_none=True)
  date_of_death = fields.Date(allow_none=True)

  address = fields.Nested(AddressStructSchema, allow_none=True)

  provider = fields.Nested(ProviderStructSchema, allow_none=True)
  attributed_medical_group = fields.Nested(MedicalGroupStructSchema, allow_none=True)
  restrict_to_tin = fields.Str(allow_none=True)

  line_of_business = fields.Str(allow_none=True)

  claims = fields.Nested(ClaimStructSchema, many=True)

  medicare_status_code = fields.Str(allow_none=True, validate=validate.Length(max=2))
  dual_status_code = fields.Str(allow_none=True)
  original_entitlement_status_code = fields.Str(allow_none=True, validate=validate.Length(max=1))

  @post_load
  def make_patient_struct(self, data):
    return PatientStruct(**data)
