import logging
import os
import time
import subprocess
import json
import sys
import schedule
import threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'event_manager')))
from EventManager import EventManager

data_lock = threading.Lock()


with open('config.json', 'r') as f:
    config = json.load(f)


target = config['Target']
no_of_probes = config['NoOfProbes']
from_countries = config['From']
measure = config['Measure']
packets = config['Packets']
me = config['Me']
size = config['Size']


EXTRACTION_RUNNING = False
TRIMMED_LOGS = False
INIT_EXECUTION = True

latency_file = 'output/latency.json'
progress_file = 'output/progress.json'
awanta_measurements = 'output/awanta_measurements'
iteration = 0

if not os.path.exists('output'):
    os.makedirs('output')


if TRIMMED_LOGS:
    logging.basicConfig(filename='output/awanta.out', level=logging.INFO, format='%(message)s')
else:
	logging.basicConfig(filename='output/awanta.out', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


whole_dict = dict()
completed_countries = list()            



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


def measure_country(country):
    """
    Run a ping measurement (for RTT/jitter) and a traceroute measurement
    (for hop count) against `target`, from probes in the given country.
    Returns a dict of {probe_id: {"rtt": ..., "jitter": ..., "hop_count": ...}}.
    """
    logging.info('Measuring for country: ' + country)
    each_dict = dict()
    
    cmd = [
        "ripe-atlas", "measure", str(measure),
        "--target", str(target),
        "--probes", str(no_of_probes),
        "--from-country", str(country),
        "--packets", str(packets),
        "--size", str(size),
        "--renderer", "json"
    ]
    try:
        ripe = subprocess.run(cmd, capture_output=True, shell=False, encoding="utf8")
        results = json.loads(ripe.stdout)
        for res in results:
            probe_id = str(res.get('prb_id'))
            rtts = [r.get('rtt') for r in res.get('result', []) if r.get('rtt') is not None]

            avg_rtt = 0.0
            jitter = 0.0
            if rtts:
                avg_rtt = sum(rtts) / len(rtts)
                
                variance = sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)
                jitter = variance ** 0.5

            
            hop_count = 0
            try:
                tr_cmd = [
                    "ripe-atlas", "measure", "traceroute",
                    "--target", str(target),
                    "--probes", str(probe_id),
                    "--renderer", "json"
                ]
                tr_ripe = subprocess.run(tr_cmd, capture_output=True, shell=False, encoding="utf8")
                tr_results = json.loads(tr_ripe.stdout)
                if tr_results and isinstance(tr_results, list):
                    
                    hop_count = len(tr_results[0].get('result', []))
            except Exception as tr_e:
                logging.error(f"Error performing traceroute for probe {probe_id} in {country}: {tr_e}")

            each_dict[probe_id] = {"rtt": avg_rtt, "jitter": jitter, "hop_count": hop_count}
    except Exception as e:
        logging.error(f"Error parsing RIPE Atlas output for {country}: {e}")

    return each_dict


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
            
            for country in from_countries:
                each_dict = measure_country(country)

                with data_lock:
                    whole_dict[country] = each_dict
                    completed_countries.append(country)
                
                event_manager.publish_measurement({"country": country, "data": each_dict})

            
            with open(current_measurement_file, 'w') as f:
                json.dump(whole_dict, f)

            INIT_EXECUTION = False

        else:
            
            for country in list(completed_countries):
                each_dict = measure_country(country)

                with data_lock:
                    whole_dict[country] = each_dict
                
                event_manager.publish_measurement({"country": country, "data": each_dict})

            
            with open(current_measurement_file, 'w') as f:
                json.dump(whole_dict, f)

        iteration += 1
        
        logging.info('Total run time: %s %s', (time.time() - t_start)/60, ' minutes!')
        with data_lock:
            EXTRACTION_RUNNING = False

        
        logging.info(whole_dict)



def update_json():
    global whole_dict
    global completed_countries
    with data_lock:
        with open(latency_file, 'w') as f:
            json.dump(whole_dict, f)
        with open(progress_file, 'w') as f:
            json.dump(completed_countries, f)
    logging.info('Progress is recorded to the JSON file')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    
    schedule.every(1).minutes.do(run_threaded, measure_latency)
    schedule.every(2).minutes.do(run_threaded, update_json)

    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()