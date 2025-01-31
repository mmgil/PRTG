#!/usr/bin/env python3
"""This is an example Python script for the Script v2 sensor.
The script provides the result of rolling of an n-sided die.
The script uses the integer parameter '--sides' to determine the number of sides of the die.
If the parameter is omitted, the number of sides default to 6.
"""
import argparse  # needed to parse the script arguments
import json  # needed to construct the result message
import random  # needed for the random die roll
import shlex  # needed to parse arguments passed via pipe to stdin (PRTG uses this invocation style)
import sys  # needed to check if script is invoked from a tty or through a pipe
def fail(message: str):
    """
    Return error message to PRTG and abort the sensor script.
    This function can be used to reduce code duplication by having a common way to fail the sensor script
    Be careful with the message you pass here. As the message will be shown in PRTG as the Sensor message.
    You could potentially leak sensitive data in the sensor message if you pass an unfiltered exception.
    It is recommended only catch errors on which the user immediately can act on.
    In general exceptions should not be caught and the sensor debug log on the probe should be checked for the
    detailed error.
    """
    print(
        json.dumps(
            {
                "version": 2,
                "status": "error",
                "message": message,
            }
        )
    )
    """
    Scripts always need to exit with EXITCODE=0.
    Otherwise the Sensor will fail to recognize your script output and interpret the sensor run as failed.
    """
    exit(0)
def setup():
    """
    Parse the arguments from stdin or cli when running interactive and return them
    as a dict.
    Construct the ArgumentParser without `exit_on_error`. This allows us to forward the error to PRTG.
    """
    argparser = argparse.ArgumentParser(
        description="The script provides the result of rolling of an n-sided die",
        exit_on_error=False,
    )

    """ Define your arguments here."""
    argparser.add_argument(
        "--sides", type=int, default=6, help="The number of sides the die has."
    )
    try:
        """Check if script is executed interactively first. Otherwise expect arguments from stdin."""
        if sys.stdin.isatty():
            args = argparser.parse_args()
        else:
            pipestring = sys.stdin.read().rstrip()
            args = argparser.parse_args(shlex.split(pipestring))
    except argparse.ArgumentError:
        """ In case of an argparse.Argument error we suspect something wrong with the parameters on invocation"""
        fail("Could not parse input parameter. Check configured `Parameters` in `Script Settings`")
    return vars(args)
def work(args: dict):
    """
    The work function implements the sensor logic and returns the sensor result as a dict.
    Implement your sensor logic here.
    Read the sides parameter from args. This is the work the sensor performs.
    """
    result = random.randrange(1, args["sides"] + 1)
    """
    Construct your sensor result here
    Create a dict adhering to the expected JSON output format
    """
    return {
        "version": 2,  # The script output schema version to use
        "status": "ok",  # The sensor status
        "message": f"The die rolled {result}",  # The sensor message
        "channels": [
            {
                "id": 10,
                "name": "Last Roll",
                "type": "integer",
                "value": result,
            }
        ],
    }
if __name__ == "__main__":
    args = setup()  # Retrieve script arguments
    sensor_result = work(args)  # Execute sensor logic
    print(json.dumps(sensor_result))  # Format the result to JSON and print them to stdout.
    exit(0)