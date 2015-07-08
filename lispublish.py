#!/usr/bin/python3
#-*- coding: utf-8 -*-
import argparse
import datetime
import PyRSS2Gen
import json
import io

# Generates RSS2 feeds for results of LIS data interpretation.
# Requires PyRSS2Gen (installation on Windows: pip install PyRSS2Gen).
# Confirmed to work on Mozilla Thunderbird.
# Current issues:
#    - What should the link URL and GUID for each post be?
#    - What attributes of RSS2 should we use?

parser = argparse.ArgumentParser(
        description='RSS2 feed generator for LIS data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-f', '--file', type=str, nargs = '*', default=["data.txt_result.json"], help='set paths of JSON-formatted LIS event files to read')
parser.add_argument('-s', '--suffix', type=str, default=".xml", help='set suffix of output files')
#parser.add_argument('-q', '--quiet', action='store_true', help='suppresses verbose messages')
#parser.add_argument('-w', '--warn', action='store_true', help='enable extra warnings')
parser.add_argument('--version', action='version', version='%(prog)s 0.1 "Auspicious clouds"')
args = parser.parse_args()

for result_file_name in args.file:
    result_file_fo = io.open(result_file_name)
    result_struct = json.load(result_file_fo)

    rss_items = []
    for key in result_struct.keys():
        if key == "file_name":
            continue
        rss_items.append(
            PyRSS2Gen.RSSItem(
                title = result_struct[key]["event_name"],
                link = "http://www.hosp.ncku.edu.tw", # placeholder URL
                description = result_file_name + ": " + result_struct[key]["event_name"] + " detected at " + key + " (analysis performed at " + result_struct[key]["analysis_time"] + ")",
                guid = PyRSS2Gen.Guid(result_struct["file_name"] + "_" + key + "_" + result_struct[key]["event_name"], isPermaLink=False),
                pubDate = datetime.datetime.strptime(key, "%Y-%m-%dT%H:%M") - datetime.timedelta(hours=8) # Assuming UTC+8; PyRSS2Gen requires UTC
            )
        )
         #link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
         #description = "Dalke Scientific today announced PyRSS2Gen-0.0, "
                       #"a library for generating RSS feeds for Python.  ",
         #guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/news/"
                          #"030906-PyRSS2Gen.html"),
         #pubDate = datetime.datetime(2003, 9, 6, 21, 31)

    rss = PyRSS2Gen.RSS2(
        title = "Analysis results for file " + result_struct["file_name"],
        link = "http://www.hosp.ncku.edu.tw", # placeholder URL
        description = "Experimental automated analysis of laboratory "
                      "test results",
        lastBuildDate = datetime.datetime.now(),
        items = rss_items
    )
    rss.write_xml(open(result_file_name + args.suffix, "w"))

#rss = PyRSS2Gen.RSS2(
    #title = "Andrew's PyRSS2Gen feed",
    #link = "http://www.dalkescientific.com/Python/PyRSS2Gen.html",
    #description = "The latest news about PyRSS2Gen, a "
                  #"Python library for generating RSS2 feeds",

    #lastBuildDate = datetime.datetime.now(),

    #items = [
       #PyRSS2Gen.RSSItem(
         #title = "PyRSS2Gen-0.0 released",
         #link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
         #description = "Dalke Scientific today announced PyRSS2Gen-0.0, "
                       #"a library for generating RSS feeds for Python.  ",
         #guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/news/"
                          #"030906-PyRSS2Gen.html"),
         #pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
       #PyRSS2Gen.RSSItem(
         #title = "Thoughts on RSS feeds for bioinformatics",
         #link = "http://www.dalkescientific.com/writings/diary/"
                #"archive/2003/09/06/RSS.html",
         #description = "One of the reasons I wrote PyRSS2Gen was to "
                       #"experiment with RSS for data collection in "
                       #"bioinformatics.  Last year I came across...",
         #guid = PyRSS2Gen.Guid("http://www.dalkescientific.com/writings/"
                               #"diary/archive/2003/09/06/RSS.html"),
         #pubDate = datetime.datetime(2003, 9, 6, 21, 49)),
    #])

#rss.write_xml(open("pyrss2gen.xml", "w"))
