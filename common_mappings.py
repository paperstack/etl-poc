from decimal import Decimal
from typing import List, Optional, Type

from pandas import DataFrame
import common
from patient_struct import PatientStruct
from common import row_value
from medical_group_struct import MedicalGroupStruct
from provider_struct import ProviderStruct
from address_struct import AddressStruct
import constants as medical_constants
from claim_struct import ClaimStruct
from drug_struct import DrugStruct
from drug_fill_struct import DrugFillStruct
from adt_event_struct import AdtEventStruct
import time
from datetime import datetime, date
from external_appointment_struct import ExternalAppointmentStruct

class Mapping:

  # The file type that this mapping will recognize. This file type is useful
  # for the data set to know what files to pass to what mappings, and not have
  # to do that detection at ETL processing time, and only do it when the file
  # is uploaded.
  #
  # The file type will also be useful to Ops to make sure that they understand
  # the set of files that are needed for a DataSet to be complete and ready
  # for validation / commit.
  FILE_TYPE = None

  def columns(self) -> List[str]:
    """
    Should return the columns that the mapping will be looking for in the file.
    This list of columns will be used to determine whether this mapping can
    extract data from this file.
    """
    raise NotImplementedError("Return the columns this mapping needs, in order")

  def parse_dates(self) -> List[str]:
    """
    For mappings that have dates in some of the columns, return the list of
    fields that are expected to represent dates. Not all Mappings need to
    implement this method - only the ones that have dates.
    """
    return []

  def matches_header(self, header: str) -> bool:
    """
    Returns True if this mapping finds its columns in the header, in the order
    in which they are listed.
    """
    assert self.FILE_TYPE

    for column_name in self.columns():
      col_index = header.find(column_name)
      if col_index < 0:
        return False

    # Each of the column_names were found.
    return True

# ------------------------------------------------------------------
# Demographics


class CommonPatientMapping(Mapping):
  """
  A mapping of column names that represent structured data that we extract
  often from DataFrames.
  If a subclass of this will set these values, then this class can use those
  values and create PatientStruct structures out of a DataFrame row.
  """

  # Set the values of Gender Male / Female in the respective data file.
  FIELD_VALUE_MALE = None
  FIELD_VALUE_FEMALE = None

  NA_VALUES = []

  def __init__(self):
    self.member_number = None
    self.gender = None
    self.date_of_birth = None
    self.first_name = None
    self.last_name = None

    self.address_line_1 = None
    self.address_line_2 = None
    self.city = None
    self.state = None
    self.zip = None
    self.phone = None

    self.tin = None
    self.npi = None

    self.line_of_business = None

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.member_number,
      self.gender,
      self.date_of_birth,
      self.first_name,
      self.last_name,

      self.address_line_1,
      self.address_line_2,
      self.city,
      self.state,
      self.zip,

      self.phone,

      self.tin,
      self.npi,

      self.line_of_business
    ])

  def get_patient_struct(self, row: DataFrame) -> PatientStruct:
    """
    A simple extraction of a patient struct from the row. If there is more
    data to be extracted, mappings that expand from this mapping should
    override their own methods.
    """
    medical_group = self.get_medical_group_struct(row)

    provider_struct = self.get_provider_struct(row)
    # If there is no provider struct, this is an orphan patient.
    if provider_struct:
      provider_struct.medical_group = medical_group

    address_struct = self.get_address_struct(row)

    return PatientStruct(
      member_number=row[self.member_number],
      first_name=row[self.first_name],
      last_name=row[self.last_name],
      gender=self.get_gender(row),
      date_of_birth=row[self.date_of_birth],

      provider=provider_struct,
      address=address_struct,

      line_of_business=row_value(row, self.line_of_business)
    )

  def get_medical_group_struct(self,
                               row: DataFrame) -> Optional[MedicalGroupStruct]:
    if not self.tin:
      return None

    tin = row[self.tin]
    return MedicalGroupStruct(name="-", tin=tin)

  def get_provider_struct(self, row: DataFrame) -> Optional[ProviderStruct]:
    if not self.npi:
      return None

    npi = row[self.npi]
    return ProviderStruct(first_name="-", last_name="-", npi=npi)

  def get_address_struct(self, row: DataFrame) -> Optional[AddressStruct]:
    """
    If any of the mappings for an address are set, then an AddressStruct will
    be created with the data extracted from those columns.
    Otherwise, this will return None and assume that if addresses are present
    in the ETL, they will be filled in from somewhere else.
    """
    if not any([self.address_line_1, self.address_line_2, self.city, self.state,
                self.zip, self.phone]):
      return None

    return AddressStruct(
      address1=row_value(row, self.address_line_1, '', na_values=self.NA_VALUES) or '',
      address2=row_value(row, self.address_line_2, '', na_values=self.NA_VALUES) or '',
      city=row_value(row, self.city, '', na_values=self.NA_VALUES) or '',
      state=row_value(row, self.state, '', na_values=self.NA_VALUES) or '',
      zip=row_value(row, self.zip, '', na_values=self.NA_VALUES) or '',
      phone_number=row_value(row, self.phone, '', na_values=self.NA_VALUES) or ''
    )

  def get_gender(self, row: DataFrame) -> Optional[str]:
    if not self.gender:
      return None

    # If a gender column is specified, ensure that the field values for male and
    # female are set to something other than None - and that the developer does
    # not forget to set these values in the mapping.
    assert(all([self.FIELD_VALUE_MALE, self.FIELD_VALUE_FEMALE]))

    if row[self.gender] == self.FIELD_VALUE_MALE:
      return medical_constants.GENDER_MALE
    if row[self.gender] == self.FIELD_VALUE_FEMALE:
      return medical_constants.GENDER_FEMALE

    return medical_constants.GENDER_NONE


