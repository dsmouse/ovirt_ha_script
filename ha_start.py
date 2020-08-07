#! /usr/bin/python

from ovirtsdk.api import API
from ovirtsdk.xml import params
import time
import json
from pprint import pprint
import os 
import subprocess

VERSION = params.Version(major='4', minor='0')
 
#
URL="https://10.1.2.4/ovirt-engine/api"
USERNAME="admin@internal"
PASSWORD="password"
CERT="cert.ca"


BASEDIR=None
TAGS=( "HA1", "HA2", "HA3", "HA4", "HA5") 


def start_tag(tag): 
    try:
        api = API(url=URL, username=USERNAME, password=PASSWORD, ca_file=CERT, insecure=True)
    
        print "Connected to %s successfully!" % api.get_product_info().name
        for vm in  api.vms.list(query="tag=%s" % tag) :
            print("VM %s is in state %s" %( vm.get_name() , vm.status.state))
    #           print vm.get_name()
    #           print(dir(vm))
            try:
               if vm.status.state != 'up':
    #                   print("VM %s is in state %s" %( vm.get_name() , vm.status.state))
                  print 'Starting VM'
    #                   vm.get(VM_NAME).start()
                  vm.start()
                  print 'Waiting for VM to reach Up status'
    #                   while vm.get(VM_NAME).status.state != 'up':
                  count=30
                  while vm.status.state != 'up' and count > 0:
                     time.sleep(1)
                     count=count-1
               else:
                  print 'VM already up'
            except Exception as e:
                print 'Failed to Start VM:\n%s' % str(e)
            time.sleep(6)
               
    
    
        api.disconnect()
    
    except Exception as ex:
        print "Unexpected error: %s" % ex

def bootid():  
    with open('/proc/sys/kernel/random/boot_id', 'r') as f:
        boot_id=f.readline()
        return(boot_id)
def uptime2():  
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return(uptime_seconds)

def wait_for_complete(tag):
    scriptfile="%s/completion_script_%s" %( BASEDIR, tag)
    print("Looking for: ", scriptfile)
    if os.path.exists(scriptfile):
       subprocess.call(scriptfile)

if BASEDIR is None:
   BASEDIR = os.getcwd()


for tag in TAGS :
    print "Tag: %s" % ( tag)
    start_tag(tag)
    wait_for_complete(tag) 

## if uptime > x Minutes: I don't want to start these till base system stableizes 
if uptime2() > 600:
   boot_id=bootid()
   preexisting=False
   with open("ha_start.bootstate",'r') as f:
        pastboot=f.readline()
        if (boot_id == pastboot ) :
            preexisting=True 
   if (preexisting==False):
       for tag in ( "OnBoot", "OnBoot2" ) :
           print "Tag: %s" % ( tag)
           start_tag(tag)
           wait_for_complete(tag) 
#### add current to boot_id
   with open("ha_start.bootstate",'w') as f:
        f.write(boot_id) 

##
