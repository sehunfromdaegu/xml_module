
'''
    Below is the module used for SNUBH feature extraction in Feburary 2022.
    - original code: share/inf/workspace_philip/generators/210307_xml_extraction_and_arrange.py
    
    Modification to deal with error has been made in Feburary 2024 by Sehun. Marked by # CORRECTION

    Modification to new xml type in April 2024 by Sehun
'''

import numpy as np
import base64
import xml.etree.ElementTree as et
import scipy.signal as signal

xml_ns = {'sapphire':'urn:ge:sapphire:sapphire_3'}

def age_from_xml(xml_root):
    data = ''
    try:
        data = xml_root.find('sapphire:demographics/sapphire:patientInfo/sapphire:visit/sapphire:patientData/sapphire:patientAge', xml_ns).get('V')
    except:
        raise Exception('XML::NOATTRIB')  # CAT 
    return data

def gender_from_xml(xml_root):
    try:
        return xml_root.find('sapphire:demographics/sapphire:patientInfo/sapphire:gender', xml_ns).get('V')
    except:
        raise Exception('XML::NOATTRIB')  # CAT 
        return ''

def measurements_from_xml(xml_root):
    data = []  # a list of str
    try:
        measurements = xml_root.find('sapphire:xmlData/sapphire:block/sapphire:params/sapphire:ecg/sapphire:var/sapphire:medianTemplate/sapphire:num/sapphire:global',xml_ns)
        data = [
            measurements.find('sapphire:ventricularRate', xml_ns).get('V'),
            measurements.find('sapphire:PR_Interval', xml_ns).get('V'),
            measurements.find('sapphire:QRS_Duration', xml_ns).get('V'),
            measurements.find('sapphire:QT_Interval', xml_ns).get('V'),
            measurements.find('sapphire:qtcBazettCorrection', xml_ns).get('V'),
            measurements.find('sapphire:P_Axis', xml_ns).get('V'),
            measurements.find('sapphire:R_Axis', xml_ns).get('V'),
            measurements.find('sapphire:T_Axis', xml_ns).get('V')
        ]   
    except:
        raise Exception('XML::NOATTRIB')  # CAT
        
    # Replace invalid values
    for idx in range(len(data)):
        elt = data[idx]
        try:
            data[idx] = str(int(elt))
        except:
            data[idx] = '*'
    return data            

def descriptions_xml(xml_root):
    data = []  # list of strings
    try:
        statements=xml_root.findall('sapphire:interpretation/sapphire:params/sapphire:ecg/sapphire:interp/sapphire:resting/sapphire:obset/sapphire:statement', xml_ns)
        
        # CORRECTION : rightstatement is sometimes missing, so we need to check for its existence.
        for statement in statements:
            text = statement.get('V')
            
            # Add the combined text to the data list.
            data.append(text)
            
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data


def waves_from_xml_file_sapphire(xml_path):
    waves = []
    try:
        xml_root = et.parse(xml_path)  
        
        ecgWaveforms=xml_root.findall('sapphire:xmlData/sapphire:block/sapphire:params/sapphire:ecg/sapphire:wav/sapphire:ecgWaveformMXG/sapphire:ecgWaveform',xml_ns)

        waves = [ecgWaveform.get('V').split() for ecgWaveform in ecgWaveforms]
        leads = [ecgWaveform.get('lead') for ecgWaveform in ecgWaveforms]

        #  Reorder the waves so that they are in the order 'lead_order'
        def reorder_waves(waves, leads):
            lead_order = ['I', 'II', 'III', 'AVR', 'AVL', 'AVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
            # reorder waves
            waves_dict = dict(zip(leads, waves))
            waves = [np.array(waves_dict[lead], dtype='float64') for lead in lead_order]
            return waves

        waves = reorder_waves(waves, leads)
        waves = signal.resample(waves, 5000, axis=1)

        # Append 0 to the end of the waves to make it 5500 samples long
        waves = np.concatenate((waves, np.zeros((waves.shape[0], 500))), axis=1)

    except: 
        raise Exception('XML::NOATTRIB')  # CAT

    return waves