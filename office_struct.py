from marshmallow import Schema, fields, post_load, validate
from typing import Set
from address_struct import AddressStruct, AddressStructSchema



class OfficeStruct:

  def __init__(self,
               uid: str,
               name: str,
               address: AddressStruct) -> None:
    self.uid: str = uid
    self.name: str = name

    self.address: AddressStruct = address


class OfficeStructSchema(Schema):

  uid = fields.Str(validate=validate.Length(max=50))
  name = fields.Str(validate=validate.Length(max=200))

  address = fields.Nested(AddressStructSchema)

  @post_load
  def make_office_struct(self, data):
    return OfficeStruct(**data)
