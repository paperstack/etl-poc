from datetime import date, time, datetime

from marshmallow import Schema, fields, post_load, validate
from typing import Dict
from copy import deepcopy


class ExternalAppointmentStruct:
  """
  Represents an External Appointment, a provider visit schedule event
  from a partner SOR.
  """

  def __init__(self,
               first_name: str,
               last_name: str,
               appointment_date: date,
               appointment_time: time,
               appointment_timezone: str,
               appointment_type: str,
               scheduled_provider_npi: str,
               appointment_status: str,
               gender: str = None,
               date_of_birth: date = None,
               member_number: str = None,
               medical_member_number: str = None,
               external_appointment_id: str = None,
               appointment_location_id: str = None,
               external_last_modified_date: datetime = None,
               external_created_date: date = None,
               plan_id: int = None,
               extra_data: dict = None) -> None:

    self.first_name: str = first_name
    self.last_name: str = last_name
    self.gender: str = gender
    self.date_of_birth = date_of_birth
    self.appointment_date: date = appointment_date
    self.appointment_time: time = appointment_time.isoformat()
    self.appointment_type: str = appointment_type.lower()
    self.scheduled_provider_npi: str = scheduled_provider_npi
    self.appointment_status: str = appointment_status.lower()
    self.member_number: str = member_number
    self.medical_member_number: str = medical_member_number
    self.external_appointment_id: str = external_appointment_id
    self.appointment_location_id: str = appointment_location_id
    self.external_last_modified_date: date = external_last_modified_date
    self.external_created_date: date = external_created_date
    self.appointment_timezone = appointment_timezone
    self.plan_id = plan_id
    self.extra_data = extra_data

  def get_persistence_fields(self) -> Dict:
    """
    This will return a dict suitable as kwargs for Django's get_or_create
    method. They keys used for lookup and those used for defaults will be
    based on the type of data present in the struct
    """
    all_fields = deepcopy(self.__dict__)
    result = {}

    # These fields will not be stored because they add no value to
    # the stored external appointment object, they are only used to
    # add more confidence to patient matching.
    # We could move them to extra_data if there's a case for persistence
    all_fields.pop('gender', None)
    all_fields.pop('date_of_birth')

    # St. Lukes Use Case
    if self.external_appointment_id:
      result['external_appointment_id'] = self.external_appointment_id
      all_fields.pop('external_appointment_id')

    result['defaults'] = all_fields
    return result


class ExternalAppointmentStructSchema(Schema):

  first_name = fields.Str(required=True, validate=validate.Length(max=200))
  last_name = fields.Str(required=True, validate=validate.Length(max=200))
  gender = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1))
  date_of_birth = fields.Date(required=False, allow_none=True)
  appointment_date = fields.Date(required=True)
  appointment_time = fields.Str(required=True)
  appointment_timezone = fields.Str(required=True)
  appointment_type = fields.Str(required=True, validate=validate.Length(max=30))
  scheduled_provider_npi = fields.Str(required=True, validate=validate.Length(max=20))
  appointment_status = fields.Str(required=True, validate=validate.Length(max=10))
  member_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
  medical_member_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
  external_appointment_id = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
  appointment_location_id = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
  external_last_modified_date = fields.Str(required=False, allow_none=True)
  external_created_date = fields.Date(required=False, allow_none=True)
  plan_id = fields.Int(required=True)
  extra_data = fields.Dict(required=False, allow_none=True)

  @post_load
  def make_external_appointment_struct(self, data):
    return ExternalAppointmentStruct(**data)
