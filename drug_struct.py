from marshmallow import Schema, fields, post_load, validate


class DrugStruct:

  def __init__(self,
               ndc: str,
               drug_name: str,
               gpi: str,
               gcn: str,
               brand_flag: str) -> None:
    # National Drug Code - https://www.accessdata.fda.gov/scripts/cder/ndc/
    self.ndc = ndc
    self.drug_name = drug_name

    # Generic Product Identifier
    self.gpi = gpi
    # Generic Code Number - generic formulation of a drug.
    self.gcn = gcn
    # Identifies whether the drug dispensed was paid at brand or generic
    # (based on the client-specific Drug File).
    self.brand_flag = brand_flag

  @property
  def drug_name(self):
    result = self.__drug_name[0:250] if self.__drug_name else self.__drug_name
    return result

  @drug_name.setter
  def drug_name(self, drug_name):
    self.__drug_name = drug_name[0:250] if drug_name else drug_name

  def has_drug_name(self):
    return self.drug_name not in ['-', '', None]


class DrugStructSchema(Schema):
  ndc = fields.Str(required=True, allow_none=False, validate=validate.Length(max=20))
  drug_name = fields.Str(required=True, allow_none=False, validate=validate.Length(max=250))

  gpi = fields.Str(required=True, allow_none=False, validate=validate.Length(max=200))
  gcn = fields.Str(required=True, allow_none=False, validate=validate.Length(max=200))
  brand_flag = fields.Str(required=True, allow_none=False, validate=validate.Length(max=20))

  @post_load
  def make_drug_struct(self, data):
    return DrugStruct(**data)
