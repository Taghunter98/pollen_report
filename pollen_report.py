import requests
import subprocess
import re
import os
from dotenv import load_dotenv

proc = subprocess.Popen(["gcloud auth application-default print-access-token"], stdout=subprocess.PIPE, shell=True)
(output, err) = proc.communicate()

output = re.sub("b'", '', str(output))
output = str(output)[:-3]


KEY = os.getenv('KEY')
TOKEN = f"Bearer {output}"
latitude = 51.055002
longitude = 0.571595

headers = {
    'X-Goog-User-Project': 'vmi-website-432609',
    'Authorization': TOKEN
}

url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={KEY}8&location.longitude={longitude}&location.latitude={latitude}&days=1"
result = requests.get(
    url, headers=headers
)

print(result.json())