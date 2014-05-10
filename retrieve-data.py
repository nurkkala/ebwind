#!/usr/bin/env python

from datetime import datetime, timedelta
from urllib import urlencode
from urllib2 import urlopen
import json
import logging

from django.utils.timezone import now

from windstream.models import *

# Span of hours to retrieve per query (maximum).
HOURS_PER_QUERY = 4

logger = logging.getLogger('ebwind.retrieve')

def open_url(install_id, start_timestamp):
    url = 'http://ds.windstream-inc.com/WSData/api/performancedata.json'
    params = { 'installid': install_id,
               'timezone': 'utc',
               'start': start_timestamp.strftime("%Y-%m-%d %H:%M"),
               'span': "{}hours".format(HOURS_PER_QUERY)

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
        start_timestamp = latest_sample.time_stamp
    except TurboMillSample.DoesNotExist:
        logger.debug("No sample for %s", mill)
        # N.B., earliest known date (for Matthews Community Center) is 2012-11-29.
        start_timestamp = datetime(2012, 11, 29, 0, 0, 0)

    num_added = num_skipped = 0
    stop_timestamp = now()
    sixty_minutes = timedelta(hours=HOURS_PER_QUERY)
    logger.info("START %s", start_timestamp)
    logger.info("STOP  %s", stop_timestamp)
    while start_timestamp < stop_timestamp:
        # The JSON feed prefixes thedata with a Unicode Byte Order Mark (BOM). This
        # decoding removes the mark.
        logger.info("Retrieving %s from %s", mill, start_timestamp)
        raw = open_url(mill.install_id, start_timestamp).read().decode('utf-8-sig')
        data = json.loads(raw)

        for datum in data:
            try:
                sample = TurboMillSample.objects.get(location=mill, time_stamp=datum['TimeStamp'])
                logger.debug("ALREADY HAVE %s at %s", sample.location, sample.time_stamp)
                num_skipped += 1
            except TurboMillSample.DoesNotExist:
                logger.debug("ADDING %s at %s", mill, datum['TimeStamp'])
                num_added += 1
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
        start_timestamp += sixty_minutes

    logger.info("ADDED %d, SKIPPED %d", num_added, num_skipped)

def retrieve():
    for mill in TurboMillLocation.objects.all():
        retrieve_data(mill)

if __name__ == '__main__':
    retrieve()
