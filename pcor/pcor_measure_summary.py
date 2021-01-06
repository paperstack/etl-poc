from datetime import date
from typing import Optional

from marshmallow import Schema, fields, post_load


class PcorMeasureSummaryStruct:
  def __init__(self,
               as_of_date: date,
               performance_year: int,
               measure_code: str,
               tin: str,
               plan_id: int,
               eligible_members: Optional[int],
               compliant_members: Optional[int],
               non_compliant_members: Optional[int],
               current_rate: str,
               five_star_threshold_percent_target: str,
               num_members_to_achieve_five_star_treshold: Optional[int],
               quality_rating: Optional[int],
               cms_weight: Optional[int],
               cms_weighted_quality_rating: Optional[int]) -> None:

    self.as_of_date: date = as_of_date
    self.performance_year = performance_year
    self.measure_code: str = measure_code
    self.tin: str = tin
    self.plan_id = plan_id
    self.eligible_members: Optional[int] = eligible_members
    self.compliant_members: Optional[int] = compliant_members
    self.non_compliant_members: Optional[int] = non_compliant_members
    self.current_rate: str = current_rate
    self.five_star_threshold_percent_target: str = five_star_threshold_percent_target
    self.num_members_to_achieve_five_star_treshold: Optional[int] = num_members_to_achieve_five_star_treshold
    self.quality_rating: Optional[int] = quality_rating
    self.cms_weight: Optional[int] = cms_weight
    self.cms_weighted_quality_rating: Optional[int] = cms_weighted_quality_rating

  def key(self):
    return f"{self.tin}{self.as_of_date}{self.measure_code}"


class PcorMeasureSummaryStructSchema(Schema):
  as_of_date = fields.Date(required=True)
  performance_year = fields.Int(required=True)

  measure_code = fields.Str(required=True)
  tin = fields.Str(required=True)
  plan_id = fields.Int(required=True)

  eligible_members = fields.Int(required=True, allow_none=True)
  compliant_members = fields.Int(required=True, allow_none=True)
  non_compliant_members = fields.Int(required=True, allow_none=True)

  current_rate = fields.Str(required=True)
  five_star_threshold_percent_target = fields.Str(required=True)
  num_members_to_achieve_five_star_treshold = fields.Int(required=True, allow_none=True)
  quality_rating = fields.Int(required=True, allow_none=True)
  cms_weight = fields.Int(required=True, allow_none=True)
  cms_weighted_quality_rating = fields.Int(required=True, allow_none=True)

  @post_load
  def make_group_summary_struct(self, data):
    return PcorMeasureSummaryStruct(**data)


class PcorMeasureSummaryUpdateStruct(Schema):
  def __init__(self,
               num_existing: int = 0,
               num_created: int = 0) -> None:

    self.num_existing: int = num_existing
    self.num_created: int = num_created


class PcorMeasureSummaryUpdateStructSchema(Schema):
  num_existing = fields.Int(required=True)
  num_created = fields.Int(required=True)

  @post_load
  def make_pcor_summary_update_struct(self, data):
    return PcorMeasureSummaryUpdateStruct(**data)
