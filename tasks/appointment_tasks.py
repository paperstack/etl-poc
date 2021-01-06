from prefect import task, context
from typing import List, Dict
import prefect
from tasks.external_appointment_struct import ExternalAppointmentStruct
from prefect.engine.results.prefect_result import PrefectResult
from stlukes_mappings import StLukesEtlAppointmentMapping
import common_io
from stlukes_constants import APPOINTMENTS_XWALK
import requests
from external_appointment_update_summary_struct import ExternalAppointmentUpdateSummaryStruct,\
  ExternalAppointmentUpdateSummaryStructSchema
from external_appointment_struct import ExternalAppointmentStructSchema
import common
import json



@task
def extract_nodes(input_file_path: str) -> List[ExternalAppointmentStruct]:
  logger = prefect.context.get("logger")
  logger.info("extracting nodes")
  appointments = []
  mapping = StLukesEtlAppointmentMapping()
  df = common_io.read_csv_fast(input_file_path,
                               columns=mapping.columns(),
                               sep='|',
                               parse_dates=[mapping.appointment_date,
                                            mapping.date_of_birth,
                                            mapping.external_created_date,
                                            mapping.external_last_modified_date])

  for i in df.index:
    row = df.loc[i]

    appointment = mapping.get_appointment_struct(row)
    appointment.plan_id = 1

    # TODO: We hardcode this for now as a placeholder until we figure out
    # a proper approach to St. Lukes and others going forward
    appointment.appointment_timezone = 'America/Boise'

    # TODO: Remove once St. Lukes data is corrected or at least add config
    xwalk_id = APPOINTMENTS_XWALK.get(appointment.appointment_location_id)
    appointments.append(appointment)

  return appointments


@task
def build_graphs(nodes: List[ExternalAppointmentStruct]) -> List[ExternalAppointmentStruct]:
  logger = prefect.context.get("logger")
  logger.info("building graphs")
  for node in nodes:
    logger.info(f"Got appt for {node.first_name} {node.last_name}")

  return nodes


@task
def post_graph(appointment: ExternalAppointmentStruct) -> Dict:
  logger = prefect.context.get("logger")
  s = ExternalAppointmentUpdateSummaryStruct()
  external_appointment_schema = ExternalAppointmentStructSchema()
  external_appointment_update_schema = ExternalAppointmentUpdateSummaryStructSchema()

  json_data = external_appointment_schema.dump(appointment)
  
  summary: ExternalAppointmentUpdateSummaryStruct
  summary, err = common.post_to_endpoint(1, json_data,
                                         '/api/external_appointment/update',
                                         external_appointment_update_schema,
                                         commit=False)
  
  return summary

@task(result=PrefectResult())
def aggregate_summaries(summaries: List[ExternalAppointmentUpdateSummaryStruct]) -> Dict:
  logger = prefect.context.get("logger")
  result = ExternalAppointmentUpdateSummaryStruct()
  for summary in summaries:
    result.num_new_appointments += summary.num_new_appointments
    result.num_valid_appointments += summary.num_valid_appointments
    result.num_existing_appointments += summary.num_existing_appointments
    result.num_dropped_appointments += summary.num_dropped_appointments
    result.details.extend(summary.details)
  
  return ExternalAppointmentUpdateSummaryStructSchema().dump(result)



