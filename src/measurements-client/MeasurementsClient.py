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

#Get variables for StoreScp from config.json.
target = config['Target']
no_of_probes = config['NoOfProbes']
from_country = config['From']
measure = config['Measure']

logging.basicConfig(filename='sintra.csv', level=logging.INFO, format='%(message)s')


ripe = subprocess.run("ripe-atlas measure {0} --target {1} --probes {2} --from-country {3}".format(measure, target, no_of_probes, from_country), capture_output=True, shell=True, encoding="utf8")

output_str = ripe.stdout

logging.info(output_str)