
'''
    Below is the module used for SNUBH feature extraction in Feburary 2022.
    - original code: share/inf/workspace_philip/generators/210307_xml_extraction_and_arrange.py
    
    Modification to deal with error has been made in Feburary 2024 by Sehun. Marked by # CORRECTION
'''

import numpy as np
import base64
import xml.etree.ElementTree as et

xml_ns = {'hy':'http://www3.medical.philips.com'}

# For .XML files

def hospital_from_xml(xml_root):
    return 'HY'

def age_from_xml(xml_root):
    data = ''  # str
    try:
        data = xml_root.find('hy:patient/hy:generalpatientdata/hy:age/hy:years',xml_ns).text
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data

def gender_from_xml(xml_root):
    data = ''  # str
    try:
        data = xml_root.find('hy:patient/hy:generalpatientdata/hy:sex',xml_ns).text
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data

def measurements_from_xml(xml_root):
    data = []  # a list of str
    try:
        interpretation = xml_root.find('hy:interpretations/hy:interpretation', xml_ns)
        
        measurements = interpretation.findall('hy:interpretationmeasurements', xml_ns)
        if len(measurements) == 0:  # globalmeasurements
            measurements = interpretation.find('hy:globalmeasurements', xml_ns)
            data = [
                measurements.find('hy:heartrate', xml_ns).text,
                measurements.find('hy:print', xml_ns).text,
                measurements.find('hy:qrsdur', xml_ns).text,
                measurements.find('hy:qtint', xml_ns).text,
                measurements.find('hy:qtcb', xml_ns).text,
                measurements.find('hy:pfrontaxis', xml_ns).text,
                measurements.find('hy:qrsfrontaxis', xml_ns).text,
                measurements.find('hy:tfrontaxis', xml_ns).text
            ]           
        else:  # interpretationmeasurements
            measurements = measurements[0]
            data = [
                measurements.find('hy:heartrate', xml_ns).text,
                measurements.find('hy:meanprint', xml_ns).text,
                measurements.find('hy:meanqrsdur', xml_ns).text,
                measurements.find('hy:meanqtint', xml_ns).text,
                measurements.find('hy:meanqtc', xml_ns).text,
                measurements.find('hy:pfrontaxis', xml_ns).text,
                measurements.find('hy:qrsfrontaxis', xml_ns).text,
                measurements.find('hy:tfrontaxis', xml_ns).text
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
        statements = xml_root.findall('hy:interpretations/hy:interpretation/hy:statement', xml_ns)
        
        # CORRECTION : rightstatement is sometimes missing, so we need to check for its existence.
        for statement in statements:
            # Extract the text from the leftstatement element.
            left_text = statement.find('hy:leftstatement', xml_ns).text
            
            right_element = statement.find('hy:rightstatement', xml_ns)
            right_text = right_element.text if right_element is not None and right_element.text else ''
            
            # Combine the left and right texts, trimming any excess whitespace.
            combined_text = f'{left_text} {right_text}'.strip()
            
            # Add the combined text to the data list.
            data.append(combined_text)

        # combine severity
        data +=[xml_root.find('hy:interpretations/hy:interpretation/hy:severity', xml_ns).text] # n*(lhs + rhs) + severity(e.g. - ABNORMAL ECG -)

        if len(data) > 9:  # CAT
            raise ValueError('descriptions length check')
        else:
            data += ['*'] * (9-len(data))
            
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data

