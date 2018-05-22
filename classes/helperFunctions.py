# -*- coding: utf-8 -*-

from datetime import timezone
import re
import emoji
import numpy as np

class helperFunctions():  
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    def extract_emojis(str):
        #str = str.decode('utf-32').encode('utf-32', 'surrogatepass')
        #return list(c for c in str if c in emoji.UNICODE_EMOJI)
        return list(c for c in str if c in emoji.UNICODE_EMOJI)
    def getRectangleBounds(points):
        lats = []
        lngs = []
        for point in points:
            lngs.append(point[0])
            lats.append(point[1])
        limYMin = np.min(lats)       
        limYMax = np.max(lats)    
        limXMin = np.min(lngs)       
        limXMax = np.max(lngs)
        return limYMin,limYMax,limXMin,limXMax