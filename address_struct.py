from marshmallow import Schema, fields, post_load, validate


class AddressStruct:

  def __init__(self,
               address1: str,
               address2: str,
               city: str,
               state: str,
               zip: str,
               phone_number: str,
               secondary_phone_number: str = "") -> None:
    """
    We consider a valid address to have State and Zip set. All other fields
    can be left blank.
    """
    self.address1 = address1
    self.address2 = address2

    self.city = city
    self.state = state
    self.zip = zip

    self.phone_number = phone_number
    self.secondary_phone_number = secondary_phone_number


class AddressStructSchema(Schema):
  state = fields.Str(required=True, allow_none=False, validate=validate.Length(max=50))
  zip = fields.Str(required=True, allow_none=False, validate=validate.Length(max=50))

  address1 = fields.Str(required=True, allow_none=True)
  address2 = fields.Str(required=True, allow_none=True)

  city = fields.Str(required=True, allow_none=True)

  phone_number = fields.Str(required=True, validate=validate.Length(max=20))
  fax_number = fields.Str(required=False, validate=validate.Length(max=20))
  secondary_phone_number = fields.Str(required=True, validate=validate.Length(max=20))

  @post_load
  def make_address_struct(self, data):
    return AddressStruct(**data)
