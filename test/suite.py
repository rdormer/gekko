import pytest
import os

reports = os.listdir('test/reports')

for report in reports:
    print(report)
    testout = os.popen("./gekko test/reports/" + report).read()
    correctout = os.popen("cat test/outputs/" + report[:-4] + ".txt").read()
    assert(testout == correctout)
