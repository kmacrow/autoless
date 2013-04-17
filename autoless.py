#!/usr/bin/env python

import os
import sys
import stat
import time
import sched
import signal
import optparse

# stat files every second
STAT_FREQUENCY = 1

# could use this for other scripts...
FILE_EXTENSION = '.less'


# get a file's atime (last modified on unix)
def filemtime(file_name):
    return os.stat(file_name).st_mtime


# main()  
def autoless():

    cwd = os.getcwd()
    
    # cache a mapping of file : last known atime
    watch = {}
    
    s = sched.scheduler(time.time, time.sleep)
    
    # build watch map
    for script_name in os.listdir('.'):
        script_name = os.path.join(cwd, script_name)
        
        # brutally simple filter
        if script_name.endswith(FILE_EXTENSION):
            watch[script_name] = filemtime(script_name)
            
    
    print 'Watching %d %s scripts...' % (len(watch), FILE_EXTENSION)
    
    # stat watched scripts every x seconds to check mtimes
    def check_scripts():
        
        # need to build?
        make  = False
        
        for script_name in watch:
            atime = filemtime(script_name)
            
            # modified since we last checked?
            if atime > watch[script_name]:
                
                # update map
                watch[script_name] = atime
                
                # trigger build
                make = True
                
                # poorly thought out optimization?
                break
        
            
        if make:
            # brutally simple build
            os.system('make')    
        
        # check again in x seconds    
        s.enter(STAT_FREQUENCY, 1, check_scripts, ())
        
    
    # handle ^C at the terminal
    def sigint(sig, frame):
        print "\nCaught ^C exiting..."
        sys.exit(0)
         
     
     
    signal.signal(signal.SIGINT, sigint)
    
    # check in x seconds
    s.enter(STAT_FREQUENCY, 1, check_scripts, ())        
    
    # infinite loop
    s.run()
        
         

if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option('-t','--type',dest='type',help='The file extension to watch.')
    p.add_option('-f','--freq',dest='freq',help='How often to stat files (sec)')
    (o, a) = p.parse_args()
    
    if o.type != None:
        FILE_EXTENSION = '.'+o.type
    if o.freq != None:
        STAT_FREQUENCY = int(o.freq)
                 
    autoless()
