import requests
import subprocess
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

proc = subprocess.Popen(["gcloud auth print-access-token"], stdout=subprocess.PIPE, shell=True)
(output, err) = proc.communicate()

output = re.sub("b'", '', str(output))
output = str(output)[:-3]

load_dotenv()
KEY = os.getenv('KEY')
TOKEN = f"Bearer {output}"
PROJECT_ID = os.getenv('PROJECT_ID')
latitude = 51.055002
longitude = 0.571595

headers = {
    'X-Goog-User-Project': PROJECT_ID,
    'Authorization': TOKEN
}

url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={KEY}8&location.longitude={longitude}&location.latitude={latitude}&days=1"
result = requests.get(
    url, headers=headers
)

class PollenType():
    def __init__(self, object):
        self.obj = object
        self.code = object['code']
        self.displayName = object['displayName']
        if 'inSeason' in object:
            self.inSeason = object['inSeason']
        
        if 'indexInfo' in object:
            self.indexInfo = object['indexInfo']

            if 'category' in self.indexInfo:
                self.category = self.indexInfo['category']
        
            if 'indexDescription' in self.indexInfo:
                self.information = self.indexInfo['indexDescription']

    def print(self):
        if 'inSeason' in self.obj:
            print(f"\nCODE: {self.obj['code']}\nNAME: {self.obj['displayName']}\nSEASON: In Season\n")

    def createHTML(self, colour):
        html =  f"""\n
            <li>
                <span class="material-symbols-outlined"> psychiatry </span>
                <div class="element">
                    <h3>{self.displayName}</h3>
                    <span
                        style="
                        height: 25px;
                        width: 25px;
                        background-color: {colour};
                        border-radius: 50%;
                        display: inline-block;
                    "
                    ></span>
                </div>
                <p>{self.information}</p>
            </li>
        """

        return str(html)
        
    def colour(self):
        if hasattr(self, 'indexInfo'):
            value = self.indexInfo['value']
            if value == 0:
                return "rgb(218, 218, 218)"
            elif value == 1:
                return "rgb(4, 157, 60)"
            elif value == 2:
                return "rgb(59, 180, 81)"
            elif value == 3:
                return "rgb(251, 255, 0)"
            elif value == 4:
                return "rgb(255, 144, 0)"
            else:
                return "rgb(247, 45, 3)"
        else:
            return
            

data = result.json()
pollen_types = data["dailyInfo"][0]["plantInfo"]
pollen_data = []

for key in pollen_types:
    pollen_type = PollenType(key)
    colour = pollen_type.colour()
    if colour is not None:
        pollen_data.append(pollen_type)
        
# Order pollen data based on colour
new_arr = [[] for i in range(6)]
for item in pollen_data:
    colour = item.colour()

    grey = "rgb(218, 218, 218)"
    dark_green = "rgb(4, 157, 60)"
    green = "rgb(59, 180, 81)"
    yellow = "rgb(251, 255, 0)"
    orange = "rgb(255, 144, 0)"
    red =  "rgb(247, 45, 3)"

    if colour == red:
        new_arr[0].append(item)
    elif colour == orange:
        new_arr[1].append(item)
    elif colour == yellow:
        new_arr[2].append(item)
    elif colour == green:
        new_arr[3].append(item)
    elif colour == dark_green:
        new_arr[4].append(item)
    elif colour == grey:
        new_arr[5].append(item)

ordered_pollen_data = []

for item in new_arr:
    for index in item:
        ordered_pollen_data.append(index.createHTML(index.colour()))


html_start = """
<html>
  <link
    rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&icon_names=psychiatry"
  />
  <body>
    <div class="background">
      <div class="container">
        <div style="display: flex; flex-direction: column; gap: 10px">
          <h1>Pollen Report</h1>
          <p>Today's forcast for Iden Green</p>
        </div>

        <ul>
"""

html_end = """
        </ul>
      </div>
    </div>
  </body>
  <style>
    * {
      margin: 0;
      padding: 0;
      font-family: Arial, Helvetica, sans-serif;
    }
    .background {
      display: flex;
      height: auto;
      width: auto;
      flex-direction: column;
      align-items: center;
      background-color: lightgray;
    }
    .container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      width: auto;
      height: auto;
      gap: 25px;
      padding: 40px;
      margin: 40px;
      background-color: white;
      box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 24px;
      border-radius: 12px;
    }
    li {
      list-style: none;
      padding-bottom: 20px;
      border: solid 1px darkgray;
      border-radius: 8px;
      margin-bottom: 20px;
      padding: 20px;
    }
    .element {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 10px;
    }

    @media screen and (max-width: 600px) {
      .container {
        margin: 10px;
        padding: 20px;
      }
    }
  </style>
</html>
"""

def populate_html(array, start, end):
    li_elements = ''
    for item in array:
        li_elements += item

    return start + li_elements + end

html = populate_html(ordered_pollen_data, html_start, html_end)


def sendEmail(html, reciever):
        """
        Method to send an email to the client

        Args:
            message (string): The message body of the email
        """

        # Email Configuration
        EMAIL_SENDER = os.getenv('EMAIL_SENDER')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        
        try:
            msg = MIMEMultipart()
            msg['From'] = "Pollen Report" 
            msg['To'] = reciever
            msg['Subject'] = "Today's pollen report for Iden Green"

            # Attach message body
            msg.attach(MIMEText(html, 'html'))

            # Connect to the SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, reciever, msg.as_string())
        
                print(f"Email sent successfully to {reciever}")
        except Exception as e:
            print(f"Error: {e}")


#sendEmail(html, "cheryl.bassett@vmi.tv")
sendEmail(html, "jb@vmi.tv")