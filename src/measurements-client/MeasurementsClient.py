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