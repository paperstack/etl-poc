from typing import List, Optional

from pandas import DataFrame
import stlukes_constants
from common_mappings import CommonAppointmentMapping


class StLukesEtlAppointmentMapping(CommonAppointmentMapping):

  FILE_TYPE = stlukes_constants.APPOINTMENTS_FILE
  FIELD_VALUE_MALE = 'Male'
  FIELD_VALUE_FEMALE = 'Female'
  NA_VALUES = ['']

  def __init__(self):
    super().__init__()

    # These are the members of the CommonPatientMapping mapping
    self.member_number = 'EDWPatientID'
    self.medical_member_number = 'Patient_MRN'
    self.first_name = 'Patient_First_Name'
    self.last_name = 'Patient_Last_Name'
    self.gender = 'Gender'
    self.date_of_birth = 'DOB'
    self.external_appointment_id = 'Appointment_ID'
    self.appointment_date = 'Appointment_Date'
    self.appointment_time = 'Appointment_Time'
    self.appointment_type = 'Appointment_Type'
    self.appointment_location_id = 'Appointment_LocationID'
    self.scheduled_provider_npi = 'Scheduled_Provider_NPI'
    self.appointment_status = 'Appointment_Status'
    self.external_last_modified_date = 'Appointment_lastmodifieddate'
    self.external_created_date = 'Appointment_createddate'
