import re
import pandas as pd
from os import listdir
from datetime import date, datetime
import csv
import os

path = "./data"

header = ["ParticipantName", "Gender", "Email", "DOB", "Age", "Address", "Phone Number", "ParentName", "Parent's Email", "Phone Number_P1", "ParentName_2", "Phone Number_P2", "Emergency Name 1", "Phone Number_Em1",
          "Emergency Name 2", "Phone Number_Em2", "Minor/Adult", "Media",  "type", "file_name", "EnvelopeId"]

allergy_header = ["Allegry Type_other", "Allegry Food", "Allegry Signs_hm", "Allegry Signs_where", "Allegry Animal",
                  "Allegry Treatment", "Allegry Treatment_2", "Allegry Insect"]


def open_file(df):
    """
    get data from the files

    :param df: panda data frame
    :return:
    """
    data_json = {}
    data = dict.fromkeys(header, False)
    data_json.update({"EnvelopeId": df['EnvelopeId'][1]})
    for i in range(len(df['Field'])):
        for field in data.keys():

            # input from the signer
            field_val = df['Value'][i]

            # form field
            field_name = df['Field'][i]

            # fix fields that have different values
            if field_name == "Emr_Name" or field_name == "Emer_Name_1":
                field_name = "Emergency Name 1"
            if field_name == "Emr_Name_2" or field_name == "Emer_Name_2":
                field_name = "Emergency Name 2"
            if field_name == "Participant Name" or field_name == "Volunteer Name":
                field_name = "ParticipantName"

            if not data[field] and (field_name == field):
                data[field] = True
                # add data from the field
                data_json.update({field_name: field_val})

                # check minor to separate adult and minor
                if field == "DOB":
                    dob = str(field_val)
                    if calculate_age(dob) > 17:
                        data_json.update({"Minor/Adult": "Adult"})
                    else:
                        data_json.update({"Minor/Adult": "Minor"})
                break

    return data_json


def get_allergy_info(df):
    """
    get allergy info using the allergy header

    :param df:
    :return:
    """
    data_json = {}
    # turn not visited fields to false
    allergy_data = dict.fromkeys(allergy_header, False)

    for i in range(len(df['Field'])):
        for field in allergy_data.keys():
            field_val = df['Value'][i]
            field_name = df['Field'][i]
            if not allergy_data[field] and (field_name == field):
                # turn collected fields to true
                allergy_data[field] = True
                data_json.update({field_name: field_val})
                break
    return data_json


def calculate_age(birthDate):
    """
    calculate age from the birth date

    :param birthDate:
    :return:
    """
    birth = datetime.strptime(birthDate, "%m/%d/%Y").date()
    today = date.today()
    try:
        birthday = birth.replace(year=today.year)

    # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError:
        birthday = birth.replace(year=today.year,
                                 month=birth.month + 1, day=1)

    if birthday > today:
        return today.year - birth.year - 1
    else:
        return today.year - birth.year


def get_age(df):
    """
    mark minor and adult
    :param df:
    :return:
    """
    for i in range(len(df['Field'])):
        if "DOB" in df['Field'][i]:
            if calculate_age(df['Value'][i]) > 17:
                return "Adult"
            else:
                return "Minor"

'''
def cleanUpFolder():
    """
    delete all existing files in the volunteers & participants folders

    :return:
    """
    global path
    t = ["participants/Minor", "participants/Adult", "/volunteers/Minor", "volunteers/Adult"]

    for folder in t:

        #print("folder is: ", folder)
        #print("path is: ", path)
        for file in listdir(f'{path}/{folder}'):
            #print(os.path.abspath(f'{path}/{folder}/{file}'), " is removed")
            os.remove(os.path.abspath(f'{path}/{folder}/{file}'))


def organize():
    """
    move download files to folders and rename file with Envelope id

    :return:
    """
    print('organize')
    global path
    #cleanUpFolder()
    for file in listdir(path):
        if file.endswith(".csv"):
            df = pd.read_csv(f"./data/{file}", usecols=['EnvelopeId', 'Field', 'Value']).fillna("")
            source = path + '/' + file
            print(source)

            # add envelope id to the file name
            file_name = re.sub(r'[0-9]+', '', file.replace("(", "").replace(")", "")).replace(".csv",
                                                                                              f"_{df['EnvelopeId'][1]}.csv")

            # move files to folders
            try:
                if "participant-registration" in file:
                    print(f"destination -> {path}/participants/{get_age(df)}/{file_name}")
                    os.rename(source, f"{path}/participants/{get_age(df)}/{file_name}")
                elif "internal-policies" in file:
                    print(f"destination -> {path}/volunteers/{get_age(df)}/{file_name}")
                    os.rename(source, f"{path}/volunteers/{get_age(df)}/{file_name}")

            except FileExistsError as e:
                print(f"deleting {source}")
                os.remove(source)
'''

if __name__ == '__main__':
    print("Running ...")
    #organize()
    info_minor = []
    info = []

    '''
    t = ["participants/Minor", "participants/Adult", "/volunteers/Minor", "volunteers/Adult"]

    for folder in t:
    '''
    for file in listdir(f'{path}/'):
        if file.endswith(".csv"):
            file_data = {}
            df = pd.read_csv(f"{path}/{file}", usecols=['EnvelopeId', 'Field', 'Value']).fillna("")
            file_data = open_file(df)
            file_data["file_name"] = f"{path}/{file}"

            if "participant-registration" in file:
                file_data["type"] = "participant"
                file_data.update(get_allergy_info(df))

            elif "internal-policies" in file:
                file_data["type"] = "volunteers"

            info.append(file_data)

    # allergy info to the file
    [header.append(i) for i in allergy_header]
    with open('all_data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(info)

    print("DONE!")