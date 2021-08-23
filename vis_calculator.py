# You can use whatever package(s) you like to handle the timeseries data
import json
import numpy as np
import pandas as pd
import traces
import matplotlib.pyplot as plt
import csv


class VISCalculator:

    def __init__(self, medications_filename, medication_administrations_filename, note_filename, procedures_filename):
        self.medications_filename = medications_filename
        self.medication_administrations_filename = medication_administrations_filename
        self.note_filename = note_filename
        self.procedures_filename = procedures_filename
        self.note_file = None
        with open(self.note_filename) as json_file:
            self.note_file = json.load(json_file)
        with open(self.medications_filename) as json_file1:
            self.medications = json.load(json_file1)
        with open(self.medication_administrations_filename) as json_file2:
            self.medication_administrations = json.load(json_file2)

    def make_procedures_from_log(self):
        # create an empty list to add in the two dictionaries for two instances
        procedures = []
        # Create a reader and iterate through rows to add them into the dictionaries
        with open(self.procedures_filename, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for rows in reader:
                dictionary = {}
                dictionary['identifier'] = rows['case_id']
                dictionary['subject'] = rows['mrn']
                dictionary['performer'] = rows['primary_surgeon']
                dictionary['code'] = rows['primary_procedure_code']
                # Transform into datetime recource in fhir
                dictionary['performedDateTime'] = rows['procedure_date'] + 'T' + rows['procedure_time'] 
                procedures.append(dictionary)          
        return procedures


    def make_procedures_from_note(self):
        
        # create an empty list to add in the two dictionaries for two instances
        procedures2 = []
        dictionary2 = {}
        dictionary3 = {}
        # add in key and values from the parsed note
        key = ['code', 'performedDateTime', 'recorder', 'status']
        procedure_note_1 = ['40701008', self.note_file['coded_entities'][25]['value'], 
                            self.note_file['coded_entities'][3]['value'], 'completed']
        procedure_note_2 = ['112811009', self.note_file['coded_entities'][33]['value'], 
                            self.note_file['coded_entities'][3]['value'], 'completed']
        # loop through to pair the keys and values
        for i in range(len(key)):
            dictionary2[key[i]] = procedure_note_1[i]
            dictionary3[key[i]] = procedure_note_2[i]
        procedures2.append(dictionary2)
        procedures2.append(dictionary3)
        return procedures2


    def make_encounters_from_note(self):
        # create empty libraries
        hospitalization = {}
        cicu = {}
        coded_entities = self.note_file["coded_entities"]
        # use nested for loop to extract useful resources
        for i in range(len(coded_entities)):
            if "coding" in coded_entities[i]:
                for key, value in coded_entities[i]["coding"]["umls"].items():
                    if key == "C0184666":
                        hospitalization["serviceType"] = "Hospitalization"
                        if coded_entities[i].get("value_units") == "date" and "period" in hospitalization:
                            hospitalization["period"]["start"] = coded_entities[i]["value"]
                            continue
                        if coded_entities[i].get("value_units") == "date":
                            period = {}
                            hospitalization["period"] = period
                            hospitalization["period"]["start"] = coded_entities[i]["value"]
                    if key == "C0586003":
                        hospitalization["serviceType"] = "Hospitalization"
                        if coded_entities[i].get("value_units") == "date" and "period" in hospitalization:
                            hospitalization["period"]["end"] = coded_entities[i]["value"]
                            continue
                        if coded_entities[i].get("value_units") == "date":
                            period = {}
                            hospitalization["period"] = period
                            hospitalization["period"]["end"] = coded_entities[i]["value"]
                    if key == "C5240707":
                        cicu["serviceType"] = "CICU"
                        if coded_entities[i].get("value_units") == "date" and "period" in cicu:
                            cicu["period"]["start"] = coded_entities[i]["value"]
                            continue
                        if coded_entities[i].get("value_units") == "date":
                            period = {}
                            cicu["period"] = period
                            cicu["period"]["start"] = coded_entities[i]["value"]
                    if key == "C5240710":
                        cicu["serviceType"] = "CICU"
                        if coded_entities[i].get("value_units") == "date" and "period" in cicu:
                            cicu["period"]["end"] = coded_entities[i]["value"]
                            continue
                        if coded_entities[i].get("value_units") == "date":
                            period = {}
                            cicu["period"] = period
                            cicu["period"]["end"] = coded_entities[i]["value"]
                    if key == "C0086582":
                        if "subject" in hospitalization:
                            hospitalization["subject"]["gender"] = "male"
                        else:
                            subject = {}
                            subject["gender"] = "male"
                            hospitalization["subject"] = subject
                        
                        if "subject" in cicu:
                            cicu["subject"]["gender"] = "male"
                        else:
                            subject = {}
                            subject["gender"] = "male"
                            cicu["subject"] = subject
                    if key == "C0086287":
                        if "subject" in hospitalization:
                            hospitalization["subject"]["gender"] = "female"
                        else:
                            subject = {}
                            subject["gender"] = "female"
                            hospitalization["subject"] = subject
                        
                        if "subject" in cicu:
                            cicu["subject"]["gender"] = "female"
                        else:
                            subject = {}
                            subject["gender"] = "female"
                            cicu["subject"] = subject
                    if key == "C0803906" and i < len(coded_entities)-1:
                        if "subject" in hospitalization:
                            hospitalization["subject"]["birthDate"] = coded_entities[i+1]["value"]
                        else:
                            subject = {}
                            subject["birthDate"] = coded_entities[i+1]["value"]
                            hospitalization["subject"] = subject
                        
                        if "subject" in cicu:
                            cicu["subject"]["birthDate"] = coded_entities[i+1]["value"]
                        else:
                            subject = {}
                            subject["birthDate"] = coded_entities[i+1]["value"]
                            cicu["subject"] = subject
        return {"Hospitalization":hospitalization, "CICU":cicu}

    def make_fhir_resources(self):
        # create an empty dictionary and add encounter and procedure as keys
        # add in paired values
        resources = {}
        resources["Encounter"] = self.make_encounters_from_note()
        resources["Procedure"] = self.make_procedures_from_log() + self.make_procedures_from_note()
        return resources

    def calculate_vis_score(self, medications_names_and_quantities):
        # use a for loop to calculate the vis scores
        score = 0
        for item in medications_names_and_quantities:
            name = item[0]
            quantity = item[1]
            if name == "Milrinone":
                score += 10 * quantity
            elif name == "Dobutamine":
                score += quantity
            elif name == "Dopamine":
                score += quantity
            elif name == "Vasopressin":
                score += 10000*quantity
            elif name == "Epinephrine":
                score += 100 * quantity
            elif name == "Norepinephrine":
                score += 100 * quantity
        return score

    def calculate_vis_timeseries(self):
        """ Return the VIS timeseries
        """
        # create an empty dictionary to store paired data
        mid_dictionary = {}
        for i in range(0, len(self.medications), 2):
            mid_dictionary[self.medications[i+1].get("id")] = self.medications[i].get("code").get("coding")[0].get("display")
        mid_admins = []
        for admin in self.medication_administrations:
            new_dict = {}
            new_dict["id"] = admin.get("id")
            new_dict["medication"] = admin.get("medicationReference").get("reference")
            new_dict["rate"] = admin.get("rateQuantity").get("value")
            new_dict["start"] = admin.get("effectivePeriod").get("start")
            new_dict["end"] = admin.get("effectivePeriod").get("end")
            mid_admins.append(new_dict)
        mid_admins = sorted(mid_admins, key=lambda k: k['start']) 
        print(mid_admins)
        # create a new dictionary where keys correspond to dates and the values correspond to vis scores
        vis_by_time = {}
        for i in range(len(mid_admins)):
            vis_score = self.calculate_vis_score([[mid_dictionary.get(mid_admins[i].get("medication")), mid_admins[i].get("rate")]])
            start_vis = vis_score
            end_vis = vis_score
            for key, value in vis_by_time.items():
                if key > mid_admins[i].get("start"):
                    vis_by_time[key] += vis_score
                    start_vis += vis_by_time.get(key)
                if key > mid_admins[i].get("end"):
                    end_vis += vis_by_time.get(key)
                if key ==  mid_admins[i].get("start"): break
            vis_by_time[mid_admins[i].get("start")] = start_vis
            vis_by_time[mid_admins[i].get("end")] = end_vis   
        return pd.DataFrame(vis_by_time.items(), columns=['Timestamp', 'VIS'])
            
    def plot_vis_timeseries(self):
        """ Return filename that you saved the VIS timeseries to (.png)
        """
        # rerun the VIS timeseries code
        mid_dictionary = {}
        for i in range(0, len(self.medications), 2):
            mid_dictionary[self.medications[i+1].get("id")] = self.medications[i].get("code").get("coding")[0].get("display")
        mid_admins = []
        for admin in self.medication_administrations:
            new_dict = {}
            new_dict["id"] = admin.get("id")
            new_dict["medication"] = admin.get("medicationReference").get("reference")
            new_dict["rate"] = admin.get("rateQuantity").get("value")
            new_dict["start"] = admin.get("effectivePeriod").get("start")
            new_dict["end"] = admin.get("effectivePeriod").get("end")
            mid_admins.append(new_dict)
        mid_admins = sorted(mid_admins, key=lambda k: k['start']) 
        print(mid_admins)
        vis_by_time = {}
        for i in range(len(mid_admins)):
            vis_score = self.calculate_vis_score([[mid_dictionary.get(mid_admins[i].get("medication")), mid_admins[i].get("rate")]])
            start_vis = vis_score
            end_vis = vis_score
            for key, value in vis_by_time.items():
                if key > mid_admins[i].get("start"):
                    vis_by_time[key] += vis_score
                    start_vis += vis_by_time.get(key)
                if key > mid_admins[i].get("end"):
                    end_vis += vis_by_time.get(key)
                if key ==  mid_admins[i].get("start"): break
            vis_by_time[mid_admins[i].get("start")] = start_vis
            vis_by_time[mid_admins[i].get("end")] = end_vis   
        df = pd.DataFrame(vis_by_time.items(), columns=['Timestamp', 'VIS'])
        # plot vis vs timestamp using the dataframe and save as png
        df.plot(x = 'Timestamp', y = 'VIS')
        plt.savefig("test_05/results/VIS_timeseries.png")
        return "test_05/results/VIS_timeseries.png"

    def get_max_vis_score_info(self):
        """ Return dictionary with required info about the max VIS score
        """
        # Sorry for not finishing goal 3 in this project due to limited time! I've tried to put my thoughts on this problem below:
        # 1. The function will take in fhir resource and the key information on medication and time will be extracted to construct a dataframe.
        # 2. We can use timeseries data and perform further identification through filtering out the unwanted entries that are not reported during CICU.
        # 3. Find the max VIS score in first 24h.
        # 4. Check duration of the highest score by text extraction and calculation using time.
        # 5. Perform the classification by seperately do the analysis on first 24 hrs and 24 - 48 hrs, and take the bigger classification  number of the two results.

