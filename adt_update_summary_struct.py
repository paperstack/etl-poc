from typing import List

from marshmallow import Schema, fields, post_load

from datetime import date


class AdtUpdateSummaryStruct:
  """Summary of data updates for inserting / adding a new ADT event."""

  def __init__(self,
               num_valid_events: int = 0,
               num_new_events: int = 0,
               num_existing_events: int = 0,
               num_dropped_events: int = 0,
               new_events_min_date: date = None,
               new_events_max_date: date = None,
               details: List[str] = None) -> None:
    self.num_valid_events: int = num_valid_events

    self.num_new_events: int = num_new_events
    self.num_existing_events: int = num_existing_events
    self.num_dropped_events: int = num_dropped_events

    self.new_events_min_date: date = new_events_min_date
    self.new_events_max_date: date = new_events_max_date

    self.details = details or []


class AdtUpdateSummaryStructSchema(Schema):

  num_valid_events = fields.Int()
  num_new_events = fields.Int()
  num_existing_events = fields.Int()
  num_dropped_events = fields.Int()

  new_events_min_date = fields.Date(required=False, allow_none=True)
  new_events_max_date = fields.Date(required=False, allow_none=True)

  details = fields.List(fields.Str(), allow_none=True)

  @post_load
  def make_adt_update_summary_struct(self, data):
    return AdtUpdateSummaryStruct(**data)
