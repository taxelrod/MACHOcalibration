#!/usr/bin/env python

import requests
import sys

if __name__ == "__main__":

    SMASHcat = sys.argv[1]
    MACHOcat = sys.argv[2]

    r = requests.post(
         'http://cdsxmatch.u-strasbg.fr/xmatch/api/v1/sync',
         data={'request': 'xmatch', 'distMaxArcsec': 1.5, 'RESPONSEFORMAT': 'CSV',
               'colRA1': 'RA', 'colDec1': 'DEC', 'colRA2': 'RA', 'colDec2': 'DEC'},
         files={'cat1': open(MACHOcat, 'r'), 'cat2': open(SMASHcat, 'r')})

    h = open('results.csv', 'w')
    h.write(r.text)
    h.close()

