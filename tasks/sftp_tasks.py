import os
import stat
from typing import Tuple

import paramiko
import prefect
from prefect import task


EXCLUDED_FILES = [
  'authorized_keys',
  'id_rsa',
  'id_rsa.pub',
  'keys',
]
EXCLUDED_DIRECTORIES = ['.', '..', '.ssh']


@task(nout=2)
def extract_directories(
        hostname,
        port,
        username,
        password,
        path,
) -> Tuple[set, set]:
  logger = prefect.context.get('logger')

  logger.info('Connecting to SFTP')
  ssh_client = paramiko.SSHClient()
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh_client.connect(hostname, port, username, password)

  sftp_client = ssh_client.open_sftp()
  dirs, files = _get_all_directories_files(sftp_client, path, logger)

  logger.info(f'Directories: {dirs}')
  logger.info(f'Files: {files}')

  return dirs, files


def _get_all_directories_files(sftp_client, path, logger):
  dirs = set()
  files = set()

  for fileattr in sftp_client.listdir_attr(path):
    if stat.S_ISDIR(fileattr.st_mode):
      dirs.add(fileattr.filename)
    else:
      files.add(fileattr.filename)

  resp_dirs = {path}
  resp_files = {
    (path, file) for file in files
    if not file.lower() in EXCLUDED_FILES
  }

  for directory in dirs:
    # SftpClient does not return "." and ".." as directories, but we're doing
    # this just to make sure that some clients are not weirder than others,
    # because this would lead to a stack overflow in recursion.
    if directory not in EXCLUDED_DIRECTORIES:
      full_path = os.path.join(path, directory)
      temp_dirs, temp_files = _get_all_directories_files(
        sftp_client,
        full_path,
        logger,
      )
      resp_dirs |= temp_dirs
      resp_files |= temp_files

  return resp_dirs, resp_files


@task(nout=3)
def get_existing_datasets(directories: set) -> Tuple[dict, dict, dict]:
  # TODO: GET /businessentity/<sftp_username>/data/sets?internal_names=<directories>
  # TODO: categorize directories based on datasets response
  new_directories = {}
  monitoring_directories = {}
  not_monitoring_directories = {}

  return new_directories, monitoring_directories, not_monitoring_directories


@task
def post_dataset(directory: str, sftp_username: str):
  # TODO: POST /businessentity/<sftp_username>/data/sets
  # TODO: return response
  pass
