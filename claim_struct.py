from typing import List, Optional

from datetime import datetime, date
from decimal import Decimal

from marshmallow import Schema, fields, post_load, validate
from diagnosis_struct import DiagnosisStruct, DiagnosisStructSchema
from drug_fill_struct import DrugFillStruct, DrugFillStructSchema
from procedure_struct import ProcedureStruct, ProcedureStructSchema




class ClaimStruct:

  def __init__(self,
               claim_number: str,
               claim_type: str,
               member_number: str,
               from_date: datetime,
               thru_date: datetime,
               provider_npi: str = None,
               medical_group_tin: str = None,
               setting: str = None,
               diagnoses: List[DiagnosisStruct] = None,
               procedures: List[ProcedureStruct] = None,
               pharmacy_npi: str = None,
               pharmacy_name: str = None,
               prescribing_npi: str = None,
               prescribing_tin: str = None,
               drug_fills: List[DrugFillStruct] = None,
               amount_gross: Decimal = None,
               amount_paid: Decimal = None,
               admission_date: date = None,
               discharge_date: date = None,
               revenue_code: str = None,
               drg_code: str = None,
               drg_type: str = None,
               hcg_code: str = None,
               status_code: str = None,
               plan_name: str = None) -> None:

    self.claim_number: str = claim_number
    self.claim_type: str = claim_type
    self.member_number: str = member_number

    self.from_date: datetime = from_date
    self.thru_date: datetime = thru_date

    # If this is a Claim for a procedure and a series of Diagnoses, these two
    # fields will represent the provider and medical group that did that
    # procedure.
    #
    # For Claims that represent Prescriptions (RX Claims), these fields will
    # be None. We use a separate field for the pharmacy that filled that
    # prescription.
    self.provider_npi: str = provider_npi
    self.medical_group_tin: str = medical_group_tin

    self.setting: str = setting

    self.diagnoses: List[DiagnosisStruct] = diagnoses or []
    self.procedures: List[ProcedureStruct] = procedures or []

    # The pharmacy where the Drug Fill happened. If a claim is a DrugFill claim,
    # the pharmacy_npi is the one that is considered to have 'performed' the
    # claim, the provider_npi field will be None, and the prescribing_npi field
    # will hold the Provider that prescribed these drugs.
    #
    # NOTE(octavian): You will not find this field on the Claim model because
    # as we import data, we set the Pharmacy Provider as the claim.provider
    # field. In our DB the `claim.provider` represents the Provider that was
    # paid for this claim - in the case of a Procedure that's a Doctor
    # performing it, and in the case of a Drug Fill that's a Pharmacy filling
    # it.
    self.pharmacy_npi: str = pharmacy_npi
    self.pharmacy_name: str = pharmacy_name

    # For pharmacy claims, we also record the prescribing NPI. We want to avoid
    # overloading the provider_npi field that has a very clear meaning as the
    # provider that performed the procedure in a Claim.
    self.prescribing_npi: str = prescribing_npi
    self.prescribing_tin: str = prescribing_tin

    # just like there's only one Procedure per Claim most of the time - for
    # rx claims each claim represents one drug fill most of the time.
    self.drug_fills: List[DrugFillStruct] = drug_fills or []

    # For now filled only for Prescriptions, but maybe in the near term future
    # we can start using this for regular Claims too.
    self.amount_gross: Decimal = amount_gross
    self.amount_paid: Decimal = amount_paid

    # Hospital claims might have these fields.
    if admission_date:
      self.admission_date: date = admission_date
    if discharge_date:
      self.discharge_date: date = discharge_date

    # Hospital Revenue Codes. For more information, look at models.Claim.
    if revenue_code is not None:
      self.revenue_code: str = revenue_code

    # Diagnosis Related Groups code. For more information, look at models.Claim.
    if drg_code is not None:
      self.drg_code: str = drg_code
    if drg_type is not None:
      self.drg_type: str = drg_type

    # Health Cost Guidelines code. Learn more at models.Claim.
    if hcg_code is not None:
      self.hcg_code: str = hcg_code

    if status_code is not None:
      self.status_code: str = status_code

    if plan_name is not None:
      self.plan_name: str = plan_name

  # -------------------------------------------------------------------
  # Getters for fields that are not always present on the struct

  def get_admission_date(self) -> Optional[date]:
    return getattr(self, "admission_date", None)

  def get_discharge_date(self) -> Optional[date]:
    return getattr(self, "discharge_date", None)

  def get_revenue_code(self) -> Optional[str]:
    return getattr(self, "revenue_code", None)

  def get_drg_code(self) -> Optional[str]:
    return getattr(self, "drg_code", None)

  def get_drg_type(self) -> Optional[str]:
    return getattr(self, "drg_type", None)

  def get_hcg_code(self) -> Optional[str]:
    return getattr(self, "hcg_code", None)

  def get_status_code(self) -> Optional[str]:
    return getattr(self, "status_code", None)

  def get_plan_name(self) -> Optional[str]:
    return getattr(self, "plan_name", None)

  # ------------------------------------------------------------------
  # Utility functions

  """def maybe_add_diagnosis(self, code: str) -> List[str]:
    # TODO(octavian): Remove the errors returned - because this always returns
    #   an empty list.
    code = HedisCode.normalize_icd_code(code)

    if self.has_diagnosis_code(code):
      return []

    d = DiagnosisStruct(
      claim_number=self.claim_number,
      member_number=self.member_number,
      code=code,
      code_type=icd.detect_icd_code(code)
    )
    self.diagnoses.append(d)
    return []
"""
  def has_diagnosis_code(self, code: str) -> bool:
    for d in self.diagnoses:
      if d.code == code:
        return True
    return False

  def maybe_add_procedure(self, code: str) -> List[str]:
    if self.has_procedure_code(code):
      return []

    #if not Procedure.is_valid_code(code):
    #  return ["%s is not a valid procedure code" % code]

    p = ProcedureStruct(
      claim_number=self.claim_number,
      member_number=self.member_number,
      code=code
    )
    self.procedures.append(p)
    return []

  def has_procedure_code(self, code: str) -> bool:
    for p in self.procedures:
      if p.code == code:
        return True
    return False

  def set_member_number(self, member_number: str):
    self.member_number = member_number
    for p in self.procedures:
      p.member_number = member_number
    for d in self.diagnoses:
      d.member_number = member_number

  def maybe_add_procedures_and_diagnoses_from_claim(self, new_claim):
    for d in new_claim.diagnoses:
      self.maybe_add_diagnosis(d.code)

    for p in new_claim.procedures:
      self.maybe_add_procedure(p.code)

  def key(self) -> str:
    # Note: The IPANS ETL has duplicate claim numbers for different patients
    # in the RX Claims file. As far as we can tell, this is not a common
    # occurrence across files or ETLs, but it will be a good idea to move
    # away from the assumption that claim numbers are unique.
    return f"{self.member_number}-{self.claim_number}"


