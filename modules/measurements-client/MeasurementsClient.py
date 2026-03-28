import logging
import os
import time
import subprocess
import json
import sys
import schedule
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'event-manager')))
from EventManager import EventManager

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

latency_file = 'output/latency.json'
progress_file = 'output/progress.json'
awanta_measurements = 'output/awanta_measurements'
iteration = 0

if not os.path.exists('output'):
    os.makedirs('output')

# Output in a preferred format.
if TRIMMED_LOGS:
    logging.basicConfig(filename='output/awanta.out', level=logging.INFO, format='%(message)s')
else:
	logging.basicConfig(filename='output/awanta.out', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# A dictionary of dictionaries, to store the output of measurements: [country:[src: rtt]]
whole_dict = dict()
completed_countries = list()            


# All measured endpoints are saved between iterations as JSON files.
try:
    with open(latency_file, 'r') as f:
        whole_dict = json.load(f)
        INIT_EXECUTION = False
except (FileNotFoundError, json.JSONDecodeError):
    logging.info("No existing JSON file. Initialized with empty value for the latency values")

try:
    with open(progress_file, 'r') as f:
        completed_countries = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    logging.info("No existing JSON file. Initialized with empty value for completed countries")

event_manager = EventManager()

def measure_latency():
    global whole_dict
    global EXTRACTION_RUNNING
    global INIT_EXECUTION
    global iteration
    current_measurement_file = awanta_measurements + str(iteration)

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
                # Using --renderer json for precise data extraction and jitter calculation
                ripe = subprocess.run("ripe-atlas measure {0} --target {1} --probes {2} --from-country {3} --packets {4} --size {5} --renderer json".format(measure, target, no_of_probes, country, packets, size), capture_output=True, shell=True, encoding="utf8")
                
                try:
                    results = json.loads(ripe.stdout)
                    for res in results:
                        probe_id = str(res.get('prb_id'))
                        rtts = [r.get('rtt') for r in res.get('result', []) if r.get('rtt') is not None]
                        
                        avg_rtt = 0.0
                        jitter = 0.0
                        if rtts:
                            avg_rtt = sum(rtts) / len(rtts)
                            # Jitter as Standard Deviation
                            variance = sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)
                            jitter = variance ** 0.5
                        
                        # Traceroute for hop count analysis
                        hop_count = 0
                        try:
                            tr_ripe = subprocess.run("ripe-atlas measure traceroute --target {0} --probes {1} --from-country {2} --renderer json".format(target, 1, country), capture_output=True, shell=True, encoding="utf8")
                            tr_results = json.loads(tr_ripe.stdout)
                            if tr_results and isinstance(tr_results, list):
                                # The number of elements in the 'result' array represents the hops
                                hop_count = len(tr_results[0].get('result', []))
                        except Exception as tr_e:
                            logging.error(f"Error performing traceroute for probe {probe_id} in {country}: {tr_e}")

                        each_dict[probe_id] = {"rtt": avg_rtt, "jitter": jitter, "hop_count": hop_count}
                except Exception as e:
                    logging.error(f"Error parsing RIPE Atlas output for {country}: {e}")
                
                whole_dict[country] = each_dict
                completed_countries.append(country)
                # Publish event via Event Manager for real-time propagation
                event_manager.publish_measurement({"country": country, "data": each_dict})
            
            # Write in a human readable file after all countries have been processed.
            with open(current_measurement_file, 'w') as f:
                json.dump(whole_dict, f)
            
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


# Write the JSON file periodically to track the progress and persist it to the filesystem
def update_json():
    global whole_dict
    global completed_countries
    with open(latency_file, 'w') as f:
        json.dump(whole_dict, f)
    with open(progress_file, 'w') as f:
        json.dump(completed_countries, f)
    logging.info('Progress is recorded to the JSON file')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
# The thread scheduling
schedule.every(1).minutes.do(run_threaded, measure_latency)
schedule.every(2).minutes.do(run_threaded, update_json)

# Keep running in a loop.
while True:
    schedule.run_pending()
    time.sleep(1)