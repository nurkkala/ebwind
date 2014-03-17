from urllib import urlencode
from urllib2 import urlopen

from bs4 import BeautifulSoup
from dateutil.parser import parse

from windstream.models import *

# Known spans: 5min, 5minutes, 1day, 5days, 1hour (TODO: get more info from Windstream)

def open_url(install_id):
    url = 'http://ds.windstream-inc.com/WSData/api/performancedata.html'
    params = { 'installid': install_id,
               'span': '90min',
               'timezone': 'local',
               'sort': 'desc' }

    full_url = "{}?{}".format(url, urlencode(params))
    return urlopen(full_url)

def scrape_data(mill):
    print "Scraping {}".format(mill)
    soup = BeautifulSoup(open_url(mill.install_id))

    for row in soup.body.table.tbody.find_all('tr'):
        contents = [ datum.string for datum in row ]
        sample_time = parse(contents[0])
        try:
            sample = TurboMillSample.objects.get(location=mill, time_stamp=sample_time)
            print "ALREADY HAVE", sample.location, sample.time_stamp
        except TurboMillSample.DoesNotExist:
            print "ADDING", mill, sample_time
            TurboMillSample.objects.create(location=mill,
                                           time_stamp=sample_time,
                                           joules=contents[1],
                                           watts_avg=contents[2],
                                           volts_avg=contents[3],
                                           volts_peak=contents[4],
                                           volts_min=contents[5],
                                           amps_avg=contents[6],
                                           amps_peak=contents[7],
                                           speed_avg=contents[8],
                                           speed_peak=contents[9],
                                           dir_mag=contents[10],
                                           dir_ang=contents[11],
                                           dir_cos=contents[12])

def scrape():
    for mill in TurboMillLocation.objects.all():
        scrape_data(mill)

if __name__ == '__main__':
    scrape()