# ------------------------------------------------------------------
# Claims


class CommonClaimMapping(Mapping):

  NA_VALUES = []

  def __init__(self):
    self.claim_number = None
    self.claim_type = None
    self.member_number = None

    self.from_date = None
    self.thru_date = None
    self.admission_date = None
    self.discharge_date = None

    self.procedures = []
    self.diagnoses = []

    self.provider_npi = None
    self.medical_group_tin = None
    self.drg_code = None
    self.drg_type = None
    self.setting = None

    self.revenue_code = None
    self.amount_gross = None
    self.amount_paid = None

    # For certain sets of claims, we have the name of the payer that adjudicated
    # that claim - and we would like to store this in the database.
    self.plan_name = None

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.member_number,
      self.claim_number,
      self.claim_type,

      self.from_date,
      self.thru_date,
      self.admission_date,
      self.discharge_date,

      self.provider_npi,
      self.medical_group_tin,
      self.drg_code,
      self.drg_type,
      self.setting,

      self.revenue_code,
      self.amount_gross,
      self.amount_paid,

      self.plan_name
    ] + self.diagnoses + self.procedures)

  def parse_dates(self) -> List[str]:
    return common.remove_all_none([
      self.from_date,
      self.thru_date,
      self.admission_date,
      self.discharge_date
    ])

  def get_claim_struct(self,
                       row: DataFrame,
                       claim_cls: Type[ClaimStruct] = ClaimStruct) -> Optional[ClaimStruct]:
    ap_raw_value = row_value(row, self.amount_paid, '0',
                             na_values=self.NA_VALUES)
    amount_paid = Decimal(ap_raw_value)

    ag_raw_value = row_value(row, self.amount_gross, '0',
                             na_values=self.NA_VALUES)
    amount_gross = Decimal(ag_raw_value)

    claim = claim_cls(
      claim_number=row[self.claim_number],
      claim_type=row_value(row, self.claim_type, 'UNK',
                           na_values=self.NA_VALUES),
      member_number=row[self.member_number],

      from_date=row_value(row, self.from_date, na_values=self.NA_VALUES),
      thru_date=row_value(row, self.thru_date, na_values=self.NA_VALUES),
      admission_date=row_value(row, self.admission_date,
                               na_values=self.NA_VALUES),
      discharge_date=row_value(row, self.discharge_date,
                               na_values=self.NA_VALUES),

      provider_npi=row_value(row, self.provider_npi, na_values=self.NA_VALUES),
      medical_group_tin=row_value(row, self.medical_group_tin,
                                  na_values=self.NA_VALUES),

      setting=row_value(row, self.setting, na_values=self.NA_VALUES),
      drg_code=row_value(row, self.drg_code, na_values=self.NA_VALUES),
      drg_type=row_value(row, self.drg_type, na_values=self.NA_VALUES),

      amount_paid=amount_paid,
      amount_gross=amount_gross,

      revenue_code=row_value(row, self.revenue_code, na_values=self.NA_VALUES),

      plan_name=row_value(row, self.plan_name, na_values=self.NA_VALUES)
    )
    for column in self.procedures:
      code = row_value(row, column, na_values=self.NA_VALUES)
      if code:
        claim.maybe_add_procedure(row[column])

    for column in self.diagnoses:
      code = row_value(row, column, na_values=self.NA_VALUES)
      if code:
        claim.maybe_add_diagnosis(row[column])

    return claim


