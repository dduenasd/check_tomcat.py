#! /usr/bin/env python
# -*- coding: utf-8 -*-

# I'm a Spanish speaker, my English is basic but I try to write everything in English.
# Many translations have been made with automatic translators.
# If something is not meant pray excuse me.
# ¡VAMOS A ELLO! (LET'S GO!)

#-------------------------------------------------------------------------------
# Name:        check_tomcat.pl
# Purpose:
# Plugin para chequeo de servidor tomcat para nagios
# Check tomcat server plugin for nagios
# It plugin uses the status?XML=true page of tomcat, this page usually is:
# http://host-name:8080/manager/status?XML=true
#
# Author:      Daniel Dueñas
#
# This plugin conforms to the Nagios Plugin Development Guidelines
# https://nagios-plugins.org/doc/guidelines.html
#
# Created:     18/02/2014
# Copyright:   (c) Daniel Dueñas 2014
# Licence:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#-------------------------------------------------------------------------------

import argparse, sys
import urllib2
import socket
import xml.etree.ElementTree as ET
from math import log

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#VARIABLE DEFINITIONS
#--------------------------------------------------------------------------
version="1.0"   #Plugin version
status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}
exit_status = 'OK'
output = ""
longoutput = ""
perfdata = ""
mensage = ""
plugin_description ='''Nagios plugin for check an apache tomcat server
'''
mode_help ='''Tomcat monitorizacion mode:
    status: The status of tomcat server
    mem:    Tomcat server used percentage memory status, warning and critical values
            requiered in percentage.
    thread: Tomcat connectors Threads used, warning and critical values requiered.
            The parameter connector is optional, if not exists, all connector were shown.
'''
tree_xml=None

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#FUNCTIONS
#-------------------------------------------------------------------------
#Try if string is a float
def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

#This function define the range of warning and critical values
#Return a range --> (min,max,True/False)
#if True, data must be in a range
#if False, data must be out of a range
def define_range(str):
    if is_float_try(str):
        range = (0,float(str),True)  # x -> in range(0,x)
    elif str.count(":")==1:
        splits = str.split(":")
        if is_float_try(splits[0]) and is_float_try(splits[1]):
            range=(float(splits[0]),float(splits[1]),True) # x:y  -> in range(x,y)
        elif is_float_try(splits[0]) and splits[1]=="":
            range=(float(splits[0]),float("inf"),True)  # x:  -> in range(x,infinite)
        elif splits[0]=="~" and is_float_try(splits[1]):
            range=(float("-inf"),float(splits[1]),True) # ~:x -> in range(-infinite,x)
        if splits[0][0]=="@" and is_float_try(splits[0].replace("@","")) and is_float_try(splits[1]):
            range=(float(splits[0].replace("@","")),float(splits[1]),False) # @x:y -> out of range(x,y)
    else:
        print "bad range definition in "+str
        sys.exit(1) #Error in range definition
    if range[0]<range[1]:
        return range   # OK
    else:
        print "Second value of range "+str+" is less than first value"
        exit(1)

#Critical and warning function resolve
#This function return exit_status: OK,WARNING,CRITICAL or UNKNOWN string
def define_status(value,warning,critical):
    warning_range = define_range(warning)  #Define warning range
    critical_range = define_range(critical)#Define critical range
    val=float(value)                       #The value
    exit_status="UNKNOWN"                   #status by default

    if args.verbosity:
        print "Value for test: "+str(value)
        print "Warning range (min:%s max:%s in_range:%s)"%(str(warning_range[0]),str(warning_range[1]),str(warning_range[2]))
        print "Critical range (min:%s max:%s in_range:%s)"%(str(critical_range[0]),str(critical_range[1]),str(critical_range[2]))

    #value into the range range(x:y:True)
    if warning_range[2]==True and critical_range[2]==True:
        if (warning_range[1]>critical_range[1]) or (warning_range[0]<critical_range[0]):
            parser.print_usage()
            parser.exit(3,"ERRROR: critical range (%s) is greater than warning range(%s)\n" % (critical, warning))
        if value<warning_range[0] or value>warning_range[1]:
            exit_status="WARNING"
            if value<critical_range[0] or value>critical_range[1]:
                exit_status="CRITICAL"
        else:
            exit_status="OK"
    #value out of range range(x:y:False)
    elif warning_range[2]==False and critical_range[2]==False:
        if (warning_range[1]<critical_range[1]) or (warning_range[0]>critical_range[0]):
            parser.print_usage()
            parser.exit(3,"ERRROR: critical range (%s) is greater than warning range(%s)\n" % (critical, warning))
        if value>warning_range[0] and value<warning_range[1]:
            exit_status="WARNING"
            if value>critical_range[0] and value<critical_range[1]:
                exit_status="CRITICAL"
        else:
            exit_status="OK"
    #warning and critical ranges must be both in or out
    else:
        parser.print_usage()
        parser.exit(status[exit_status],'''
ERROR: Both critical and warning values must be in or out of the ranges:
       warning('''+warning+''') and critical ('''+critical+''')\n''')

    return exit_status

