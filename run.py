""" Carta Healthcare Data Science test solutions

    Author:  Jingwen Yuan
    Date: 8/19/2021

    Notes: Challenging but fun test!


"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from test_05.vis.vis_calculator import VISCalculator

from carta_interview import Datasets, get_data_file, save_json

MED_FILENAME = get_data_file(Datasets.MEDICATIONS)
MED_ADMIN_FILENAME = get_data_file(Datasets.MEDICATION_ADMINISTRATIONS)
NOTE_FILENAME = get_data_file(Datasets.PARSED_NOTE)
PROCEDURE_FILENAME = get_data_file(Datasets.PROCEDURES)


calculator = VISCalculator(MED_FILENAME, MED_ADMIN_FILENAME, NOTE_FILENAME, PROCEDURE_FILENAME)

fhir_resources = calculator.make_fhir_resources()
vis_timeseries = calculator.calculate_vis_timeseries()
vis_plot_file = calculator.plot_vis_timeseries()
max_vis_score_info = calculator.get_max_vis_score_info()

## Print your result here!
print("All Extracted FHIR Resources")
print(fhir_resources)
save_json(fhir_resources, "test_05/results/fhir_resources.json")
print("\n\n")

print("VIS Score Timeseries")
print(vis_timeseries)
# Assumes the timeseries is a pandas dataframe 
# You can remove and use whatever else you want to save the .csv file
vis_timeseries.to_csv("test_05/results/VIS_timeseries.csv")
print("\n\n")

print("VIS Score Plot saved to")
print(vis_plot_file)
print("\n\n")

print("Max VIS Score Info")
print(max_vis_score_info)
save_json(max_vis_score_info, "results/maximum_VIS_score_info.json")
print("\n\n")
