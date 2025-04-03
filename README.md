# Pollen Report

### Background

I suffer from hayfever and sometimes I have no idea if I need to take a tablet or not, so I built this system to automatically check and send me and my mum an email with the pollen forcast for our area.

### How does it work?

This script first makes a call to Google's pollen API and retrieves the data through a workaround to the OAuth 2 token system, by running a system command to the `gcloud` cli and parsing the token to make it usable. The script is then able to parse the JSON and construct an html template in order based on pollen density and email the template to the reciever of choice.

### Features

- Daily pollen updates for a given area
- Dynamic HTML template styling
- Automation via cron

### Get Started

Simply add the bash file to your crontab with the following command.

```
07*** ./path/to/script/automation.sh
```
