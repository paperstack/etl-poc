from datetime import date

from marshmallow import Schema, fields, post_load


class PcorValueStruct:
  def __init__(self,
               as_of_date: date,
               performance_year: int,
               member_number: str,
               column: str,
               value: str) -> None:

    self.as_of_date: date = as_of_date
    self.performance_year: int = performance_year
    self.member_number: str = member_number
    self.column: str = column
    self.value: str = value

  def key(self):
    return f"{self.as_of_date}{self.member_number}{self.column}{self.value}"


class PcorValueStructSchema(Schema):
  as_of_date = fields.Date(required=True)
  performance_year = fields.Int(required=True)

  member_number = fields.Str(required=True)
  column = fields.Str(required=True)
  value = fields.Str(required=True)

  @post_load
  def make_pcor_value_struct(self, data):
    return PcorValueStruct(**data)
