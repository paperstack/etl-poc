from datetime import datetime

from io import StringIO
from typing import Dict, Set, List
import pandas as pd
import common



CHUNKSIZE = 2


'''if settings.SFE_ENV in ['testing', '']:
  log.debug("Setting CHUNKSIZE=2 for tests")
  CHUNKSIZE = 2
'''

# ----------------------------------------------------------------------
# Generic wrappers around common operations that we do

def values_from_column(csv_file: str,
                       column_name: str,
                       sep: str = ",") -> Set[str]:
  """
  Extracts all the values from a column of a file that represents a CSV, and
  returns them as a Set.
  """
  df = read_csv(csv_file, [column_name], sep=sep)
  return set(df[column_name])


# ----------------------------------------------------------------------
# Pandas wrappers for doing chunking.

def read_fwf(file: str,
             mapping: Dict[str, str],
             columns: List[str],
             filter_column_values: Set[str],
             filter_column_name: str) -> pd.DataFrame:
  """
  Returns a data frame that contains the columns in the parameters list, and
  only the row that match the `only_member_numbers` list for the column
  that is passed in as a parameter.
  """
  iterator = pd.read_fwf(
    StringIO(file.contents),
    widths=mapping.values(),
    header=None,
    names=mapping.keys(),
    dtype=str,
    keep_default_na=False,
    chunksize=CHUNKSIZE,
    iterator=True,
    usecols=columns
  )

  return _concat_df(iterator, filter_column_values, filter_column_name)


def read_csv(file: str,
             columns: List[str],
             filter_column_values: Set[str] = None,
             filter_column_name: str = None,
             sep: str = ",",
             parse_dates: List[str] = None) -> pd.DataFrame:
  """
  Returns a data frame that contains the columns in the parameters list, and
  only the row that match the `only_member_numbers` list for the column
  that is passed in as a parameter.

  NOTE: passing a custom_date_parser to pandas.read_csv is slow for several
  reasons 1) it parses the entire file whereas the returned data could be only
  a fraction of the file 2) the custom date parser itself is very slow as it
  attempts several date formats 3) pandas code calls native methods much faster
  than python code

  BUT this custom_date_parser is able to better deal with cases of extreme
  date values like 01/01/8888 whereas pandas will only parse dates before year
  2262. Such extreme date values where encountered in Ampersand data.

  SEE read_csv_fast for the much faster version of this function that only
  deals with dates before year 2262 and returns None for valid dates after that
  year.
  """
  def custom_date_parser(value):
    d = common.parse_date(value)
    if not d:
      # If this was not a date - and instead was something empty - return None.
      return None

    if d.year > 2100:
      d = datetime(2100, d.month, d.day)
    return d

  iterator = pd.read_csv(
    StringIO(file.contents),
    header=0,
    dtype=str,
    keep_default_na=False,
    chunksize=CHUNKSIZE,
    iterator=True,
    usecols=columns,
    sep=sep,
    parse_dates=parse_dates,
    date_parser=custom_date_parser
  )

  return _concat_df(iterator, filter_column_values, filter_column_name)


def read_csv_fast(file: str,
                  columns: List[str],
                  filter_column_values: Set[str] = None,
                  filter_column_name: str = None,
                  sep: str = ",",
                  parse_dates: List[str] = None) -> pd.DataFrame:
  """
  Offers the same functionality as read_csv but doesn't deal with dates after
  year 2262. Any such date, even if valid, will be replaced with None.
  """
  iterator = pd.read_csv(
    file,
    header=0,
    dtype=str,
    keep_default_na=False,
    chunksize=CHUNKSIZE,
    iterator=True,
    usecols=columns,
    sep=sep,
  )

  concat_df = _concat_df(iterator, filter_column_values, filter_column_name)

  for col in parse_dates or []:
    concat_df[col] = pd.to_datetime(concat_df[col], errors='coerce')

  return concat_df


def _concat_df(iterator,
               filter_column_values: Set[str],
               filter_column_name: str) -> pd.DataFrame:
  """
  Returns a data frame with all the rows that have the filter_column_values
  in the filter_column_name column.

  The method assumes that the iterator has chunking set and will iterate over
  all the chunks of the data frame.

  There are certain cases where it is unknown if the filter column
  will be present but if it is filtering should be applied. Such
  a scenario will be handled gracefully.
  """
  if filter_column_values:
    df = pd.concat([
      chunk[chunk[filter_column_name].isin(filter_column_values)]
      if filter_column_name in chunk else chunk
      for chunk in iterator
    ])
  else:
    df = pd.concat([chunk for chunk in iterator])

  return df
