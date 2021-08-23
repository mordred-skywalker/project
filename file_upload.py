
import os
import json
import datetime
from enum import Enum


class Datasets(Enum):
	SUPPLY_USAGE = "hospital-supply-usage.csv"
	PRICING = "pricing.csv"
	PATIENT_EXTRACT1 = "patients-extract1.xlsx"
	PATIENT_EXTRACT2 = "patients-extract2.xlsx"
	MEDICATIONS = "medications.json"
	MEDICATION_ADMINISTRATIONS = "medication-administrations.json"
	RAW_NOTE = "raw-sample-note.txt"
	PARSED_NOTE = "parsed-sample-note.json"
	PROCEDURES = "procedure_log.csv"


def get_data_dir():
	return os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")


def get_data_file(dataset):
	return os.path.join(get_data_dir(), dataset.value)

class TestJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return obj.isoformat()
		# Let the base class default method raise the TypeError
		return json.JSONEncoder.default(self, obj)

def save_json(data, filepath):
	with open(filepath, "w") as f:
		json.dump(data, f, indent=4, cls=TestJSONEncoder)