class ClaimStructSchema(Schema):

  claim_number = fields.Str(required=True, validate=validate.Length(max=50))
  claim_type = fields.Str(required=True, validate=validate.Length(max=16))
  member_number = fields.Str(required=True, validate=validate.Length(max=200))

  from_date = fields.DateTime(required=True)
  thru_date = fields.DateTime(required=True)

  provider_npi = fields.Str(allow_none=True)
  medical_group_tin = fields.Str(allow_none=True)

  setting = fields.Str(allow_none=True)

  diagnoses = fields.Nested(DiagnosisStructSchema, many=True)
  procedures = fields.Nested(ProcedureStructSchema, many=True)

  # Fields that are particular to RX Claims.
  pharmacy_npi = fields.Str(allow_none=True)
  pharmacy_name = fields.Str(allow_none=True, validate=validate.Length(max=250))

  prescribing_npi = fields.Str(allow_none=True)
  prescribing_tin = fields.Str(allow_none=True)

  drug_fills = fields.Nested(DrugFillStructSchema, many=True, allow_none=True)

  # Cost related fields.
  amount_gross = fields.Decimal(places=2, allow_none=True)
  amount_paid = fields.Decimal(places=2, allow_none=True)

  # Sometimes hospital claims will have these.
  admission_date = fields.Date()
  discharge_date = fields.Date()

  # Unique 4 Digit Numbers
  revenue_code = fields.Str(validate=validate.Length(max=4))

  drg_code = fields.Str(validate=validate.Length(max=3))
  drg_type = fields.Str(validate=validate.Length(max=50))
  hcg_code = fields.Str(validate=validate.Length(max=10))

  status_code = fields.Str(validate=validate.Length(max=10))
  plan_name = fields.Str(validate=validate.Length(max=200))

  @post_load
  def make_claim_struct(self, data):
    return ClaimStruct(**data)
