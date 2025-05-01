import pytest
import glob
import os

files = glob.glob('test/reports/**/*.yml', recursive=True)
for report in files:
    print(report)
    testout = os.popen("./gekko " + report).read()
    trueval = report.replace('reports', 'outputs').replace('.yml', '.txt')
    correctout = os.popen("cat " + trueval).read()
    assert(testout == correctout)
