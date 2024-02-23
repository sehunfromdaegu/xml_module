'''
    Below is the module used for SNUBH feature extraction in Feburary 2022.
    - original code: share/inf/workspace_philip/generators/210307_xml_extraction_and_arrange.py
'''

import numpy as np
import base64
import xml.etree.ElementTree as et

xml_ns = {'snu':'http://www3.medical.philips.com'}

# For .XML files

def hospital_from_xml(xml_root):
    return 'SNUB'

def age_from_xml(xml_root):
    data = ''  # str
    try:
        data = xml_root.find('snu:patient/snu:generalpatientdata/snu:age/snu:years',xml_ns).text
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data

def gender_from_xml(xml_root):
    data = ''  # str
    try:
        data = xml_root.find('snu:patient/snu:generalpatientdata/snu:sex',xml_ns).text
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data

def measurements_from_xml(xml_root):
    data = []  # a list of str
    try:
        interpretation = xml_root.find('snu:interpretations/snu:interpretation', xml_ns)
        
        measurements = interpretation.findall('snu:interpretationmeasurements', xml_ns)
        if len(measurements) == 0:  # globalmeasurements
            measurements = interpretation.find('snu:globalmeasurements', xml_ns)
            data = [
                measurements.find('snu:heartrate', xml_ns).text,
                measurements.find('snu:print', xml_ns).text,
                measurements.find('snu:qrsdur', xml_ns).text,
                measurements.find('snu:qtint', xml_ns).text,
                measurements.find('snu:qtcb', xml_ns).text,
                measurements.find('snu:pfrontaxis', xml_ns).text,
                measurements.find('snu:qrsfrontaxis', xml_ns).text,
                measurements.find('snu:tfrontaxis', xml_ns).text
            ]           
        else:  # interpretationmeasurements
            measurements = measurements[0]
            data = [
                measurements.find('snu:heartrate', xml_ns).text,
                measurements.find('snu:meanprint', xml_ns).text,
                measurements.find('snu:meanqrsdur', xml_ns).text,
                measurements.find('snu:meanqtint', xml_ns).text,
                measurements.find('snu:meanqtc', xml_ns).text,
                measurements.find('snu:pfrontaxis', xml_ns).text,
                measurements.find('snu:qrsfrontaxis', xml_ns).text,
                measurements.find('snu:tfrontaxis', xml_ns).text
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
        statements = xml_root.findall('snu:interpretations/snu:interpretation/snu:statement', xml_ns)
        data = [
            statement.find('snu:leftstatement', xml_ns).text + ' ' + statement.find('snu:rightstatement', xml_ns).text
            for statement in statements
        ] + [xml_root.find('snu:interpretations/snu:interpretation/snu:severity', xml_ns).text]  # n*(lhs + rhs) + severity(e.g. - ABNORMAL ECG -)
        
        if len(data) > 9:  # CAT
            raise ValueError('descriptions length check')
        else:
            data += ['*'] * (9-len(data))
            
    except:
        raise Exception('XML::NOATTRIB')  # CAT
    return data



def get_xml_feature_from_binary(binary):
    root = et.fromstring(binary)
    output = measurements_from_xml(root)
    return output


def measurements_from_xml_muse(xml_root):
    try:
        data_record = xml_root.find('DATA_RECORD')
        waveform_raws = data_record.findall('waveform_raw')
        assert len(waveform_raws) == 1

        data = [
            data_record.find('ventricular_rate').text,
            data_record.find('pr_interval').text,
            data_record.find('qrs_duration').text,
            data_record.find('qt_interval').text,
            data_record.find('qt_corrected').text,
            data_record.find('p_axis').text,
            data_record.find('r_axis').text,
            data_record.find('t_axis').text
        ]

    except:
        raise Exception('XML::NOATTRIB')

    # Replace invalid values
    for idx in range(len(data)):
        elt = data[idx]
        try:
            data[idx] = str(int(elt))
        except:
            data[idx] = '*'

    return data


def get_xml_feature_from_binary_muse(binary):
    root = et.fromstring(binary)
    output = measurements_from_xml_muse(root)
    return output
