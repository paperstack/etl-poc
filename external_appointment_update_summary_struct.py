from typing import List

from marshmallow import Schema, fields, post_load

from datetime import date


class ExternalAppointmentUpdateSummaryStruct:
  """
  Summary of data updates for inserting / adding a new external appointments.
  """

  def __init__(self,
               num_valid_appointments: int = 0,
               num_new_appointments: int = 0,
               num_existing_appointments: int = 0,
               num_dropped_appointments: int = 0,
               details: List[str] = None) -> None:

    self.num_valid_appointments = num_valid_appointments
    self.num_new_appointments = num_new_appointments
    self.num_existing_appointments = num_existing_appointments
    self.num_dropped_appointments = num_dropped_appointments
    self.details = details or []


class ExternalAppointmentUpdateSummaryStructSchema(Schema):
  num_valid_appointments = fields.Int()
  num_new_appointments = fields.Int()
  num_existing_appointments = fields.Int()
  num_dropped_appointments = fields.Int()
  details = fields.List(fields.Str(), allow_none=True)

  @post_load
  def make_adt_update_summary_struct(self, data):
    return ExternalAppointmentUpdateSummaryStruct(**data)
