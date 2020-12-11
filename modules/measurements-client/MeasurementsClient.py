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
size = config['Size']

# Global Constants: Configurations and folder locations
EXTRACTION_RUNNING = False
TRIMMED_LOGS = False
INIT_EXECUTION = True

latency_file = 'output/latency.pickle'
progress_file = 'output/progress.pickle'
human_readable_measurements = 'output/sintra_measurements'
iteration = 0

if not os.path.exists('output'):
    os.makedirs('output')

# Output in a preferred format.
if TRIMMED_LOGS:
    logging.basicConfig(filename='output/sintra.out', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
else:
	logging.basicConfig(filename='output/sintra.out', level=logging.INFO)

# A dictionary of dictionaries, to store the output of measurements: [country:[src: rtt]]
whole_dict = dict()
completed_countries = list()            


# All meaured endpoints are saved between iterations as pickle files.
try:
    with open(latency_file, 'rb') as f:
        whole_dict = pickle.load(f)
        INIT_EXECUTION = False
except:
    logging.info("No existing pickle file. Initialized with empty value for the latency values")

try:
    with open(progress_file, 'rb') as f:
        completed_countries = pickle.load(f)
except:
    logging.info("No existing pickle file. Initialized with empty value for completed countries")

def measure_latency():
    global whole_dict
    global EXTRACTION_RUNNING
    global INIT_EXECUTION
    global iteration
    current_measurement_file = human_readable_measurements + str(iteration)

    if EXTRACTION_RUNNING:
        logging.info("Previous measurement still running. Skip this iteration.......................")
    else:
        t_start = time.time()
        EXTRACTION_RUNNING = True
    
        if INIT_EXECUTION:
            # Loop through each country in the array of countries.
            for country in from_countries:
                logging.info('Measuring for country: ' + country)
                each_dict = dict()
                ripe = subprocess.run("ripe-atlas measure {0} --target {1} --probes {2} --from-country {3} --packets {4} --size {5}".format(measure, target, no_of_probes, country, packets, size), capture_output=True, shell=True, encoding="utf8")
                output_str = ripe.stdout
                output_line_separated = output_str.split('\n')

                for line in output_line_separated:
	                if len(line) > 1:
	                    entries = line.split()
	                    each_dict[entries[5]] = entries[10][6:-1]
                
                whole_dict[country] = each_dict
                completed_countries.append(country)
            
                # Write in a human readable file for every country's iteration.
                with open(current_measurement_file, 'w') as f:
                    f.write(json.dumps(whole_dict))
            
            INIT_EXECUTION = False

        else:
            # Update the whole_dict incrementally. But not a complete rerun.
            logging.info("Todo: Subsequent Execution is not implemented yet...")

        iteration += 1
        # Record the total run-time
        logging.info('Total run time: %s %s', (time.time() - t_start)/60, ' minutes!')
        EXTRACTION_RUNNING = False

        # Print the dictionary to a local file.
        logging.info(whole_dict)


# Write the pickle file periodically to track the progress and persist it to the filesystem
def update_pickle():
    global whole_dict
    global completed_countries
    with open(latency_file, 'wb') as f:
        pickle.dump(whole_dict, f)
    with open(progress_file, 'wb') as f:
        pickle.dump(completed_countries, f)    
    logging.info('Progress is recorded to the pickle file')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
# The thread scheduling
schedule.every(1).minutes.do(run_threaded, measure_latency)
schedule.every(2).minutes.do(run_threaded, update_pickle)

# Keep running in a loop.
while True:
    schedule.run_pending()
    time.sleep(1)