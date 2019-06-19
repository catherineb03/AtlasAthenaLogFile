import re
import argparse
import sys

desc = 'Tool to check for error messages in a log file. By default ERROR, FATAL \
  and CRITICAL messages are considered. The config file may be used to \
provide patterns of lines to exclude from this check - known false positives. \
If no config file is provided, all errors will be shown.'

epilogue = 'Note that at least one of errors and warnings must be true, otherwise there is nothing to search for.\
    Using --errors will disable errors.'

errorRegex = ["^ERROR | ERROR | FATAL |CRITICAL |ABORT_CHAIN",
"^Exception\:|^Caught signal|^Core dump|Traceback|Shortened traceback|stack trace|^Algorithm stack\:|IncludeError|ImportError|AttributeError|inconsistent use of tabs and spaces in indentation\
|glibc detected|tcmalloc\: allocation failed|athenaHLT.py\: error"]

traceback = ['Traceback|Shortened traceback|^Algorithm stack']

warningRegex = ['WARNING']

def main():
    parseOptions()
    parseConfig()
    scanLogfile()
    printResults()

def parseOptions():
    parser = argparse.ArgumentParser(description=desc, epilog=epilogue)
    parser.add_argument('logfile',metavar='<logfile>')
    parser.add_argument('--config',
    metavar='<file>',
    type = str,
    help ='specify config file (default is check_log.conf) will be got from cwd if it does not exist',
    default='check_log.conf'
    )
    parser.add_argument('--showexcludestats',
    action = 'store_true',
    default = False,
    help ='print a summary table of the number of times each of the exclude patterns was matched (default False)'
    )
    parser.add_argument('--warnings',
    action = 'store_true',
    default = False,
    help ='check in addition for WARNING messages (default False)'
    )
    parser.add_argument('--errors', 
    action = 'store_false',
    default = True,
    help = 'check errors (default true)'
    )
    global args
    args = parser.parse_args()
    print(args)
    if not (args.errors or args.warnings): 
        print('error: at least one of errors and warnings must be enabled')
        sys.exit(4) # error codes have been changed from the Perl script

# Parses the config file provided into a list (ignorePattern)
# If no config file is used, all results will be printed to the terminal
def parseConfig():
    global ignorePattern
    global noConfig
    ignorePattern = []
    configFileAddress = args.config
    try: 
        with open(configFileAddress,'r') as configFile:
            for aline in configFile:
                if 'ignore' in aline:
                  line = aline.strip('ignore').strip().strip("'")
                  ignorePattern.append(line)
        noConfig = False
    except:
      print('NO CONFIG FILE FOUND, NOTHING WILL BE IGNORED')
      noConfig = True

def scanLogfile():
    resultsA =[]
    global pattern
    pattern = []
    tPattern = re.compile('|'.join(traceback))
    global msgLevels
    global logFileAddress
    if args.warnings == True:
        pattern.extend(warningRegex)
    if args.errors == True:
        pattern.extend(errorRegex)
    msgLevels = re.compile('|'.join(pattern))
    igLevels = re.compile('|'.join(ignorePattern))
    logFileAddress = args.logfile
    try:
        with open(logFileAddress,'r') as logFile:
            tracing = False
            for line in logFile:
                if re.search(tPattern,line):
                    tracing = True
                elif line =='\n':
                    tracing = False
                if re.search(msgLevels,line):
                    resultsA.append(line)
                elif tracing:
                    resultsA.append(line)
    except:
        sys.exit(2)
    if args.showexcludestats and not noConfig:
        seperateIgnoreRegex = [re.compile(line) for line in ignorePattern]
        global ignoreDict
        ignoreDict = {line:False for line in ignorePattern} # stores ignored errors/warnings       
    global results
    results = []
    if noConfig:
        results = resultsA
        return
    for i in range(len(resultsA)):
        if not re.search(igLevels,resultsA[i]):
            results.append(resultsA[i])
        elif args.showexcludestats:
            for i in range(len(seperateIgnoreRegex)):
                if re.search(seperateIgnoreRegex[i],line):
                    ignoreDict[ignorePattern[i]] = True
  
def printResults():
    global pattern
    print('Checking for: '+ str(pattern) +' in log.\n')
    if args.showexcludestats and not noConfig:
        print('Ignored:')
        for i in ignoreDict:
            if ignoreDict[i]:
                print(i)
        print('\n')
    print('Found messages in '+ logFileAddress +':')
    if len(results) > 0:
        for msg in results: print(msg.strip('\n'))
        print("FAILURE : error/fatal found in " + logFileAddress)
        sys.exit(10)

main()
