"""ONACommandLine.py:
A sample command line interface for the ONA-1000
Dependencies:
ONA1000Controls (dependency: TBControllerCommon)"""

from ONA1000Controls import *

#When DEBUG=True, uses *REM VISIBLE ON (for debugging only)
#Otherwise, when DEBUG is False, uses *REM command
DEBUG=False

#START MAIN
#Get the ip address and attempt to connect
ipaddr=input(f"Please enter the ip address of the ONA-1000 to connect:\n")
try:
    ona1=ONA1000Controls(targetip=ipaddr, timeout=10, debug=DEBUG)
    time.sleep(1)
    ona1.connect()
except Exception as e:
    print(f"Did not connect to ONA-1000 Correctly: Exception {e}")
while not ona1.isConnected:
    #Attempt to connect again
    ipaddr=input("Please enter the ip address of the ONA-1000 to connect:\n")
    try:
        ona1=ONA1000Controls(targetip=ipaddr, timeout=10, debug=DEBUG)
        ona1.connect()
    except Exception as e:
        print(f"Did not connect to ONA-1000 Correctly: Exception {e}")
writelog("Entering Remote mode.")
ona1.setRemoteOn()
time.sleep(1)
#Bring up app selection screen automatically after connecting to remote   
#Will automatically reconnect if necessary
try:
    ona1.runCommand("MULTIAPP")
except Exception as e:
    print(f"Start Command did not run: Exception {e}")

notExit=True
while notExit:
    #Prompt for command and then format it
    activeapp=ona1.getActiveApp()
    if activeapp is None:
        print("No app currently active.")
    elif isinstance(activeapp, Application):
        print(f"Active App: {activeapp.getappname()}, Port{activeapp.getPort()}")
    else:
        print("Error: getActiveApp returned wrong type")
    cmdval=input("Enter a command or enter \"HELP\" for help:\n")
    try:
        if ona1.runCommand(cmdval) == "EXIT":
            notExit=False
    except Exception as e:
        print(f"Command did not run: Exception {e}")

"""
Any question about the script, please contact Brad Sicotte at 
email: bsicotte@teracomm.com
"""
        
