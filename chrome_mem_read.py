#! /usr/bin/env python
import sys
import fnmatch
import re

def mem_stat(pid):
    res = {'so_set': set(),
           'heaps': {},
           'ppid': -1,
           'state': '-1',
           'sigign': '-1',
           'sigcgt': '-1',
           'cmdline': '-1',
           'type': 'renderer'
           }

    with open('/proc/%s/cmdline' % pid, 'r') as fh:
        cmdline = fh.read()
        
        if 'zygote' in cmdline:
            t = 'zygote'
        elif 'gpu-process' in cmdline:
            t = 'gpu_process'
        elif 'gpu-broker' in cmdline:
            t = 'gpu_broker'
        elif 'extension-process' in cmdline:
            t = 'extension process'
        elif 'renderer' in cmdline:
            t = 'renderer'
        elif 'ppapi' in cmdline:
            t = 'ppapi'
        #elif cmdline == CHROME_PATH:
            #t = 'parent'
        else:
            t = cmdline
        res['cmdline'] = cmdline
        res['type'] = t
            
    with open('/proc/%s/status' % pid, 'r') as fh:
        for line in fh.readlines():
            label, value = line.split(':')
            if label in ['PPid', 'State', 'SigIgn', 'SigCgt']:
                res[label.lower()] = value.strip()

    with  open('/proc/%s/maps' % pid, 'r') as maps_file:
        i = 0
        for line in maps_file.readlines():                      # for each mapped region
            linelist = line.strip().split()
            
            # Heaps, mmaps
            if 'rw' in linelist[1] and len(linelist) == 5:  # ignores mapped files
                start = int(linelist[0].split('-')[0], 16)
                end = int(linelist[0].split('-')[1], 16)
                res['heaps'][start] = {'end': end}
                
            # Shared libraries
            if 'r-x' in linelist[1] and len(linelist) == 6 and not fnmatch.fnmatch(linelist[5], '[*]'):
                res['so_set'].add(linelist[5])
                
            i += 1

    return res


def mem_read(pid, token):

    maps_file = open('/proc/%s/maps' % pid, 'r')
    mem_file = open('/proc/%s/mem' % pid, 'r', 0)

    chunk = None
    location = None
    start = None

    # 7ffff2e45000-7ffff2e46000 rw-p 00014000 ca:01 942264 /usr/lib/chromium-browser/libs/libwebview.so
    # 7fffefa7f000-7fffefa82000 rw-p 00000000 00:00 0

    res = {}
    i = 0
    for line in maps_file.readlines():                      # for each mapped region
        linelist = line.strip().split()
        if 'rw' in linelist[1] and len(linelist) == 5:
            start = int(linelist[0].split('-')[0], 16)
            end = int(linelist[0].split('-')[1], 16)
            mem_file.seek(start)                            # seek to region start
            chunk = mem_file.read(end - start)              # read region contents
            location = chunk.find(token)                    # an offset in the chunk
            if location >= 0:
                res[i] = {}
                res[i]['found'] = 'found! %s, %s, %s' % (line.strip(), location, token)
                mem_file.seek(start + location)
                dump = mem_file.read(128)
                res[i]['dump'] = dump
        i += 1
        #else:
            #print 'no %s' % line
        #break
            
    maps_file.close()
    mem_file.close()
    
    return res

    #print start
    #print location

    #with open('/proc/%s/mem' % pid, 'r+') as fh:
        #fh.seek(start + location)
        # fh.seek(location)

        #d = fh.read(20)
        #print d,
        # fh.seek(location)

        #fh.write('whoa')
        #fh.seek(start + location)

        #print fh.read(40)
        
        
def mem_read_re(pid, regex):
    chunk = None
    location = None
    start = None

    res = {}
    i = 0
    with open('/proc/%s/maps' % pid, 'r') as maps_file:
        for line in maps_file.readlines(): 
            linelist = line.strip().split()
            if 'rw' in linelist[1] and len(linelist) == 5:
                start = int(linelist[0].split('-')[0], 16)
                end = int(linelist[0].split('-')[1], 16)
                with open('/proc/%s/mem' % pid, 'r', 0) as mem_file:
                    mem_file.seek(start) 
                    chunk = mem_file.read(end - start) 
                location = re.findall(regex, chunk)  
                return location
                i += 1
            
    maps_file.close()
    mem_file.close()
    
    return res
        
        

if __name__ == '__main__':

    pid = sys.argv[1]
    token = sys.argv[2]
    
    res = mem_read(pid, token)
    
    print res.keys()
    for key, item in res.iteritems():
        if 'found' in item.keys():
            print item['found']
