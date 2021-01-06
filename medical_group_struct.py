from typing import Optional, List, Dict

from marshmallow import Schema, fields, post_load, validate
from address_struct import AddressStruct, AddressStructSchema
from office_struct import OfficeStruct, OfficeStructSchema



class MedicalGroupStruct:

  def __init__(self,
               tin: str,
               name: str,
               address: AddressStruct = None,
               offices: List[OfficeStruct] = None) -> None:
    self.tin = tin
    self.name = name

    if address:
      self.address = address

    self.offices = offices or []

  def __str__(self):
    return self.name

  @property
  def tin(self) -> str:
    return self.__tin

  @tin.setter
  def tin(self, tin: str):
    self.__tin = tin.replace("-", "")

  def name_is_missing(self) -> bool:
    """
    Returns True if this Medical Group has a name set. Most ETL's set the
    name as '-' which might not be a good idea, but we are here now.

    More recently we've started populating medical group names that are missing
    with the TIN. Also kind of silly.
    """
    return self.name in ['', '-'] or self.name.startswith('-') or self.name is None

  def get_address(self) -> Optional[AddressStruct]:
    return getattr(self, "address", None)

  def get_office(self, uid):
    next((x for x in self.offices if x.uid == uid), None)

  def office_already_added(self, uid):
    return self.get_office(uid) is not None

  def data_complete(self):
    return not self.name_is_missing() and self.get_address() is not None and self.tin is not None


class MedicalGroupStructSchema(Schema):
  tin = fields.Str(required=True, allow_none=False, validate=validate.Length(max=20))
  name = fields.Str(required=True, allow_none=False, validate=validate.Length(max=200))

  address = fields.Nested(AddressStructSchema, allow_none=True)
  offices = fields.Nested(OfficeStructSchema, many=True)

  @post_load
  def make_medical_group_struct(self, data):
    return MedicalGroupStruct(**data)
