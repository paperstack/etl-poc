from prefect import Flow, utilities

from tasks import sftp_tasks as tasks

with Flow('SFTP') as flow:
  # TODO: Get these from Prefect context
  hostname = ''
  port = 22
  username = ''
  password = ''
  path = '/home/tsxmdpyhcbwfolqu/sftp'

  directories, files = tasks.extract_directories(
    hostname,
    port,
    username,
    password,
    path,
  )
  # TODO: process zip files
  new, monitoring, not_monitoring = tasks.get_existing_datasets(directories)

  # Create a new dataset for each new directory
  for directory in new.keys():
    tasks.post_dataset(directory, username)


flow.register(project_name='SFTP')
