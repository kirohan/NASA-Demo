"""
NASA MODIS Processing Pipeline
Supports decadal timeseries extraction from Terra/Aqua MODIS:
- MOD11A2: Land Surface Temperature & Emissivity 8-Day L3 Global 1km
- MOD13Q1: Vegetation Indices 16-Day L3 Global 250m
"""
import numpy as np

def decode_modis_lst(raw_digital_number):
    """MOD11A2 scale factor 0.02. Converts to Kelvin then Celsius."""
    if raw_digital_number == 0:
        return None
    kelvin = raw_digital_number * 0.02
    return round(kelvin - 273.15, 2)

def decode_modis_ndvi(raw_digital_number):
    """MOD13Q1 scale factor 0.0001. Valid range -2000 to 10000."""
    if raw_digital_number < -2000 or raw_digital_number > 10000:
        return None
    return round(raw_digital_number * 0.0001, 4)

def check_modis_qa_flags(qa_byte):
    """
    Evaluates MOD11A2 Quality Assurance (QA) bitmask:
    Bits 0-1: Mandatory QA flags:
      00: LST produced, good quality
      01: LST produced, check other QA
      10: LST not produced due to cloud effects
      11: LST not produced primarily due to other reasons
    """
    qa_int = int(qa_byte)
    mandatory_qa = qa_int & 0b11
    if mandatory_qa == 0b00:
        return "High Quality (Cloud-Free)"
    elif mandatory_qa == 0b01:
        return "Acceptable Quality (Check Flags)"
    else:
        return "Obscured / Cloud Contaminated"