class CommonRxClaimMapping(Mapping):

  NA_VALUES = []

  def __init__(self):
    self.member_number = None
    self.claim_number = None
    self.claim_type = None

    self.from_date = None

    self.ndc = None
    self.drug_name = None
    self.generic_indicator = None

    self.prescriber_npi = None
    self.pharmacy_npi = None
    self.pharmacy_name = None

    self.amount_gross = None
    self.amount_paid = None

    self.refill_number = None
    self.refills_authorized = None

    self.quantity_dispensed = None
    self.days_supply = None

    self.script_written_date = None
    self.plan_name = None

    self.fill_date = None

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.member_number,
      self.claim_number,
      self.claim_type,

      self.from_date,

      self.ndc,
      self.drug_name,
      self.generic_indicator,

      self.prescriber_npi,
      self.pharmacy_npi,
      self.pharmacy_name,

      self.amount_gross,
      self.amount_paid,

      self.refill_number,
      self.refills_authorized,
      self.quantity_dispensed,
      self.days_supply,

      self.script_written_date,
      self.plan_name
    ])

  def parse_dates(self) -> List[str]:
    return common.remove_all_none([
      self.from_date,
      self.script_written_date
    ])

  def get_refills_authorized(self, row: DataFrame) -> Optional[int]:
    # If this value is set in the ETL, then use it and pull out the number of
    # refills authorized.
    refills_authorized = None
    if self.refills_authorized:
      n = row_value(row, self.refills_authorized, na_values=self.NA_VALUES)
      if n:
        refills_authorized = Decimal(n).to_integral_value()

    return refills_authorized

  def get_drug_struct(self, row: DataFrame) -> DrugStruct:
    return DrugStruct(
      ndc=row[self.ndc],
      drug_name=row_value(row, self.drug_name, "-"),
      brand_flag=row_value(row, self.generic_indicator, "-"),
      gpi="-",
      gcn="-"
    )

  def get_drug_fill_struct(self, row: DataFrame) -> DrugFillStruct:
    refills_authorized = self.get_refills_authorized(row)

    drug_struct = self.get_drug_struct(row)

    return DrugFillStruct(
      claim_number=row[self.claim_number],
      member_number=row[self.member_number],

      ndc=row[self.ndc],
      drug=drug_struct,

      # When we don't use row_value, it means that we expect these values to
      # always be present, and always have an expected format.
      refill_number=Decimal(row_value(row, self.refill_number, default=0)).to_integral_value(),
      quantity_dispensed=Decimal(row[self.quantity_dispensed]).to_integral_value(),
      days_supply=Decimal(row[self.days_supply]).to_integral_value(),

      refills_authorized=refills_authorized,
      script_written_date=row_value(row, self.script_written_date, None),
      fill_date=row_value(row, self.fill_date, None)
    )

  def get_claim_struct(self,
                       row: DataFrame,
                       claim_cls: Type[ClaimStruct] = ClaimStruct) -> Optional[ClaimStruct]:
    drug_fill_struct = self.get_drug_fill_struct(row)

    ap_raw_value = row_value(row, self.amount_paid, '0', self.NA_VALUES)
    amount_paid = Decimal(ap_raw_value)

    ag_raw_value = row_value(row, self.amount_gross, '0', self.NA_VALUES)
    amount_gross = Decimal(ag_raw_value)

    claim = claim_cls(
      claim_number=row[self.claim_number],
      claim_type=row_value(row, self.claim_type, None) or '',
      member_number=row[self.member_number],

      from_date=row[self.from_date],
      thru_date=row[self.from_date],

      prescribing_npi=row[self.prescriber_npi],
      pharmacy_npi=row_value(row, self.pharmacy_npi, None),
      pharmacy_name=row_value(row, self.pharmacy_name, None),

      drug_fills=[drug_fill_struct],

      amount_paid=amount_paid,
      amount_gross=amount_gross,

      plan_name=row_value(row, self.plan_name, None)
    )
    return claim

