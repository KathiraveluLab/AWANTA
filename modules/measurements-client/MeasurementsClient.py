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
from_countries = config['From']
measure = config['Measure']
packets = config['Packets']
me = config['Me']

logging.basicConfig(filename='sintra.csv', level=logging.INFO, format='%(message)s')

whole_dict = dict()



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

logging.info(whole_dict)
