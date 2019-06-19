import logtest

invigilator = logtest.Test()

# Replace testExpected with the names and expected exit codes of the logs you're using to test
testExpected = {"athena.log.1": 10, "athena.log.2": 10, "athena.log": 0}
testOutcome = testExpected.copy()


def testlog(logName, expectedValue):
	print(expectedValue)
    realValue = invigilator.testcase(logName,config='t.conf')
    print(realValue)
    return (realValue == expectedValue) # If the values match, returns True


for k in testExpected:
	v = testExpected[k]
	testOutcome[k] = testlog(k, v)

print(testOutcome) # If False, something broke
