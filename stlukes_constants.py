# NOTE: If you are adding file types in here, also add them in
#  models/data_set.py, otherwise the ETL will not recognize the data set.
DEMOGRAPHICS_FILE = 'patients'
CLAIMS_FILE = 'claims'
CLAIMS_DIAGS_FILE = 'diagnosis'
CLAIMS_PROCS_FILE = 'procs'
RX_CLAIMS_FILE = 'rx_claims'
PROVIDERS_FILE = 'providers'
ADT_EVENTS_FILE = 'adt_events'
APPOINTMENTS_FILE = 'appointments'

# used for ADT Etl
DEFAULT_SEP = '|'

DEMOGRAPHICS_MEMBER_NUMBER = 'EDWPatientID'

SELECT_HEALTH_VALUE = 'SelectHealth-Medicare Advantage-SLHC'
ALL_SUPPORTED_PLANS = [
  SELECT_HEALTH_VALUE
]

# TODO: Remove once St. Lukes data is corrected
APPOINTMENTS_XWALK = {
  "10101186": "4422",
  "10101101": "4465",
  "10622000": "231182",
  "10621000": "297184",
  "10428005": "307572",
  "10409150": "321359",
  "10444001": "321359",
  "10187114": "405523",
  "10302102": "4324",
  "10303100": "4335",
  "10201132": "4341",
  "10203100": "4342",
  "10206100": "4343",
  "10201101": "4345",
  "10201102": "4355",
  "10153110": "4399",
  "10111100": "4405",
  "10140100": "4419",
  "10140125": "4419",
  "10129101": "4421",
  "10163100": "4424",
  "10153111": "4425",
  "10125101": "4426",
  "10613001": "4427",
  "10109100": "4455",
  "10140121": "4462",
  "10122100": "4466",
  "10133106": "4468",
  "10150105": "4469",
  "10103104": "4488",
  "10146100": "4547",
  "10112100": "4548",
  "10131100": "4550",
  "10103117": "4551",
  "10133119": "4551",
  "10132112": "4576",
  "10119100": "4586",
  "10165132": "500213",
  "10433002": "5951",
  "10415108": "5958",
  "10440006": "5959",
  "10400177": "5962",
  "10415110": "5969",
  "10415111": "5971",
  "10444006": "5972",
  "10428001": "5973",
  "10409130": "5975",
  "10409127": "5988"
}
