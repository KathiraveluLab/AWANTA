import logging
import os
import signal
import csv
import time
import shutil
import subprocess
import datetime
import json
import sys
import schedule
import pickle
import threading


with open('config.json', 'r') as f:
    config = json.load(f)

#Get the constants for the RIPE Atlas Measurements from config.json.
target = config['Target']
no_of_probes = config['NoOfProbes']
from_countries = config['From']
measure = config['Measure']
packets = config['Packets']
me = config['Me']

TRIMMED_LOGS = false

# Output in a preferred format.
if TRIMMED_LOGS:
    logging.basicConfig(filename='sintra.out', level=logging.INFO, format='%(message)s')
else:
	logging.basicConfig(filename='sintra.out', level=logging.INFO)

# A dictionary of dictionaries, to store the output of measurements: [country:[src: rtt]]
whole_dict = dict()

# Loop through each country in the array of countries.
for country in from_countries:
    each_dict = dict()
    ripe = subprocess.run("ripe-atlas measure {0} --target {1} --probes {2} --from-country {3} --packets {4}".format(measure, target, no_of_probes, country, packets), capture_output=True, shell=True, encoding="utf8")
    output_str = ripe.stdout
    output_line_separated = output_str.split('\n')


    for line in output_line_separated:
	    if len(line) > 1:
	        entries = line.split()
	        each_dict[entries[5]] = entries[9][4:]
    whole_dict[country] = each_dict

# Print the dictionary to a local file.
logging.info(whole_dict)
