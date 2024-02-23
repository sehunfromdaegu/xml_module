import numpy as np
import base64
import xml.etree.ElementTree as et
import csv
import datetime
import pickle
import tqdm
# Ref: https://github.com/hewittwill/ECGXMLReader

# ISH xml contains '?' at the beginning of the file which is not a valid xml format.
def parse_corrected_xml(xml_path):
    # Read and correct the XML content
    with open(xml_path, 'r', encoding='Windows-1252') as file:
        content = file.read()

    # Correct the issue if the extra '?' is present at the beginning
    if content.startswith('?<?xml'):
        content = content[1:]
    
    # Parse the corrected XML content
    xml_root = et.fromstring(content)
    return xml_root

def waves_from_xml_file(xml_path):

    # For ISH, use 'parse_corrected_xml' because the xml files contains errors... 
    xml_root = parse_corrected_xml(xml_path)
    # xml_root = et.parse(xml_path).getroot()

    xml_waveform = xml_root.findall('Waveform')[-1]

    freq = float(xml_waveform.find('SampleBase').text)

    waves = dict()
    try:
        lead_nr = xml_waveform.find('NumberofLeads')
        leaddatas = xml_waveform.findall('LeadData')

        if lead_nr is not None:
            if int(lead_nr.text) != len(leaddatas):
                raise ValueError(f"Noted # of leads:{lead_nr.text} != # of recored # of leads:{len(leaddatas)}")
        if len(leaddatas) != 8 and len(leaddatas) != 12:
            raise ValueError(f"There are invalid number of leads:{len(leaddatas)}")

        for xml_leaddata in xml_waveform.findall('LeadData'):
            key, wave = waves_from_lead_data(xml_leaddata, freq)
            waves[key] = wave

        if len(waves) == 8 and not 'III' in waves.keys():
            waves['III'] = np.subtract(waves['II'], waves['I'])
            waves['aVR'] = np.add(waves['I'], waves['II'])*(-0.5)
            waves['aVL'] = np.subtract(waves['I'], waves['III'])*(0.5)
            waves['aVF'] = np.add(waves['II'], waves['III'])*(0.5)

        # Define the standard order of ECG leads
        lead_order = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

        # Ensure all required leads are present in the waves dictionary
        waves = {key: waves[key] for key in lead_order if key in waves}

        # Convert the waves dictionary to a list of arrays in the order defined by lead_order
        waves_list = [waves[key] for key in lead_order if key in waves]

    except Exception as e:
        raise e
    
    # return freq, waves_list
    return waves_list

def waves_from_lead_data(xml_leaddata, freq=500.0):
    
    lead_sample_count_total = int(xml_leaddata.find('LeadSampleCountTotal').text)
    if lead_sample_count_total != 10*freq: # check if signal is of 10 seconds
        raise ValueError(f"Lead signal is not of 10 seconds. Frequency is {int(freq)} while the length of signal is {lead_sample_count_total}.")
    
    lead_ID = xml_leaddata.find('LeadID').text
    lead_amp_unit_per_bit = float(xml_leaddata.find('LeadAmplitudeUnitsPerBit').text)
    if xml_leaddata.find('LeadAmplitudeUnits') is not None:
        lead_amp_unit = xml_leaddata.find('LeadAmplitudeUnits').text
        assert lead_amp_unit == 'MICROVOLTS'
        
    wave = xml_leaddata.findall('WaveFormData')
    
    assert len(wave) == 1
    
    wave = wave[0]
    wave = base64.b64decode(wave.text)    
    wave = np.frombuffer(wave, 'h')
    wave = (lead_amp_unit_per_bit/1000.) * wave  # millivolts
    
    return lead_ID, wave

def measurements_from_xml_file(xml_path):
    
    try:
        xml_root = parse_corrected_xml(xml_path)
        # xml_root = et.parse(xml_path).getroot()
        xml_measurements = xml_root.findall('RestingECGMeasurements')[-1]
    
        measurements = [
            measurement.text if measurement is not None else '*'
            for measurement in [
                xml_measurements.find('VentricularRate'),
                xml_measurements.find('PRInterval'),
                xml_measurements.find('QRSDuration'),
                xml_measurements.find('QTInterval'),
                xml_measurements.find('QTCorrected'),
                xml_measurements.find('PAxis'),
                xml_measurements.find('RAxis'),
                xml_measurements.find('TAxis'),
            ]
        ]
       
    except Exception as e:
        raise e

    return measurements