from marshmallow import Schema, fields, post_load, validate


class ProcedureStruct:

  def __init__(self, claim_number: str, member_number: str, code: str) -> None:
    self.claim_number = claim_number
    self.member_number = member_number
    self.code = code


class ProcedureStructSchema(Schema):
  claim_number = fields.Str(required=True, validate=validate.Length(max=50))
  member_number = fields.Str(required=True, validate=validate.Length(max=200))
  code = fields.Str(required=True, validate=validate.Length(max=34))

  @post_load
  def make_procedure_struct(self, data):
    return ProcedureStruct(**data)
