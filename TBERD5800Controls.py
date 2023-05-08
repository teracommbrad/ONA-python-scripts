"""File TBERD5800Controls.py
V4 - Restructured to depend on TBControllerCommon.py
Defines TBerd5800Controls class, which is a modified version of the 
RemoteControl5800 class from tberd5800scriptSample.py originally by Sean Li
v2.0 Removed dependency on tberd5800scriptSample.py
v3.0 Removed dependency on TBERDCommandTypes
v3.1 Limited exceptions thrown, to make connection functions threadsafe
Depends on TBERDCommandTypes.py which should be included with this file"""

"""Note that this is a significantly modified version of RemoteControl5800 from tberd5800scriptSample.py,
with additional features, such as verbose vs not verbose mode (non-verbose is silent, verbose is verbose)

Also, note that the peek and poke commands take a little over 1 second each.
If you try to peek too quickly, you get old values. 

"""

"""Common Apps
Other common apps can be added in format
{"name":APPNAME, "appId":appid}"""

commonapps=[{"name":"100 Gig E Layer 2 Traffic Terminate", "appId":"TermEth100GL2Traffic"}, 
            {"name":"100 Gig E Kr4 FEC Layer 2 Traffic Terminate", "appId":"TermEth100GL2TrafficRsFEC"},
            {"name":"10 Gig E Layer 2 Traffic Terminate", "appId":"TermEth10GL2Traffic"},
            {"name":"25 Gig E Layer 2 Traffic Terminate", "appId":"TermEth25GL2Traffic"}]

from TBControllerCommon import *
import traceback
class TBERD5800Controls(Controller_base):
    """class TBERD5800HLControls: A high-level control class for the T-BERD 5800
    A highly modification of tberd5800scriptSample.RemoteControl5800"""
    def __init__(self, targetip, debug=False, timeout=30):
        """Initialization function:
        Inputs:
        targetip (str): The target IP address as a string i.e. \"192.168.200.2\"
        timeout (float): Timeout fuction: Does not appear to do anything
        """
        
        # Check IP format
        
        self.commonapps=commonapps
        self.currentport = 8000
        self.side = "BOTH"
        self.slic = "BASE"
        self.isConnected=False
        self.ipValid=False
        self.isSession=False
        self.curr=None
        #self.timeout=timeout
        self.debug=debug
        self.validports=[1, 2]
        m = re.match('(\d+)\.(\d+)\.(\d+)\.(\d+)', targetip.strip())
        if not m:
            writelog('Wrong IP format, please check and then continue')
            raise ValueError(f"IP address of {targetip} is invalid")
        
        try:
            # create an AF_INET, STREAM socket (TCP)
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #Line added: Set socket timeout (Was infinite before)
            self.soc.settimeout(timeout)
        except Exception as msg:
            writelog(f'Failed to create socket. Error: {msg}')
            return

        
        self.ip = targetip
        self.isConnected=False
        self.laserStatus=False
        self.ipValid=True
    
    def connect(self, verbose=False):
        """
        connect:
        Modified version of connect from tberd5800scriptSample with (verbose)
        and normal (quiet) modes.
        
        Connects T-BERD 5800 to remote mode and sets connected status in object
        Returns True on successful connection, False othersise"""
        shh=not verbose
        try:
            moduleParams = self.side + "," + self.slic + ",\"BERT\""
            #Open current port and send *REM command
            self.socketOpen(str(self.currentport))
            if self.debug:
                self.socketSend("*REM VISIBLE ON", shh)
            else:
                self.socketSend("*REM", shh)
            # Verify the module is on
            self.socketSend("MOD:FUNC:SEL? " + moduleParams, shh)
            resp = self.socketRead()
            if resp.strip() != "ON":
                writelog("The module is not enabled")
                return False
            # Get the module port number
            self.socketSend("MOD:FUNC:PORT? " + moduleParams, shh)
            modulePort = self.socketRead()
            if modulePort.strip() == "-1":
                writelog("Unable to obtain the module port number")
                return False
            self.socketClose()
            #2 - Get RC port number
            self.socketOpen(str(modulePort))
            self.socketSend("*REM", shh)
            # Verify the module is fully booted up and ready for RC connections
            self.socketSend(":SYST:FUNC:READY? " + moduleParams, shh)
            resp = self.socketRead()
            if resp != "1":
                writelog("The module is not ready ")
                return False
            # Query for the RC port number
            self.socketSend(":SYST:FUNC:PORT? " + moduleParams, shh)
            rcPort = self.socketRead()
            if rcPort.strip() == "-1":
                writelog("Unable to obtain the RC port number")
                return False
            self.socketClose()
            # Step 3: Connect to the RC port
            self.socketOpen(str(rcPort))
            writelog("Connection opened to RC port " + str(self.currentport))
            self.isConnected=True
            return True
        except Exception as msg:
            info = traceback.format_exc()
            writelog(info + 'Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
            return False
    
    def exit(self, timeout=30):
        """exit:
        Gracefully exits remote mode and re-enables GUI if not in visible/debug mode 
        Base Version for TB5800"""
        self.settimeout(timeout)
        self.sendscpi(":EXIT")
        if not self.debug:
            self.sendscpi("*GUI")# Must return to gui, returns to default app 
        self.socketClose()
    
"""
Any question about the script, please contact Brad Sicotte at 
email: bsicotte@teracomm.com
"""