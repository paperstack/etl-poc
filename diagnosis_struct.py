from marshmallow import Schema, fields, post_load, validate


class DiagnosisStruct:

  def __init__(self,
               claim_number: str,
               member_number: str,
               code: str,
               code_type: str) -> None:
    self.claim_number = claim_number
    self.member_number = member_number
    self.code = code
    self.code_type = code_type


class DiagnosisStructSchema(Schema):
  claim_number = fields.Str(required=True, allow_none=False, validate=validate.Length(max=50))
  member_number = fields.Str(required=True, allow_none=False, validate=validate.Length(max=200))
  code = fields.Str(required=True, allow_none=False)
  code_type = fields.Str(required=True, allow_none=False, validate=validate.Length(max=20))

  @post_load
  def make_diagnosis_struct(self, data):
    return DiagnosisStruct(**data)
