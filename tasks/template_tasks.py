from prefect import task, context
from typing import List, Tuple
import prefect
MemberNumberList = List[str]


@task
def pre_screen(configuration_id) -> MemberNumberList:
  logger = prefect.context.get("logger")
  logger.info("Pre screening patients to include in etl")
  return []

@task
def extract(member_number_filter=None) -> Tuple[List[str], List[str]]:
  logger = prefect.context.get("logger")
  logger.info("performing extract")
  return ([], [])

@task
def transfer(patients: List[str], claims: List[str]) -> List[str]:
  logger = prefect.context.get("logger")
  logger.info("performing transfer")
  return [patients + claims]
  
@task
def load(patient_roster: List[str]):
  logger = prefect.context.get("logger")
  logger.info("performing load")
  
@task
def post_load_orphan(member_number_list: MemberNumberList):
  logger = prefect.context.get("logger")
  logger.info("performing orphaning")

  
  
  
  
