'''
Treatments
'''
import os
import csv
from flask import current_app

TREATMENT_CSV_FN = 'treatments.csv'

# load the data
treatment_dict = {}

full_fn = os.path.join(
    current_app.instance_path,
    TREATMENT_CSV_FN
)

with open(full_fn) as csvfile:
    reader = csv.reader(csvfile, )