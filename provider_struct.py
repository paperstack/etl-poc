from marshmallow import Schema, fields, post_load, validate
from typing import Set
from medical_group_struct import MedicalGroupStruct, MedicalGroupStructSchema




class ProviderStruct:

  def __init__(self,
               first_name: str,
               last_name: str,
               npi: str,
               medical_group: MedicalGroupStruct = None,
               supported_offices_uids: Set[str] = None) -> None:
    self.first_name: str = first_name
    self.last_name: str = last_name

    self.npi: str = npi

    # Important Note: This is the provider that this PCP was practicing at
    # the time when we ingested the data. It is possible that individual claims
    # could happen at different NPI/TIN association.
    self.medical_group: MedicalGroupStruct = medical_group

    self.supported_offices_uids = supported_offices_uids or set()

  def name(self):
    if self.first_name or self.last_name:
      return self.first_name + ' ' + self.last_name
    else:
      return '- -'


class ProviderStructSchema(Schema):

  first_name = fields.Str(validate=validate.Length(max=200))
  last_name = fields.Str(validate=validate.Length(max=200))

  npi = fields.Str(required=True, validate=validate.Length(max=20))

  medical_group = fields.Nested(MedicalGroupStructSchema)

  supported_offices_uids = fields.List(fields.Str())

  @post_load
  def make_provider_struct(self, data):
    return ProviderStruct(**data)
