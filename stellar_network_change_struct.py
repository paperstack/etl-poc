import structlog
from marshmallow import Schema, fields, post_load

log = structlog.get_logger()


class StellarNetworkChangeStruct:
  """
  Describes a change to the Provider<>MedicalGroup Stellar Network.

  This change is Provider centric - and will capture Providers that are in the
  stellar network, whether they are new to it or not, what Medical Groups
  they belong to, and whether that changed.
  """
  def __init__(self, provider_npi: str,
               provider_name: str,
               provider_new_to_stellar_network: bool,
               to_medical_group_tin: str,
               to_medical_group_name: str,
               from_medical_group_tin: str,
               from_medical_group_name: str) -> None:
    self.provider_npi: str = provider_npi
    self.provider_name: str = provider_name
    self.provider_new_to_stellar_network: bool = provider_new_to_stellar_network

    self.to_medical_group_tin: str = to_medical_group_tin
    self.to_medical_group_name: str = to_medical_group_name

    # If the FROM_TIN is the same as the TO_TIN then nothing has changed.
    self.from_medical_group_tin: str = from_medical_group_tin
    self.from_medical_group_name: str = from_medical_group_name


class StellarNetworkChangeStructSchema(Schema):

  provider_npi = fields.Str(required=True)
  provider_name = fields.Str(required=True)

  provider_new_to_stellar_network = fields.Bool()

  to_medical_group_tin = fields.Str(required=True)
  to_medical_group_name = fields.Str(required=True)

  from_medical_group_tin = fields.Str(required=True, allow_none=True)
  from_medical_group_name = fields.Str(required=True, allow_none=True)

  @post_load
  def make_network_change_struct(self, data):
    return StellarNetworkChangeStruct(**data)
