import sys
sys.path.append('R:/Housman_Code/')
from r_numpy_lib import *
########################################################
x = [
      [
        -108.6328125,
        40.979898069620155
      ],
      [
        -87.1875,
        38.548165423046584
      ],
      [
        -98.4375,
        29.84064389983441
      ],
      [
        -99.4921875,
        33.43144133557529
      ]
    ]

#kml name
out_kml = 'R:/Phase3_GEE/test.kml'


#call
xy_list_to_kml(x, out_kml, '', 'geog',0, 1   )