import json
import logging
import ee
import os

logger = logging.getLogger(__name__)
private_key_path = "geotest-privkey.json"
if not os.path.isfile(private_key_path):
    raise FileNotFoundError("geotest-privkey.json not found. This file should exists in utils.gee package.")

service_account = 'geo-test@geotest-317218.iam.gserviceaccount.com'
with open(private_key_path, 'r') as pk:
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json.dumps(json.load(pk)))
ee.Initialize(credentials)
