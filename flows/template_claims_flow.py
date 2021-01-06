from prefect import Parameter, utilities
from prefect.core.flow import Flow
from tasks import extract, pre_screen, transfer, load, post_load_orphan
import logging

log = utilities.logging.get_logger()
with Flow("{{Client}} Claims ETL") as flow:
  configuration_id = Parameter("configuration_id")

  # log.info(f"Running claims ETL with configuration {configuration_id}.")
  member_list = pre_screen(configuration_id)
  extracted_data = extract(member_list)
  patient_roster = transfer(extracted_data[0], extracted_data[1])
  l = load(patient_roster=patient_roster)
  post_load_orphan(member_number_list=member_list, upstream_tasks=[l])

flow.register()

