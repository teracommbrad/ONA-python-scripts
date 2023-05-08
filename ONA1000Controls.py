"""ONA1000Controls.py
A controller library for the ONA1000 based on TBControllerCommon
"""
from TBControllerCommon import *
import traceback

#Default Parameters
defaultModuleName='TM400G-1' 
commonapps=[{"name":"100 Gig E Layer 2 Traffic Terminate", "appId":"TermEth100GL2Traffic"}, 
            {"name":"200 Gig E Layer 2 Traffic Terminate", "appId":"TermEth200GL2Traffic"}, 
            {"name":"400 Gig E Layer 2 Traffic Terminate", "appId":"TermEth400GL2Traffic"}, 
            {"name":"10 Gig E Layer 2 Traffic Terminate", "appId":"TermEth10GL2Traffic"},
            {"name":"25 Gig E Layer 2 Traffic Terminate", "appId":"TermEth25GL2Traffic"},
             {"name": "100 Gig E KP4 FEC Layer 2 Traffic Terminate", "appId":"TermEth100GL2TrafficKP4FEC"}]

ONA_PORTS=[1, 2]

class ONA1000Controls(Controller_base):
    """An object to control the ONA1000, 
    a subclass of TBControllerCommon.Controller_base 
    Also depends on other TBControllerCommon functions
    """
    def __init__(self, targetip, debug=False, timeout=30, moduleName=defaultModuleName):
        """__init__:
        Initializes an object of type ONA1000Controls
        Inputs:
        targetip (str) : The target ip address
        debug (Boolean) : Debug mode (Default false)
        timeout (int) : The socket timeout (default 30)
        moduleName (str) : the default module name, default is defaultModuleName value"""
        self.commonapps=commonapps
        self.currentport = 5025
        self.isConnected=False
        self.ipValid=False
        self.isSession=False
        self.curr=None
        self.moduleName=moduleName
        #self.timeout=timeout
        self.debug=debug
        self.validports=ONA_PORTS
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
    def connect(self, verbose=False, numtries=2):
        """
        connect:
        Modified version of connect from tberd5800scriptSample with (verbose)
        and normal (quiet) modes.
        
        Attempts (up to 2x) to connect to ONA-1000 to remote mode and sets connected status in object
        Inputs:
        verbose (boolean) : Verbose mode when True (default False)
        numtries (int) : Number of total attempts to connect (default 2)
        Returns True on successful connection, False othersise"""
        shh=not verbose
        try:
            respflag=False
            self.socketOpen(str(self.currentport))
            time.sleep(1)
            if self.debug:
                self.socketSend("*REM VISIBLE ON", shh)
            else:
                self.socketSend("*REM", shh)
            for idx in range(numtries):
                time.sleep(1)
            #Open current port and send *REM command
                # Verify the module is on and get module port number
                self.socketSend(":PRTM:LIST?")
                time.sleep(1)
                resp = self.socketRead()
                print(resp)
                self.socketClose()
                if resp.strip()!='':
                    print("Got Successful Response")
                    respflag=True
                    break
                else:
                    time.sleep(2)
            if not respflag:
                return False
            
            resplines=resp.split('\n')
            respjson=[]
            #Manually parse responses from :PRTM:LIST? to get desired port
            for line in resplines:
                currjson={}
                splitlines=line.split(',')
                for splitline in splitlines:
                    secondsplit=[x.strip() for x in splitline.split(':')]
                    currjson[secondsplit[0]]=secondsplit[1]
                respjson.append(currjson)
            modFoundFlag=True
            for line in respjson:
                if self.moduleName in line.keys():
                    modulePort=line[self.moduleName]
                    modFoundFlag=True
                    break
            if not modFoundFlag:
                raise RuntimeError('Requested Module could not be found')
          
           
            # Connect to the RC port
            self.socketOpen(str(modulePort))
            writelog("Connection opened to RC port " + str(self.currentport))
            self.isConnected=True
            return True
        except Exception as msg:
            info = traceback.format_exc()
            writelog(info + 'Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
            return False
    def connectToApp(self, app, args=None, timeout=None, verbose=False, multiconnect=False):
        """Special Version of connectToApp with timeout required of at least 90 seconds
        INPUTS:
        app (string) : The name of the application to launch, or alternatively the application to launch with arguments
        args (string) : The arguments to append to app
        timeout (float) : The timeout for launching application only; timeout will be reset after this command ends
        verbose (boolean) : Verbose Mode (default False)
        multiconnect (boolean) : Allow connection to multiple apps; will close other apps if False
        (Default False)
        Returns:
        True if completed successfully
        False otherwise
        """
        if timeout is None or timeout<90:
            sto=90
        else:
            sto=timeout
        super().connectToApp(app, args, sto, verbose, multiconnect)
    def exit(self, timeout=30):
        """exit:
        Gracefully exits remote mode and re-enables GUI 
        Version for ONA-1000"""
        self.settimeout(timeout)
        self.sendscpi(":EXIT")
        self.sendscpi("*GUI")# Must return to gui, returns to default app 
        self.socketClose()

"""
Any question about the script, please contact Brad Sicotte at 
email: bsicotte@teracomm.com
"""