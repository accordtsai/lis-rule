#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys

# Variables local to module
__na_ul = 145
__na_ll = 135
__unit = "mmol/l"
__event_dict = {}
__alias = {"Na": "Na", "Sodium": "Na", "NA": "Na"}

def analyze(file_name, lis_struct, time, args):
    """
    Analyzes LIS results, looking for events related to sodium,
    and puts events into a dict {file_name -> {event_time -> (event_str)}}.

    :param file_name: (str) name of current JSON file being read
    :param lis_struct: (dict) dict containing item and value pairs
    :param time: (str) time when results were obtained (as contained in JSON file)
    :param args: (dict) switches provided to lisanalyze.py via argparse

    :returns: False
    """

    #global __alias

    # Use "Na" as the standard name
    for k in lis_struct[time].keys():
        if k in __alias.keys():
            lis_struct[time].update({__alias[k]: lis_struct[time][k]})

    # Basic checks and value-setting
    if "Na" in lis_struct[time].keys():
        if args.warn and lis_struct[time]["Na"]["unit"] != __unit:
            print("WARNING: unit mismatch in entry for {}".format(time), file=sys.stderr)
        na_val = float(lis_struct[time]["Na"]["lab_value"])
    else:
        return None

    # Unit conversion; currently disabled
    #if args.convert:
    #    lis_struct[time]["Na"]["unit"] = lis_struct[time]["Na"]["unit"].lower().replace("eq", "mol")
    #    import pint
    #    ureg = pint.UnitRegistry()
    #    factor = (ureg.parse_expression(lis_struct[time]["Na"]["unit"])).to(__unit).magnitude
    #    na_val *= factor

    # Correction for glucose (Lange Pocket Guide to Diagnostic Tests, 6e, p.260)
    #import lisanalyze_glucose
    #glucose_passthrough = lisanalyze_glucose.passthrough(file_name, lis_struct, time, args)
    #if glucose_passthrough:
    #    glucose, value = glucose_passthrough
    #    if glucose > 110:
    #        na_val += (glucose - 110) * 1.6 / 100

    # Out-of-normal-range warning (currently disabled); provided values take precedence
    #if "ref_high" in lis_struct[time]["Na"].keys():
    #    if na_val > lis_struct[time]["Na"]["ref_high"]:
    #        event_time = time
    #        if file_name not in __event_dict.keys():
    #            __event_dict[file_name] = {}
    #        if event_time not in __event_dict[file_name].keys():
    #            __event_dict[file_name][event_time] = []
    #        event_str = "Hypernatremia (current value {}; reference value {})".format(na_val, lis_struct[time]["Na"]["ref_high"])
    #        __event_dict[file_name][event_time].append(event_str)
    #else:
    #    if args.warn:
    #        print("WARNING: higher reference value not provided; falling back to built-in value", file=sys.stderr)
    #    if na_val > __na_ul:
    #        event_time = time
    #        if file_name not in __event_dict.keys():
    #            __event_dict[file_name] = {}
    #        if event_time not in __event_dict[file_name].keys():
    #            __event_dict[file_name][event_time] = []
    #        event_str = "Hypernatremia (current value {}; reference value {})".format(na_val, __na_ul)
    #        __event_dict[file_name][event_time].append(event_str)
    #if "ref_low" in lis_struct[time]["Na"].keys():
    #    if na_val < lis_struct[time]["Na"]["ref_low"]:
    #        event_time = time
    #        if file_name not in __event_dict.keys():
    #            __event_dict[file_name] = {}
    #        if event_time not in __event_dict[file_name].keys():
    #            __event_dict[file_name][event_time] = []
    #        event_str = "Hyponatremia (current value {}; reference value {})".format(na_val, lis_struct[time]["Na"]["ref_low"])
    #        __event_dict[file_name][event_time].append(event_str)
    #else:
    #    if args.warn:
    #        print("WARNING: lower reference value not provided; falling back to built-in value", file=sys.stderr)
    #    if na_val < __na_ul:
    #        event_time = time
    #        if file_name not in __event_dict.keys():
    #            __event_dict[file_name] = {}
    #        if event_time not in __event_dict[file_name].keys():
    #            __event_dict[file_name][event_time] = []
    #        event_str = "Hyponatremia (current value {}; reference value {})".format(na_val, __na_ll)
    #        __event_dict[file_name][event_time].append(event_str)

    # Panic if Na > 155 mmol/l or Na < 125 mmol (Lange Pocket Guide to Diagnostic Tests, 6e, p.260)
    if na_val > 155:
        event_time = time
        if file_name not in __event_dict.keys():
            __event_dict[file_name] = {}
        if event_time not in __event_dict[file_name].keys():
            __event_dict[file_name][event_time] = []
        event_str = "Severe hypernatremia ({} ({}))".format(na_val, lis_struct[time]["Na"]["unit"])
        __event_dict[file_name][event_time].append(event_str)
    if na_val < 125:
        event_time = time
        if file_name not in __event_dict.keys():
            __event_dict[file_name] = {}
        if event_time not in __event_dict[file_name].keys():
            __event_dict[file_name][event_time] = []
        event_str = "Severe hyponatremia ({} ({}))".format(na_val, lis_struct[time]["Na"]["unit"])
        __event_dict[file_name][event_time].append(event_str)
    return False

def get_results():
    """
    Returns dict of sodium-related tests.
    Parameters: none
    Return value: dict {file_name -> {event_time -> (event_str)}}
    """
    return __event_dict

def passthrough(file_name, lis_struct, time, args):
    """
    Passes tuple of (value, unit) of sodium at indicated time, in a standardized form.

    :param file_name: (str) name of current JSON file being read
    :param lis_struct: (dict) dict containing item and value pairs
    :param time: (str) time when results were obtained (as contained in JSON file)
    :param args: (dict) switches provided to lisanalyze.py via argparse

    :returns: tuple (value, unit)
    """
    # Basic checks and value-setting
    if "Na" in lis_struct[time].keys():
        if args.warn and lis_struct[time]["Na"]["unit"] != __unit:
            print("WARNING: unit mismatch in entry for {}".format(time), file=sys.stderr)
        na_val = float(lis_struct[time]["Na"]["lab_value"])
    else:
        return None
    # Unit conversion
    if args.convert:
        import pint
        ureg = pint.UnitRegistry()
        factor = (ureg.parse_expression(lis_struct[time]["Na"]["unit"])).to(__unit).magnitude
        na_val *= factor
    return na_val, __unit
