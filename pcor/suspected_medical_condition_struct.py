from typing import Optional

from datetime import date

from marshmallow import Schema, fields, post_load


class SuspectedMedicalConditionStruct:

  def __init__(self,
               as_of_date: date,
               performance_year: int,
               member_number: str,
               status: str,
               diagnosed_on: Optional[date],
               condition: str,
               icd_code: Optional[str],
               suspected_detail: str,
               mapped_hcc_code: int) -> None:

    self.as_of_date: date = as_of_date
    self.performance_year: int = performance_year
    self.member_number: str = member_number
    self.status: str = status
    self.diagnosed_on: date = diagnosed_on
    self.condition: str = condition
    self.icd_code: str = icd_code
    self.suspected_detail: str = suspected_detail
    self.mapped_hcc_code: int = mapped_hcc_code


class SuspectedMedicalConditionStructSchema(Schema):

  as_of_date = fields.Date(required=True)
  performance_year = fields.Int(required=True)
  member_number = fields.Str(required=True)
  status = fields.Str(required=True)

  diagnosed_on = fields.Date(required=True, allow_none=True)
  condition = fields.Str(required=True)
  icd_code = fields.Str(required=True, allow_none=True)
  # In other PCOR we do not set it, so it is not required
  mapped_hcc_code = fields.Int(required=True, allow_none=True)

  suspected_detail = fields.Str(required=True)

  @post_load
  def make_struct(self, data):
    return SuspectedMedicalConditionStruct(**data)
