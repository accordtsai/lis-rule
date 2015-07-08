#!/usr/bin/python3
#-*- coding: utf-8 -*-

import re
import sys
import datetime

# Notes on writing modules:
# 1. Names of variables strictly local to the current module should
# begin with 2 underscores; also, they need to be declared global (since state is maintained)
# 2. __event_dict stores *all* PSA-related events for *all* files. Whether this
# is desirable is up for debate.

# Variables local to module
__psa_current_nadir = float('infinity')
__psa_ul = 400 # 4 ng/ml
__psa_ll = 0
__psa_increases = 0
__psa_last_value = None
__unit = "ng/dl"
__event_dict = {}

def analyze(file_name, lis_struct, time, args):
    """
    Analyzes LIS results, looking for PSA-related events, and puts events
    into a dict {file_name -> {event_time -> (eventstr)}}.

    :param file_name: (str) name of current JSON file being read
    :param lis_struct: (dict) dict containing item and value pairs
    :param time: (str) time when results were obtained (as contained in JSON file)
    :param args: (dict) switches provided to lisanalyze.py via argparse

    :returns:    False
    """

    global __psa_current_nadir
    global __psa_increases
    global __psa_last_value

    # Basic checks
    if "PSA" in lis_struct[time].keys():
        if args.warn and lis_struct[time]["PSA"]["unit"] != __unit:
            print("WARNING: unit mismatch in entry for {}".format(time), file=sys.stderr)
        if re.match("<", lis_struct[time]["PSA"]["lab_value"]):
            __psa_current_nadir = 0
        psa_val = float(lis_struct[time]["PSA"]["lab_value"])
    else:
        return None

    # Unit conversion
    if args.convert:
        import pint
        ureg = pint.UnitRegistry()
        factor = (ureg.parse_expression(lis_struct[time]["PSA"]["unit"])).to(__unit).magnitude
        psa_val *= factor

    if psa_val < __psa_current_nadir:
        __psa_current_nadir = psa_val

    # PSA increase by 2.0 ng/dl (Prostate Cancer Foundation)
    if psa_val - __psa_current_nadir > 2:
        event_name = "PSA biochemical failure (PSA increase by 2.0 ng/dl)"
        event_time = time
        analysis_time = datetime.datetime.now().isoformat()

        eventstr = ""

        if file_name not in __event_dict.keys():
            __event_dict[file_name] = {}
        if event_time not in __event_dict[file_name].keys():
            __event_dict[file_name][event_time] = []

        eventstr = event_name

        if not args.quiet:
            eventstr += "(nadir = {}, value = {} ({}))".format(__psa_current_nadir, psa_val, __unit)

        __event_dict[file_name][event_time].append(eventstr)

    # 3 consecutive increases in PSA (Lange Pocket Guide to Diagnostic Tests, 6e, p.239)
    if __psa_last_value is not None and psa_val > __psa_last_value:
        __psa_increases += 1
    else:
        __psa_increases = 0
    if __psa_increases >= 3:
        event_name = "PSA biochemical failure (3 consecutive increases)"
        event_time = time
        analysis_time = datetime.datetime.now().isoformat()

        eventstr = ""

        if file_name not in __event_dict.keys():
            __event_dict[file_name] = {}
        if event_time not in __event_dict[file_name].keys():
            __event_dict[file_name][event_time] = []

        eventstr = event_name

        if not args.quiet:
            eventstr += "(nadir = {}, value = {} ({}))".format(__psa_current_nadir, psa_val, __unit)

        __event_dict[file_name][event_time].append(eventstr)

    __psa_last_value = psa_val

    return False

def get_results():
    """
    Returns dict of PSA-related tests.
    Parameters: none
    Return value: dict {file_name -> {event_time -> (eventstr)}}
    """
    return __event_dict