# ------------------------------------------------------------------
# ADT (Admission/Discharge/Transfer) Events


class CommonAdtEventMapping(Mapping):

  NA_VALUES = ['None Provided']

  def __init__(self):
    self.member_number = None
    self.first_name = None
    self.last_name = None
    self.date_of_birth = None

    self.facility_name = None
    self.facility_type = None

    self.event_type = None
    self.event_date = None
    self.event_days = None

    self.diagnosis_code_str = None
    self.diagnosis_codes = []

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.member_number,
      self.first_name,
      self.last_name,
      self.date_of_birth,

      self.facility_name,
      self.facility_type,

      self.event_type,
      self.event_days,
      self.event_date,

      self.diagnosis_code_str,

    ] + self.diagnosis_codes)

  def get_adt_event_struct(self, row: DataFrame) -> Optional[AdtEventStruct]:
    try:
      event_days = int(row_value(row, self.event_days, 0))
    except ValueError:
      # If the value that's in the file fails to parse, save this as zero.
      event_days = 0

    event_struct = AdtEventStruct(
      first_name=row[self.first_name],
      last_name=row[self.last_name],
      date_of_birth=row[self.date_of_birth],

      facility_name=row[self.facility_name],
      facility_type=row[self.facility_type],

      event_type=row_value(row, self.event_type),
      event_date=row_value(row, self.event_date),
      event_days=event_days,

      diagnosis_codes=row[self.diagnosis_codes] | [],
    )

    return event_struct

# ------------------------------------------------------------------
# Patient <-> Provider Appointments