# convert human readable size function
def sizeof_fmt(num):
    # Human friendly size
    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 0:
        return '0 bytes'
    elif num == 1:
        return '1 byte'
    elif num < 0:
        return 'negative number'
    else:
        return None

#open tomcat status html
def read_page(host,port,url,user,password):
    url_tomcat = "http://"+host+":"+port+url
    if args.verbosity:
        print "connection url: %s\n"%(url_tomcat)

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None,url_tomcat,user,password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener=urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    req = urllib2.Request(url_tomcat)
    handle = urllib2.urlopen(req,None,5)

    # Store all page in a variable
    page = handle.read()
    # End of Open manager status
    if args.verbosity>2:
        print "page "+url_tomcat+" content:"
        print page
    # Read xml string
    root = ET.fromstring(page)
    if args.verbosity>1:
        print ET.dump(root)

    return root
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ARGPARSE OBJECT DEFINITION
#---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description=plugin_description,
                                formatter_class=argparse.RawTextHelpFormatter)
parser.version = parser.prog+" 1.0"
parser.add_argument('-V','--version', action='version',
                    help="Show plugin version",
                    version='%(prog)s '+version)
parser.add_argument('-v', '--verbosity',action="count",
                    help='''increase output verbosity:
                    -v Single line, additional information (eg list processes that fail)\n
                    -vv Multi line, configuration debug output (eg ps command used)
                    -vvv Lots of detail for plugin problem diagnosis
                    ''')
# Connection parameters
conn_parameters = parser.add_argument_group('Connection parameters',
                  'parameters for Tomcat connection')
conn_parameters.add_argument('-H', '--host',
                    help="Name or Ip of tomcat host",
                    required=True)
conn_parameters.add_argument('-p','--port',
                    help="Tomcat port (Example:8080)",
                    required=True)
conn_parameters.add_argument('-u','--user',
                    default = "admin",
                    help="Tomcat user")
conn_parameters.add_argument('-a','--authentication',
                    metavar='PASS',
                    default = "tomcat",
                    help="Tomcat authentication password")
conn_parameters.add_argument('-U','--URL',
                    default = "/manager/status?XML=true",
                    help='''Tomcat XML status page URL "/manager/status?XML=true" by default''')
conn_parameters.add_argument('-C','--connector',
                    help='''Connector name, used in thread mode''')

parameters = parser.add_argument_group('Monitirization parameters',
             'Parameters for tomcat monitorization')
parameters.add_argument('-w','--warning',
                    help="Warning value")
parameters.add_argument('-c','--critical',
                    help="Critical value")
parameters.add_argument('-m','--mode',
                    choices=['status','mem','thread'],
                    help=mode_help,
                    required=True)

#Corrects negative numbers in arguments parser
for i, arg in enumerate(sys.argv):
  if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
# arguments parse
args = parser.parse_args()
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



#No arguments
if sys.argv[1:] == []:
    parser.print_usage()
    parser.exit(status['UNKNOWN'],
                "ERROR: No arguments, write '"+parser.prog+" -h' for help\n")

if args.verbosity!=None:
    if args.verbosity>3:
        args.verbosity=3
    print "verbosity level = %i\n"%(args.verbosity)

if args.verbosity:
    print "Arguments: %s" %(str(args))
#plugin logic...



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#MODE OPTIONS LOGIC
#-------------------------------------------------------------------------
#Error handling
try:
   tree_xml=read_page(args.host,args.port,args.URL,args.user,args.authentication)
except urllib2.HTTPError as e:
   output="ERROR: The server couldn\'t fulfill the request. Error code: %s" %(e.code)
   exit_status='UNKNOWN'
except urllib2.URLError as e:
   output = 'ERROR: We failed to reach a server. Reason: %s' %(e.reason)
   exit_status='UNKNOWN'
except socket.error as e:
   output = "ERROR: Dammit! I can't connect with host "+args.host+":"+args.port
   exit_status='UNKNOWN'
