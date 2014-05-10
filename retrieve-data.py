#!/usr/bin/env python

from urllib import urlencode
from urllib2 import urlopen
import json
import logging

from windstream.models import *

logger = logging.getLogger('ebwind.retrieve')

def open_url(install_id, start_timestamp):
    url = 'http://ds.windstream-inc.com/WSData/api/performancedata.json'
    params = { 'installid': install_id,
               'timezone': 'utc',
               'start': start_timestamp
    }
    full_url = "{}?{}".format(url, urlencode(params))
    return urlopen(full_url)

def retrieve_data(mill):
    """Retrieve data saved since the most recent retrieval.

    If no data have been retrieved, go back to the earliest-known time at which data were
    gathered and retrieve everything.

    """
    start_timestamp = None
    try:
        latest_sample = TurboMillSample.objects.order_by('-time_stamp')[0]
        logger.debug("Latest sample at %s", latest_sample)
        start_timestamp = latest_sample.time_stamp.strftime("%Y-%m-%d %H:%M:30")
    except TurboMillSample.DoesNotExist:
        logger.debug("No sample for %s", mill)
        # N.B., earliest date (for Matthews Community Center) is 2012-11-29.
        start_timestamp = '2012-11-29 00:00'
    logger.info("Retrieving %s at %s", mill, start_timestamp)

    # The feed prefixes the JSON data with a Unicode Byte Order Mark. This decoding
    # removes the mark.
    raw = open_url(mill.install_id, start_timestamp).read().decode('utf-8-sig')
    data = json.loads(raw)

    num_added = num_duped = 0

    for datum in data:
        try:
            sample = TurboMillSample.objects.get(location=mill, time_stamp=datum['TimeStamp'])
            logger.debug("ALREADY HAVE %s %s", sample.location, sample.time_stamp)
            num_duped += 1
        except TurboMillSample.DoesNotExist:
            logger.debug("ADDING %s %s", mill, datum['TimeStamp'])
            TurboMillSample.objects.create(location=mill,
                                           time_stamp = datum['TimeStamp'],
                                           joules     = datum['Joules'],
                                           watts_avg  = datum['WattsAvg'],
                                           volts_avg  = datum['VoltsAvg'],
                                           volts_peak = datum['VoltsPeak'],
                                           volts_min  = datum['VoltsMin'],
                                           amps_avg   = datum['AmpsAvg'],
                                           amps_peak  = datum['AmpsPeak'],
                                           speed_avg  = datum['SpeedAvg'] or 0,
                                           speed_peak = datum['SpeedPeak'] or 0,
                                           dir_mag    = datum['DirMag'],
                                           dir_ang    = datum['DirAng'],
                                           dir_cos    = datum['DirCos'])
            num_added += 1
    logger.info("ADDED %d, DUPED %d", num_added, num_duped)

def retrieve():
    for mill in TurboMillLocation.objects.all():
        retrieve_data(mill)

if __name__ == '__main__':
    retrieve()
