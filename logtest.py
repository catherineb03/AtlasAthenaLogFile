# Returns check_log's exit code for a given log
# Used to test check_log is working correctly

import os
class Test:
    def __init__(self):
        pass
    def testcase(self,fileAddress,config,**kwargs):
        exitCode = os.system('python check_log.py --config '+config+' '+fileAddress + ' >ignore.txt')
        os.system('rm ignore.txt')
        return exitCode
