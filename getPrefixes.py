#!/usr/bin/env python

import os
import errno
import netsnmp
from datetime import date
from time import strftime
import pprint

curdate = strftime("%Y.%m.%d")
logfile = "/var/log/bgpdata/bgpprefixes"
loghead = str('{"index":{"_index":"bgpprefixdata-'+ curdate + '","_type":"prefixdata"}}')

"""
SNMP SPECIFIC VARIABLES
"""
os.environ["MIBS"] = "ALL"
version = 2
community = ""
asQueryString = "bgpPeerRemoteAs."
prefixQueryString = "cbgpPeerAcceptedPrefixes."

"""
HOST AND PEER VARIABLES
"""
host1 = ""
host2 = ""
peer1 = ""
peer2 = ""

"""
This checks if a logfile exists for today and creates it if one
is not present
"""
def createLogfileIfNeeded( filename ):
  flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
  try:
    file_handle = os.open(filename, flags)
  except OSError as e:
    if e.errno == errno.EEXIST:
      pass
    else:
      raise
  else:
    with os.fdopen(file_handle, 'w') as file_obj:
      file_obj.close()

"""
This writes a log header is json format which should correspond with an
elasticsearch index pattern
"""
def writeToLog( filename, data ):
  flags = os.O_APPEND | os.O_WRONLY
  try:
    file_handle = os.open(filename, flags)
  except OSError as e:
    if e.errno == errno.EROFS:
      raise
    else:
      pass
  else: 
    with os.fdopen(file_handle, 'a') as file_obj:
      file_obj.write(str(data))
      file_obj.write("\n")
      file_obj.close()

"""
This uses SNMP to retrieve the AS Number and the number of prefixes currently
being accepted by that peer
"""
def getAsAndPrefixes(host, peer):
  today = strftime("%Y-%m-%d")
  timeNow = strftime("%H:%M")
  recordtime = today + "T" + timeNow
  asQuery = netsnmp.Varbind(asQueryString + peer)
  prefixQuery = netsnmp.Varbind(prefixQueryString + peer)
  
  peerAs = netsnmp.snmpget(asQuery, Version=version, DestHost=host, Community=community)
  asn = peerAs[0]
  acceptedPrefixes = netsnmp.snmpwalk(prefixQuery, Version=version, DestHost=host, Community=community)
  prefixes =  acceptedPrefixes[0]
  data = str('{"@timestamp":"' + recordtime  + '",  "asn":' + asn + ',"prefixes":' + prefixes  + '}')
  writeToLog( logfile, loghead)
  writeToLog( logfile, data )

createLogfileIfNeeded(logfile)
getAsAndPrefixes(host1, peer1)
getAsAndPrefixes(host2, peer2)
