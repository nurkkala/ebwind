from urllib import urlencode
from urllib2 import urlopen
import json

from windstream.models import *

# Earliest date (for Matthews) is 2012-11-29.

def open_url(install_id):
    url = 'http://ds.windstream-inc.com/WSData/api/performancedata.json'
    params = { 'installid': install_id,
               'timezone': 'utc',
               'start': '2012-11-30 00:00',
               'span': '1day'
    }

    full_url = "{}?{}".format(url, urlencode(params))
    return urlopen(full_url)

def retrieve_data(mill):
    print "Retrieving {}".format(mill)
    raw = open_url(mill.install_id).read().decode('utf-8-sig')
    data = json.loads(raw)

    num_added = num_duped = 0

    for datum in data:
        try:
            sample = TurboMillSample.objects.get(location=mill, time_stamp=datum['TimeStamp'])
            print "ALREADY HAVE", sample.location, sample.time_stamp
            num_duped += 1
        except TurboMillSample.DoesNotExist:
            print "ADDING", mill, datum['TimeStamp']
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
    print "Added {}, Duped {}".format(num_added, num_duped)


def retrieve():
    for mill in TurboMillLocation.objects.all():
        retrieve_data(mill)

if __name__ == '__main__':
    retrieve()
