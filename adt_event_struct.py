from datetime import date, time, datetime

from marshmallow import Schema, fields, post_load
from typing import List


class AdtEventStruct:
  """
  Represents an Admission/Discharge/Transfer event as ingested from a data feed.
  """

  def __init__(self,
               first_name: str,
               last_name: str,
               date_of_birth: date,
               facility_name: str,
               event_type: str,
               event_date: date,
               event_days: int,
               diagnosis_codes: List[str],
               event_hash: str = None,
               plan_id: int = None,
               facility_type: str = None,
               note: str = None,
               member_number: str = None,
               medical_group_tin: str = None,
               event_time: time = None,
               discharge_date: date = None) -> None:
    self.first_name: str = first_name
    self.last_name: str = last_name
    self.date_of_birth: date = date_of_birth
    self.member_number: str = member_number
    self.plan_id: int = plan_id

    # We need a facility name to know where this happened.
    self.facility_name: str = facility_name

    # But these two are optional because the data feeds are poor and they
    # might not show up there at all.
    self.facility_type: str = facility_type
    self.medical_group_tin: str = medical_group_tin

    self.event_type: str = event_type
    self.event_date: date = event_date
    self.event_time: time = event_time
    self.event_days: int = event_days
    self.discharge_date: date = discharge_date

    self.diagnosis_codes: List[str] = [
      
    ]

    self.note: str = note

    self._event_hash = event_hash

  @property
  def event_hash(self) -> str:
    return self._event_hash or \
           (f"{self.first_name}-{self.last_name}-"
            f"{self.date_of_birth.strftime('%Y-%m-%d')}-{self.event_type}-"
            f"{self.event_timestamp.strftime('%Y-%m-%d-%H:%M:%S')}")

  @property
  def event_timestamp(self) -> datetime:
    """
    Creates a `datetime` object from the `event_date` and `event_time`
    attributes. Uses midnight if no `event_time` is provided.

    NOTE (lisaliu, 6/24/20): The only ADT feed live in production right now is
    from PatientPing. They provide us timestamps in Eastern time, so we leave
    them as is for Django to convert when committing to the db.
    """
    return datetime.combine(
      self.event_date,
      self.event_time or time(0, 0),
    )


class AdtEventStructSchema(Schema):

  first_name = fields.Str(required=True)
  last_name = fields.Str(required=True)
  date_of_birth = fields.Date(required=True)

  member_number = fields.Str(required=False, allow_none=True)
  plan_id = fields.Int(required=False, allow_none=True)

  facility_name = fields.Str(required=True)
  facility_type = fields.Str(allow_none=True)
  medical_group_tin = fields.Str(allow_none=True)

  event_type = fields.Str(required=True)
  event_date = fields.Date(required=True)
  event_time = fields.Time(allow_none=True)
  event_days = fields.Int(required=True)

  diagnosis_codes = fields.List(fields.Str(required=True))
  event_hash = fields.Str(required=True)

  note = fields.Str(allow_none=True)

  @post_load
  def make_adt_event_struct(self, data):
    return AdtEventStruct(**data)
