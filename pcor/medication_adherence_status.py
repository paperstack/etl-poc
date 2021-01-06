from datetime import date
from marshmallow import Schema, fields, validate, post_load


class MedicationAdherenceStatusStruct:
  def __init__(self,
               as_of_date: date,
               performance_year: int,
               member_number: str,
               measure_code: str,
               current_year_status: str,
               prior_year_result: str = None,
               drug_name: str = None,
               prescriber: str = None,
               prescriber_phone: str = None,
               pharmacy: str = None,
               pharmacy_phone: str = None,
               drug_quantity: str = None,
               last_fill_date: date = None,
               day_supply_of_fill: str = None,
               refill_due_date: date = None,
               lis: str = None,
               days_missed_in_last_45_days: str = None,
               days_of_therapy_missed_ytd: str = None,
               allowable_days_remaining: str = None,
               adherence_forecast: str = None) -> None:

    self.as_of_date: date = as_of_date
    self.performance_year: int = performance_year
    self.member_number: str = member_number
    self.measure_code: str = measure_code

    self.current_year_status: str = current_year_status
    self.prior_year_result: str = prior_year_result

    self.drug_name: str = drug_name
    self.prescriber: str = prescriber
    self.prescriber_phone: str = prescriber_phone
    self.pharmacy: str = pharmacy
    self.pharmacy_phone: str = pharmacy_phone

    self.drug_quantity: str = drug_quantity
    self.last_fill_date: date = last_fill_date
    self.day_supply_of_fill: str = day_supply_of_fill
    self.refill_due_date: date = refill_due_date

    self.lis: str = lis
    self.days_missed_in_last_45_days: str = days_missed_in_last_45_days
    self.days_of_therapy_missed_ytd: str = days_of_therapy_missed_ytd
    self.allowable_days_remaining: str = allowable_days_remaining

    self.adherence_forecast: str = adherence_forecast


class MedicationAdherenceStatusStructSchema(Schema):

  as_of_date = fields.Date(required=True)
  performance_year = fields.Int(required=True)
  member_number = fields.Str(required=True)
  measure_code = fields.Str(validate=validate.Length(max=20))

  current_year_status = fields.Str(validate=validate.Length(max=10))
  prior_year_result = fields.Str(validate=validate.Length(max=10), allow_none=True)

  drug_name = fields.Str(validate=validate.Length(max=200), allow_none=True)
  prescriber = fields.Str(validate=validate.Length(max=200), allow_none=True)
  prescriber_phone = fields.Str(validate=validate.Length(max=200), allow_none=True)
  pharmacy = fields.Str(validate=validate.Length(max=200), allow_none=True)
  pharmacy_phone = fields.Str(validate=validate.Length(max=200), allow_none=True)

  drug_quantity = fields.Str(validate=validate.Length(max=10), allow_none=True)
  last_fill_date = fields.Date(allow_none=True)
  day_supply_of_fill = fields.Str(validate=validate.Length(max=10), allow_none=True)
  refill_due_date = fields.Date(allow_none=True)

  lis = fields.Str(validate=validate.Length(max=10), allow_none=True)
  days_missed_in_last_45_days = fields.Str(validate=validate.Length(max=10), allow_none=True)
  days_of_therapy_missed_ytd = fields.Str(validate=validate.Length(max=10), allow_none=True)
  allowable_days_remaining = fields.Str(validate=validate.Length(max=10), allow_none=True)

  adherence_forecast = fields.Str(validate=validate.Length(max=10), allow_none=True)

  @post_load
  def make_med_ad_struct(self, data):
    return MedicationAdherenceStatusStruct(**data)
