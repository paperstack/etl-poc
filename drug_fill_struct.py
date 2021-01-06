from datetime import date
from typing import Optional

from marshmallow import Schema, fields, post_load, validate

from sfe.api_data.drug_struct import DrugStruct, DrugStructSchema


class DrugFillStruct:

  def __init__(self,
               claim_number: str,
               member_number: str,
               ndc: str,
               refill_number: Optional[int],
               days_supply: Optional[int],
               quantity_dispensed: Optional[int],
               drug: DrugStruct = None,
               refills_authorized: int = None,
               script_written_date: date = None,
               fill_date: date = None) -> None:
    self.claim_number = claim_number
    self.member_number = member_number

    # National Drug Code - https://www.accessdata.fda.gov/scripts/cder/ndc/
    self.ndc = ndc

    # Some prescriptions can be filled multiple times, this tells us how many
    # times has this prescription been filled so far.
    self.refill_number = refill_number
    self.refills_authorized = refills_authorized
    self.script_written_date = script_written_date
    self.fill_date = fill_date

    self.days_supply = days_supply
    self.quantity_dispensed = quantity_dispensed

    self.drug: DrugStruct = drug


class DrugFillStructSchema(Schema):
  claim_number = fields.Str(required=True, allow_none=False, validate=validate.Length(max=50))
  member_number = fields.Str(required=True, allow_none=False, validate=validate.Length(max=200))

  ndc = fields.Str(required=True, allow_none=False, validate=validate.Length(max=20))

  refill_number = fields.Int(required=True, allow_none=True)
  refills_authorized = fields.Int(allow_none=True)
  script_written_date = fields.Date(allow_none=True)

  days_supply = fields.Int(required=True, allow_none=True)
  quantity_dispensed = fields.Int(allow_none=True)

  drug = fields.Nested(DrugStructSchema)

  @post_load
  def make_drug_fill_struct(self, data):
    return DrugFillStruct(**data)