except:
   output = "ERROR: Unexpected error (I'm damned if I know!): %s"%(sys.exc_info()[0])
   exit_status='UNKNOWN'

# status option
if args.mode == 'status':
    if tree_xml!=None:
        if tree_xml.tag=='status':    #The first tag of xml is "status"
            output="The Tomcat server is up"
            exit_status='OK'
        else:
            output="This server is not a tomcat server or not status xml page"
            exit_status='UNKNOWN'
    else:
        exit_status='CRITICAL'

# mem option
if args.mode == 'mem':
    if tree_xml!=None:
        #control warning and critical values
        if (args.warning==None) or (args.critical==None):
            parser.print_usage()
            parser.exit(status['UNKNOWN'],
                        'ERROR: Warning and critical values requiered with mode "mem"\n')
        memory = tree_xml.find('.//memory')
        free_memory = float(memory.get('free'))
        total_memory = float(memory.get('total'))
        max_memory = float(memory.get('max'))
        available_memory = free_memory + max_memory - total_memory
        used_memory = max_memory - available_memory
        percent_used_memory = float((used_memory * 100)/max_memory)
        if args.verbosity:
            print "mode: mem(memory)"
            if args.verbosity > 1:
                print "free:%0.1f total:%0.1f max:%0.1f available:%0.1f used:%0.1f percent_used:%0.2f"%(free_memory,
                                        total_memory,max_memory,available_memory,used_memory,percent_used_memory)
            print "free_memory:%s total memory:%s max_memory:%s"%(sizeof_fmt(free_memory),sizeof_fmt(total_memory),sizeof_fmt(max_memory))
            print "available_memory = free_memory + max_memory - total_memory -->  %s" %(sizeof_fmt(available_memory))
            print "used_memory = max_memory - available_memory -->  %s" %(sizeof_fmt(used_memory))
            print "percent_used_memory = (used_memory * 100)/max_memory  -->  %0.2f%%\n"%(percent_used_memory)

        #Define status whit function
        exit_status=define_status(percent_used_memory,args.warning,args.critical)
        output="Used memory "+sizeof_fmt(used_memory)+" of "+sizeof_fmt(max_memory)+"(%0.2f%%)" %(percent_used_memory)
        perfdata="'Used_memory'=%0.0f%%;%s;%s"%(percent_used_memory,args.warning,
                                                    args.critical)

# threads option
if args.mode == 'thread':
    if tree_xml!=None:
        #control warning and critical values
        if (args.warning==None) or (args.critical==None):
            parser.print_usage()
            parser.exit(status['UNKNOWN'],
                        'ERROR: Warning and critical values of number of threads open is requiered with mode "thread"\n')
        if(args.connector==None):
            if (args.verbosity>0): print "Finding all connectors"
            for connector in tree_xml.findall('./connector'):
                connector_name = str(connector.get('name'))
                if (args.verbosity>0): print "Find %s connector"%(connector_name)
                thread = connector.find('./threadInfo')
                max_thread = float(thread.get('maxThreads'))
                busy_thread = float(thread.get('currentThreadsBusy'))
                iter_status=define_status(busy_thread,args.warning,args.critical)
                if status[iter_status] > status[exit_status]:
                        exit_status=iter_status
                output = output + '/connector:%s %0.0f threads busy of %0.0f '%(connector_name,busy_thread,max_thread)
                perfdata = perfdata + "'conn %s'=%0.0f;%s;%s;0;%0.0f "%(connector_name,busy_thread,args.warning,args.critical,max_thread)

        else:
            if (args.verbosity>0): print "Finding %s connector"%(args.connector)
            for connector in tree_xml.findall('./connector'):
                connector_name = str(connector.get('name'))
                if (args.connector==connector_name):
                    if (args.verbosity>0):
                        print "Find %s connector"%(connector_name)
                    thread = connector.find('./threadInfo')
                    max_thread = float(thread.get('maxThreads'))
                    busy_thread = float(thread.get('currentThreadsBusy'))
                    exit_status=define_status(busy_thread,args.warning,args.critical)
                    output = output + 'connector:%s %0.0f threads busy of %0.0f '%(connector_name,busy_thread,max_thread)
                    perfdata = perfdata + "'conn %s'=%0.0f;%s;%s;0;%0.0f "%(connector_name,busy_thread,args.warning,args.critical,max_thread)

if output=='':
    output = "ERROR: no output"
    exit_status ='UNKNOWN'
message = exit_status + " " + output
if perfdata!="":
    message = message + '|' + perfdata
if longoutput!="":
    message = message + longoutput
print message
sys.exit(status[exit_status])