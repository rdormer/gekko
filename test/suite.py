import glob
import os

ANSI_RED = '\033[91m'
ANSI_RESET = '\033[0m'

files = glob.glob('test/reports/**/*.yml', recursive=True)
for report in files:
    print(report)
    testout = os.popen("./gekko " + report).read()
    trueval = report.replace('reports', 'outputs').replace('.yml', '.txt')
    correctout = os.popen("cat " + trueval).read()

    if(testout != correctout):
        print(ANSI_RED + "FAIL: " + report + ANSI_RESET)