class CommonAppointmentMapping(Mapping):

  NA_VALUES = ['None Provided']

  def __init__(self):
    self.first_name: str = None
    self.last_name: str = None
    self.gender: str = None
    self.date_of_birth: str = None
    self.appointment_date: date = None
    self.appointment_time: time = None
    self.appointment_type: str = None
    self.scheduled_provider_npi: str = None
    self.appointment_status: str = None
    self.member_number: str = None
    self.medical_member_number: str = None
    self.external_appointment_id: str = None
    self.appointment_location_id: str = None
    self.external_last_modified_date: str = None
    self.external_created_date: str = None
    self.plan_id: int = None

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.first_name,
      self.last_name,
      self.gender,
      self.date_of_birth,
      self.appointment_date,
      self.appointment_time,
      self.appointment_type,
      self.scheduled_provider_npi,
      self.appointment_status,
      self.member_number,
      self.medical_member_number,
      self.external_appointment_id,
      self.appointment_location_id,
      self.external_last_modified_date,
      self.external_created_date,
      self.plan_id
    ])

  def get_appointment_struct(self, row: DataFrame) -> Optional[ExternalAppointmentStruct]:
    raw_time = row_value(row, self.appointment_time)
    formatted_time = datetime.strptime(raw_time, "%H%M").time()
    appointment_timezone = 'America/Boise'
    appointment_struct = ExternalAppointmentStruct(
      first_name=row_value(row, self.first_name),
      last_name=row_value(row, self.last_name),
      gender=self.get_gender(row),
      date_of_birth=row_value(row, self.date_of_birth),
      appointment_date=row_value(row, self.appointment_date),
      appointment_time=formatted_time,
      appointment_timezone=appointment_timezone,
      appointment_type=row_value(row, self.appointment_type),
      scheduled_provider_npi=row_value(row, self.scheduled_provider_npi),
      appointment_status=row_value(row, self.appointment_status),
      member_number=row_value(row, self.member_number),
      medical_member_number=row_value(row, self.medical_member_number),
      external_appointment_id=row_value(row, self.external_appointment_id),
      appointment_location_id=row_value(row, self.appointment_location_id),
      external_last_modified_date=row_value(row, self.external_last_modified_date),
      external_created_date=row_value(row, self.external_created_date)
    )

    return appointment_struct

  def get_gender(self, row: DataFrame) -> Optional[str]:
    if not self.gender:
      return None

    # If a gender column is specified, ensure that the field values for male and
    # female are set to something other than None - and that the developer does
    # not forget to set these values in the mapping.
    assert(all([self.FIELD_VALUE_MALE, self.FIELD_VALUE_FEMALE]))

    if row[self.gender] == self.FIELD_VALUE_MALE:
      return medical_constants.GENDER_MALE
    if row[self.gender] == self.FIELD_VALUE_FEMALE:
      return medical_constants.GENDER_FEMALE

    return medical_constants.GENDER_NONE


class CommonStellarProviderMapping(Mapping):
  """
  A file generated by Stellar, that contains the source of truth for the NPI/TIN
  combinations that we want to import in a data set.
  This file is generated by Ops, extracted from the data. The reason we do that
  is so that we can control what groups get imported, and be able to easily
  resolve ambiguities around the TINs that certain providers are associated
  with.
  """

  def __init__(self):
    self.first_name = 'First Name'
    self.last_name = 'Last Name'

    self.npi = 'NPI Number'
    self.tin = 'Tax ID'

    self.address_line_1 = 'Mailing Street'
    self.city = 'Mailing City'
    self.state = 'State'
    self.zip = 'Zip Code'
    self.phone = 'Phone'

    self.practice_name = 'Practice'

  def columns(self) -> List[str]:
    return common.remove_all_none([
      self.first_name,
      self.last_name,

      self.npi,
      self.tin,

      self.address_line_1,
      self.city,
      self.state,
      self.zip,
      self.phone,

      self.practice_name
    ])

  def get_provider_struct(self, row: DataFrame) -> Optional[ProviderStruct]:
    npi = self.get_npi(row)
    if not npi:
      return None

    mg_struct = self.get_medical_group_struct(row)

    return ProviderStruct(
      first_name=row_value(row, self.first_name),
      last_name=row_value(row, self.last_name),
      npi=npi,
      medical_group=mg_struct
    )

  def get_medical_group_struct(self,
                                row: DataFrame) -> Optional[MedicalGroupStruct]:
    tin = row_value(row, self.tin)
    if not tin:
      return None

    address_struct = self.get_address_struct(row)

    return MedicalGroupStruct(
      name=row_value(row, self.practice_name, f"- ({tin})"),
      tin=tin,
      address=address_struct
    )

  def get_address_struct(self, row: DataFrame) -> Optional[AddressStruct]:
    return AddressStruct(
      address1=row_value(row, self.address_line_1, ''),
      address2='',
      city=row_value(row, self.city, ''),
      state=row_value(row, self.state, ''),
      zip=row_value(row, self.zip, ''),
      phone_number=row_value(row, self.phone, '')
    )

  def get_npi(self, row: DataFrame) -> Optional[str]:
    return row_value(row, self.npi)
