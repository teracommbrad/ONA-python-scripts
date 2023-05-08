"""TBControllerCommon.py
Defines common functions and variables for TB5800/ONA series remoting
Note that class Controller is abstract and should not be used on its own.
"""

#HELP String
helpstr="""Commands Supported:

                APP : Brings up apps and starts an app chosen by user, closing others
                MULTIAPP : Brings up apps and starts an app chosen by user, not closing others
                START appname : Starts appname and closes all other apps.  
                    appname may be multiple words, including arguments (60 second default timeout)
                    Example: START TermEth100GL2Traffic 1
                MULTISTART appname : Starts appname, not closing any other apps
                CURR : Gets Current Running apps, with an arrow to the current running app            
                PEEK page addr : Peek address with given page
                    Example : PEEK 0 0x56    
                PEEK addr : Peek address
                    Example : PEEK 0x56
                POKE page addr value : poke page, address with value
                    Example : POKE 0 0x56 0x01
                POKE addr value : poke address with value
                    Example : POKE 0x56 0x01
                DELAY value : Delay value seconds
                SCPI command : send scpi with given command; command may be multiple words
                    Example: SCPI :SYST:APPL:CAPP? 
                HELP : Provides help
                EXIT or QUIT: Exit program
                CLOSEAPP : Brings up prompt to exit app
                CLOSEAPP appId : Exits app with given appId
                ACTIVE : Select an active app based on prompt

                Note: Closing app can take 5-10 seconds AFTER command is sent and received
                Command names are not case-sensitive
                Arguments/values are case sensitive
"""
#HELP string for auto mode
autohelpstr="""Auto Mode:
                Commands Supported:

                START appname : Starts appname and closes all other apps.  
                    appname may be multiple words, including arguments (60 second default timeout)
                    Example: START TermEth100GL2Traffic 1
                MULTISTART appname : Starts appname, not closing any other apps
                CURR : Gets Current Running apps, with an arrow to the current running app    
                PEEK page addr : Peek address with given page
                    Example : PEEK 0 0x56                
                PEEK addr : Peek address
                    Example : PEEK 0x56
                POKE page addr value : poke page, address with value
                    Example : POKE 0 0x56 0x01
                POKE addr value : poke address with value
                    Example : POKE 0x56 0x01
                DELAY value : Delay value seconds
                SCPI command : send scpi with given command; command may be multiple words
                    Example: SCPI :SYST:APPL:CAPP? 
                EXIT or QUIT: Exit program
                CLOSEAPP appId : Exits app with given appId
                ACTIVE : Select an active app based on prompt

                Note: Closing app can take 5-10 seconds AFTER command is sent and received
                Command names are not case-sensitive
                Arguments/values are case sensitive
"""
#Set global variables
DEFAULTDELAY=1.3
import time
import re
import socket
import datetime
def getInt(str):
    """Gets an integer in either hex (with 0x),  binary (0b), or decimal (no prefix) from a string
    Inputs: str (str) : The string to be converted
    Returns the integer conversion of str
    Throws Exception if str cannot be converted into int"""
    if "0X" in str or "0x" in str:
        #Hex
        return int(str, 16)
    elif "0B" in str or '0b' in str:
        #Binary
        return int(str, 2)
    #Assume decimal
    return int(str)
def printHelp(auto=False):
    """printHelp:
    Prints help string to console"""
    if not auto:
        print(helpstr)
    else:
        print(autohelpstr)

def parseToApplication(apstr):
    """parseToApplication:
    Parses an application name/id to Application object
    inputs: apstr (str): The application name/id input
    returns: an Application object conrresponding to apstr"""
    if "_" in apstr and " " not in apstr:
        return Application(appId=apstr)
    else:
        return Application(appstr=apstr)

class Application:
    """class Application:
    A simple class to hold the name and port of an application, and/or
    parse an application from its returned name from :SYST:APPL:CAPP"""
    def __init__(self, appstr=None, appname=None, port=None, appId=None):
        """
        Initializes an objecr of class Application
        INPUTS:
        
        appname (str) : the name of the application with port attached as last
        port (str) : The port of the application
        appId (str) : The id of the application in format abc_xyz
        Note that either appname or appstr must be provided"""
        self.appId=None
        if appstr is not None:
            splitname=appstr.split()
            if len(splitname)==1:
                self.appname=splitname[0]
            elif len(splitname)>1:
                self.appname=''.join(splitname[0:-1])
                self.port=splitname[-1]
            else:
                raise ValueError("Invalid appname provided")
        elif appId is not None:
            self.appId=appId
            appsplit=appId.split("_")
            #Split application to x*****x_y***y format
            if len(appsplit)==1:
                self.appname=appsplit[0]
            else:
                self.appname=''.join(appsplit[0:-1])
                self.port=str(appsplit[-1][-1])
        elif appname is not None:
            self.appname=appname
            self.port=str(port) #auto convert port to string if necessary
        else:
            raise ValueError("Either appname and port must both be not none, or appstr must be not none")
    def __str__(self):
        """__str__:
        Returns a string representation of the Application object"""
        if self.appId is not None:
            return f"Instance {self.appId} of {self.appname}, port {self.port}"
        else:
            return f"Instance of {self.appname}, port {self.port}"
    def getappname(self):
        """getappname:
        Returns appname"""
        return self.appname
    def getPort(self):
        """"getPort:
        returns port"""
        return self.port
    def getAppId(self):
        """getAppId:
        returns appId"""
        return self.appId
    def __eq__(self, obj):
        """__eq__(self, obj): returns whether self is equal to obj
        obj (Application) : an object of type Application
        Inputs:
        obj (Application) : The object to compare to.
        Throws TypeError if obj is not an Application type"""
        if obj is None:
            return  False
        elif not isinstance(obj, Application):
            raise TypeError("Given comarable object is not of type Application")
        if self.appId is not None and obj.appId is not None:
            return self.appId==obj.appId
        return self.appname==obj.appname and self.port==obj.port


    
def writelog(information):
    """writelog: prints the date and time formatted, and the given message to the console
    Inputs:
    Information (string or other type that can be converted to string) : The information to write"""
    now_time = datetime.datetime.now()
    strNowTime = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    print(strNowTime + " >" + str(information))
        

def getPort(validports):
    """Retrieve port number from input"""
    return input(f"Enter Port Number (Valid Ports: {sorted(validports)}):\n")


class Controller_base():
    """class Controller_base
    An Abstract class for common/shared functions for TB5800/ONA1000 remote operations
    Note that first two methods __init__ and connect are abstract and must be implemented."""
    def __init__(self, targetip, debug=False, timeout=30):
        #Blank function, must be implemented for each type of instrument
        pass
    def connect(self, verbose=False):
        #Blank function, must be implemented for each type of instrument
        pass
    def exit(self):
        #Blank function, must be implemented for each type of instrument
        pass
    #Common interface methods
    def __exit__(self):
        """Exit Destructor: calls self.exit()"""
        #self.sendscpi(":SESS:END")
        self.exit()
   
    def setRemoteOn(self):
        """setRemoteOn:
        Sets the TB5800 into remote mode
        Please delay at least 1 second after this command before talking to TB5800
        Returns True if executed successfully, False on exception"""
        try:
            if self.debug:
                self.socketSend("*REM VISIBLE ON")
            else:
                self.socketSend("*REM")
            return True
        except Exception as e:
            return False
    def socketOpen(self, sport=''):
        """socketOpen:
        Opens the a socket to the self.ip, given port; sets self.currentport
        Returns True if executed successfully, False on exception"""
        if str(sport).strip() == "":
            writelog("socketSend: 'port' parameter is required")
            return False
        try:
            self.currentport = int(sport)
        except Exception as e:
            writelog("sport must be an integer or string convertible to integer")
        try:
            if self.soc is not None:
                timeout=self.soc.gettimeout()
        except Exception as e:
            timeout=None
        else:
            try:
                self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.settimeout(timeout)
                self.soc.connect((self.ip, self.currentport))
                return True
            except Exception as msg:
                writelog('Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
                return False
                
    def socketSend(self, message, shh=0):
        """socketSend:
        send a message to the given socket, append a \n if there isn't one"""
        message = message.strip()
        if shh == 0:
            writelog(message)
        try:
            # Set the whole string
            self.soc.sendall((message+"\n").encode("utf-8"))
            return message
        except Exception:
            # send failed
            writelog('message Send failed ==> :' + message)
            return None
    def inputAppStr(self, inclCurr=True):
        """Prompt user with common applications and input application from number selected
        self (TB5800Controls): The machine to control
        inclcurr (bool default True) : Include current application at end of indexing

        Returns applicaction ID string if found, None otherwise"""
        #Error check self

        applistlen=self.printAppList(inclCurr=inclCurr)
        appbasestr=input(f"Enter app choice number\n")
        try:
            appbaseid=int(appbasestr)
            if appbaseid==0:
                return None
            if appbaseid>=1 and appbaseid<len(self.commonapps)+1:
                #Valid input
                portnum=getPort(self.validports)
                appstr=self.commonapps[appbaseid-1]["appId"]+' '+portnum            
                return appstr
            elif appbaseid==len(self.commonapps)+1 and inclCurr and applistlen>len(self.commonapps):
                #Valid input due to inclCurr, selected "current application"
                #Print list of current applications and then select
                #and valid current app open
                currapps=self.getCurrentApplications()
                if len(currapps)==0:
                    print("No current apps open")
                    return None
                for idx in range(len(currapps)):
                    print(f'[{idx+1}] {currapps[idx]}')
                print(f'[0] Do Not Open App')
                currappidxstr=input("Enter index of desired app:\n")
                try:
                    #Try to cast index to int
                    currappidx=int(currappidxstr)-1
                except Exception as e:
                    print("Improper app index. No app selected.")
                    return None
                if currappidx==-1:
                    #0 input, do nothing
                    print("Selected no application.")
                    return None
                elif currappidx<0 or currappidx>=len(currapps):
                    #Bad app index
                    print("Improper app index. No app selected")
                    return None
                else:
                    #Select good app
                    capp=currapps[currappidx]
                #Return appID
                return capp.getAppId()
            elif appbaseid==len(self.commonapps)+2 or appbaseid==-1:
                #Do Not Open.
                print("Do Not Open App Selected")
                return None
            else:
                #Bad index
                print("Improper Application Selection Index. No app selected")
                return None
        except Exception as e:
            print("Application Select Failed")
            return None
        return None
    def printAppList(self, inclCurr=True):
        """Print all common applications
        INPUTS:
        self : The TB5800Controls object for the machine (necessary for settng current apps)
        
        Returns the length of app list"""
        #Error check type of self
        if not isinstance(self, Controller_base):
            return False
        if inclCurr:
            currapps=self.getCurrentApplications()
        print("App Choices:")
        for idx in range(len(self.commonapps)):
            print(f'[{idx+1}] {self.commonapps[idx]["name"]}')
        if inclCurr:
            if len(currapps)>0:
                print(f'[{len(self.commonapps)+1}] Current Open app')
            print(f'[0] Do Not Open App')
            return len(self.commonapps)+1
        else:
            print(f'[0] Do Not Open App')
            return len(self.commonapps)
    
    def canRead(self):
        """"canRead:
        Attempts to read and return a socket message, returns '' otherwise"""
        result = ''
        result += self.soc.recv(8192).decode('utf-8')
        return result
    
    def socketRead(self):
        """
        socketRead:
        read a response from the given socket, remove the \n if there is one
        parameters:realtimeout : set timeout
        shh : if set, don't echo the command we're sending
        Returns message read from the socket
        """
        msg = self.soc.recv(8192).decode("utf-8")
        msg = msg.strip()
        return msg

    def socketClose(self):
        """socketClose:
        Close the object's socket
        returns True if close is successful"""
        try:
            self.soc.close()
            writelog("Socket connection closed")
            return True
        except Exception as e:
            print(f'Exception: {e}')
            return False

    def settimeout(self, timeout):
        """setTimeout:
        Sets the socket timeout
        inputs:
        timeout (int): The new socket timeout"""
        if self.soc.gettimeout() != timeout:
            self.soc.settimeout(timeout)

    def gettimeout(self):
        """getTimeout:
        gets the current socket timeout and returns it"""
        return self.soc.gettimeout()
    
    def switchToApp(self, app, verbose=False, launch=False):
        """Subroutine to switch to app
        Returns true if no exception occurs"""
        if isinstance(app, Application):
            try:
                if self.isSession:
                    self.sendscpi(":SESS:END " + app.getAppId().strip(), verbose)
                self.sendscpi(":SYST:APPL:SEL " + app.getAppId().strip(), verbose)
                self.sendscpi(":SESS:CREATE", verbose)
                self.sendscpi(":SESS:START", verbose)
                self.curr=app
                if launch:
                    self.sendscpi(":INIT")
                return True
            except Exception as e:
                print(f'Exception: {e}')
                return False
        return False

    def connectToApp(self, app, args=None, timeout=None, verbose=False, multiconnect=False):
        """High level method to connect to / launch application
        Checks for existing app if app has a single port as a parameter or no parameter.

        INPUTS:
        app (string) : The name of the application to launch, or alternatively the application to launch with arguments
        args (string) : The arguments to append to app
        timeout (float) : The timeout for launching application only; timeout will be reset after this command ends
        verbose (boolean) : Verbose Mode (default False)
        multiconnect (boolean) : Allow connection to multiple apps; will close other apps if False
        (Default False)
        Returns:
        True if completed successfully
        False otherwise"""
        if app is None:
            print("App must be defined.  Not starting app")
            return False
        #Connect to remote mode, startin new session if necessary
        connflag=True
        writelog("Connecting to Application")
        if not self.isConnected:
            connstatus=self.connect()
            if not connstatus:
                return False
            connflag=False
        
        #Remember timeout and make sure timeout>=60s.
        oldtimeout=self.gettimeout()
        if timeout is not None and timeout>60:
             self.soc.settimeout(timeout)
        if timeout is None or timeout<60:
            ssto=self.gettimeout()
            if ssto is None or ssto < 60:
                self.settimeout(60) #Set at least 60s timeout for connecting to appl
        runningapp=None
        if connflag:
            #If not a new connection.
            currapps=self.getCurrentApplications()
            appfound=False
            if isinstance(app, Application):
                apb=app
            else:
                apb=parseToApplication(app)
            for x in currapps:
                if x==apb:
                    runningapp=x
                    appfound=True
                    break
            if not appfound:
                if args is not None:
                    appdesc=Application(appname=app, port=args)
                else:
                    appdesc=Application(appstr=app)
                if currapps is not None and len(currapps)>0:
                    runningApp=None
                    for capp in currapps:
                        #Use full for loop as we need to get application from currapps
                        if capp==appdesc:
                            runningapp=capp
        if runningapp is not None:
            if not multiconnect:
                #Close others
                for appx in currapps:
                    if appx!=runningapp:
                        closestatus=self.closeApplication(appx.getAppId())
                        if not closestatus:
                            return False
            if not appfound:
                appport=apb.getPort()
                if appport in self.getPortsInUse():
                    print(f"Port {appport} already in use.\nCannot start new app on existing active port")
                    return False
            print(f"Application already open; switching to {runningapp}")
            switchstatus=self.switchToApp(runningapp, verbose, launch=True)
            if not switchstatus:
                return False
            self.isSession=True
            self.settimeout(oldtimeout)
        elif multiconnect:
            appport=apb.getPort()
            portsInUse=self.getPortsInUse()
            if appport in portsInUse:
                print(f"Port {appport} already in use.\nCannot start new app on existing active port")
                return False
            try:
                #Try to launch application
                retval = self.launchApplication(app, args)
            except Exception as e:
                writelog(f"Application Launch Failed: Exception: {e}")
                retval = False
            finally:
                #Resume old timeout and return
                self.settimeout(oldtimeout)
                return retval
        else:
            try:
                self.sendscpi("*RST")
                retval = self.launchApplication(app, args)
            except Exception as e:
                writelog(e)
                print(f"Application Launch Failed: Exception: {e}")
                return False
            finally:
                #Resume old timeout and return
                self.settimeout(oldtimeout)
                return retval
    def exitApplication(self, appIdToExit, nextAppId=None):
        """exitApplication
        High Level Function to exit application on the TB5800 with appID appIdToExit
        Checks if appIdToExit is valid
        INPUTS:
        appIdToExit (str) : The appID of the app to exit; must be a running app to exit
        nextAppId (str) : the appID of the next app to select; must be a running app to switch to
        Returns True if completed successfully"""
        try:
            currapps=self.getCurrentApplications()
            exitapp=Application(appIdToExit)
            if exitapp in currapps:
                self.sendscpi(":SYST:APPL:SEL "+appIdToExit)
                self.sendscpi(":EXIT")
                self.curr = None
                exitflag=True
            else:
                return False
            if nextAppId is not None and nextAppId in currapps:
                self.sendscpi(":SYST:APPL:SEL "+nextAppId)
                self.curr=Application(appId=nextAppId)
            return True
        except Exception as e:
            print(f'Exception: {e}')
            return False
    def sendscpi(self, cmd,  verbose=False, cmdend=""):
        """
        Higher-level routine for communicating with the remote control port
        Query commands: returns the value returned by the command
        Non-query commands: follows up with :SYSTem:ERRor? query, returns 1 if all is well, 0 if there is an error
        Returns None if not successful
        parameters:
        cmd : scpi command (including arguments)
        cmdend : end signal
        verbose : if set, echo the command we're sending, otherwise do not
        Variant of the sendscpi from tberd5800scriptSample.py
        Returns the result of SCPI command or None if there is no result
        May throw exception
        """
        shh=not verbose
        Info = ""
        if cmdend == "":
            try:
                sendval=self.socketSend(cmd, shh=shh)
            except TimeoutError as te:
                writelog("Socket timed out.")
                return None
            if sendval is None:
                writelog("Socket send error.")
                return None
            Info = Info + sendval

            if re.search(r'\?', cmd):
                try:
                    resp = self.canRead()
                    if resp != 0:
                        Info = Info + " " + resp
                        if not shh:
                            writelog(Info)
                        return resp.strip()
                except TimeoutError as te:
                    writelog("Socket timed out")
                    return None
                else:
                    try:
                        Info = Info + self.socketSend(":SYST:ERR?", shh=shh)
                        resp = self.canRead()
                        if resp != 0:
                            if not shh:
                                writelog(resp)
                            Info = Info + resp
                            return Info
                        else:
                            resp = self.socketRead()
                            Info = Info + resp
                            return Info
                    except TimeoutError as te:
                        writelog("SCPI command timed out")
                        return None
            else:
                try:
                    Info = Info + self.socketSend(":SYST:ERR?", shh=shh)
                    resp = self.socketRead()
                    Info = Info + resp
                    if resp == '0, "No error"':
                        return Info
                    else:
                        return Info
                except TimeoutError as te:
                    writelog("SCPI command timed out")
                    return None
                
    def getConnected(self):
        """Return whether device is connected"""
        return self.isConnected
    def selectApp(self, app, verbose=False, launch=False):
        """selectApp:
        Selects current application from already running application
        Inputs:
        app (Application) : Application object of the current app
        verbose (bool) : Verbose mode
        launch (Boolean) : Sends ":INIT" after the session commands to launch session"""
        if isinstance(app, Application):
            apidstr=app.getAppId()
            if apidstr is None:
                print("Invalid application object called")
                return False
        else:
            apidstr=app
        try:
            if self.isSession:
                self.sendscpi(":SESS:END")
            self.sendscpi(":SYST:APPL:SEL " + apidstr.strip(), verbose)
            self.sendscpi(":SESS:CREATE")
            self.sendscpi(":SESS:START")
            self.isSession=True
            if launch:
                self.sendscpi(":INIT")
            if verbose:
                writelog("Application launched successfully")
            self.curr=Application(appId=apidstr.strip())
            return True
        except Exception as e:
            print(f'Exception: {e}')
            return False
    
    def launchApplication(self, application, args=None, verbose=False):
        """launchApplication - Low Level method to launch an application with given args
        INPUTS:
        application (str) - The name of the application
        args (int or list(int)) - The arguments; default None
        verbose (Boolean) - Verbose mode on or off
        Throws runtime error if application is not found (similar to file operations)
        Returns True if successful"""
        apporig=application
        if args is not None:
            for x in args:
                apporig+=' '+x
        appstr=":SYST:APPL:LAUN "+apporig
        writelog(f"Launching appication {apporig}")
        apstval=self.sendscpi(appstr, verbose=verbose)
        #if apstval == 0:
            #return
        if ":SYST:ERR?0," in apstval:
            #No error

            appId = self.sendscpi(":SYST:APPL:LAUN?", verbose)
            self.selectApp(Application(appId=appId.strip()), launch=True)
            if self.isSession:
                self.sendscpi(":SESS:END", verbose)
            self.sendscpi(":SYST:APPL:SEL " + appId.strip(), verbose)
            self.sendscpi(":SESS:CREATE", verbose)
            self.sendscpi(":SESS:START", verbose)
            self.isSession=True
        # Need to send :INIT here to start the test. Applications begin in the
        # "Stopped" state in (GUI-disabled) RC mode.
            self.sendscpi(":INIT")
            writelog("Application launched successfully")
            self.curr=Application(appId=appId.strip())
            return True
        else:
            #Raise Exception
            raise RuntimeError(f"Application was not found: {appstr} returned {apstval}")
        
    def getPortsInUse(self):
        """getPortsInUse:
        Gets the current ports in use
        Returns:
        A list of the current ports in use"""
        currapps=self.getCurrentApplications()
        currports=[]
        for app in currapps:
            if isinstance(app, Application):
                try:
                    currports.append(app.getPort())
                except Exception as e:
                    pass
        return currports
    def closeApplication(self, appid):
        """Closes an application
        
        Inputs:
        appid (str): The appid to close
        Returns True if successful, False if exception"""
        currapps=self.getCurrentApplications()
        appToClose=Application(appId=appid.strip())
        if appToClose in currapps:
            try:
                self.sendscpi(":SYST:APPL:SEL "+appid)
                self.curr=Application(appId=appid)
                self.sendscpi(":EXIT")
                self.curr=None
                currapps=self.getCurrentApplications()
                return True
            except Exception as e:
                print(f"Exit command failed : {e}")
                return False
            

        else:
            print("App to close not in current applications; not closing app")
            return False

        
    def peek(self, register, page=0x00, delay=DEFAULTDELAY, verbose=False, returnStatus=False):
        """
        peek
        Peeks at one of the Module's I2C registers
        
        Inputs:
        register (int) : The register number to look into from 0x00 to 0xff
        page (int) : The page number from 0x00 to 0xff
        delay (int) : The delay value in seconds; Too short of a delay can result in wrong info.  
                      Should be tested using a known value (Default 1)
        verbose (boolean) : verbose mode on or off (Default False)
        returnStatus (boolean) : Returns dict of {"VALUE":value, "SUCCESS":success} if True
        Otherwise returns value
        Returns None on exception"""
        if page>0xff or page<0:
             raise ValueError(f"Page value of {hex(page)} is out of range")
        if register>0xff or register<0:
             raise ValueError(f"Register value of {hex(register)} is out of range")
        if verbose:
            writelog(f"Sending PEEK command to page {hex(page)} register {hex(register)}")
        try:
            self.sendscpi(f":SENSE:EXPERT:I2C:PEEK:PAGESEL {page}", verbose=verbose)
            self.sendscpi(f":SENSE:EXPERT:I2C:PEEK:REGADDR {register}", verbose=verbose)
            self.sendscpi(":SENSE:EXPERT:I2C:PEEK:TRIGGER", verbose=verbose)
            time.sleep(delay)
            pkv=self.sendscpi(":SENSE:DATA? :SENSE:EXPERT:I2C:PEEK:REGDATA", verbose=verbose)
            peekval= int(pkv)
            writelog(f"PEEK value : {hex(peekval)}")
            if not returnStatus:
                return peekval
            else:
                return {"VALUE": peekval, "SUCCESS":int(self.sendscpi(":SENSE:DATA? :SENSE:EXPERT:I2C:PEEK:SUCCESS", verbose=verbose))}
        except Exception as e:
            print(f'Exception {e}')
            return None

    def poke(self, register, value, page=0x00, delay=DEFAULTDELAY, verbose=False):
        """
        poke
        Pokes one of the Module's I2C registers with a value
        
        Inputs:
        register (int) : The register number to look into from 0x00 to 0xff
        value (int): The value to poke the register with.
        page (int) : The page number from 0x00 to 0xff
        delay (int) : The delay value in seconds; Too short of a delay can result in wrong info.  
                      Should be tested using a known value (Default 1.3)
                      Delay of 0 means send poke and don't wait for response.

        verbose (boolean) : verbose mode on or off (Default False)
        Return poke success if successful, None if not"""

        if page>0xff or page<0:
            raise ValueError(f"Page value of {hex(page)} is out of range (0x00 to 0xff)")
        if register>0xff or register<0:
            raise ValueError(f"Register value of {hex(register)} is out of range (0x00 to 0xff)")
        if value>0xff or value<0:
            raise ValueError(f"Poke value of {hex(value)} is out of range (0x00 to 0xff)")
        if verbose:
            writelog(f"sending POKE to page {hex(page)} register {hex(register)} with value {hex(value)}")
        try:
            self.sendscpi(f":SENSE:EXPERT:I2C:POKE:PAGESEL {page}", verbose=verbose)
            self.sendscpi(f":SENSE:EXPERT:I2C:POKE:REGADDR {register}", verbose=verbose)
            self.sendscpi(f":SENSE:EXPERT:I2C:POKE:REGDATA {value}")
            self.sendscpi(":SENSE:EXPERT:I2C:POKE:TRIGGER", verbose=verbose)
            if delay>0:
                time.sleep(delay)
                return int(self.sendscpi(":SENSE:DATA? :SENSE:EXPERT:I2C:POKE:SUCCESS", verbose=verbose))
            return None
        except Exception as e:
            print(f'Exception {e}')
            return None
    
    def runCommand(self, cmdval, auto=False):
        """runCommand : Runs a command and returns either True False or "EXIT" 
        inputs:
        self (TBERD5800Controls) : The instrument to run command on
        cmdval (str) : The command string in the format of a command in helpstr
        Returns "EXIT" for exit command
        returns True or Command value as string if command is success
        returns False if command if failure
        In most cases, we are only looking for "EXIT" returned."""
        stripcmd=cmdval.strip()
        #Split command into 2 to get keyword and remainder
        splitcmd=stripcmd.split(maxsplit=1)
        if(len(splitcmd)==0):
            #No command
            print("A command must be entered.")
            return False
        elif splitcmd[0].upper()=="HELP":
            #HELP: display help
            printHelp(auto=auto)
            return True
        elif splitcmd[0].upper()=="EXIT" or splitcmd[0].upper()=="QUIT": 
            #EXIT: set notExit to soft exit loop
            writelog("Exiting Application");
            self.exit()
            return "EXIT"
        elif splitcmd[0].upper()=="CURR":
            #CURR: Display cureent apps
            try:
                currapps=self.getCurrentApplications()
                runningapp=self.getActiveApp()
                for idx in range(len(currapps)):
                    if currapps[idx]==runningapp:
                        print(f'>[{idx+1}] {currapps[idx]}')
                                
                    else:
                        print(f'[{idx+1}] {currapps[idx]}')     
                return True

            except Exception as e:
                print(f"Exception getting current apps : {e}")    
                return False
        elif (splitcmd[0].upper()=="APP" or splitcmd[0].upper()=="MULTIAPP"):
            #APP/MULTIAPP : Brings up app selection screen to choose and start app
            #APP closes all other apps.
            #MULTIAPP leaves other apps open.  Be aware that opening multiple apps can result in errors if port is already in use.
            multiflag=False
            if auto:
                print(f"{splitcmd[0].upper()} command does not work in auto/file mode.")
                return False
            if splitcmd[0].upper()=="MULTIAPP":
                #MULTIAPP : Open app without closing other apps
                multiflag=True
            if len(splitcmd)<=1:
                #open default app menu
                selectedapp=self.inputAppStr()
                if selectedapp is not None:
                    if len(selectedapp.split())>1:
                        return self.connectToApp(app=selectedapp, multiconnect=multiflag)
                    else:
                        selappport=selectedapp[-1]
                        selappname=selectedapp.split("_")[0]
                        return self.connectToApp(app=selappname+' '+selappport, multiconnect=multiflag)
            else:
                print("APP command must have 0 arguments.")
                return False
        elif splitcmd[0].upper()=="START" or splitcmd[0].upper()=="MULTISTART":
            #START/MULTISTART command: Starts an app with given name
            #START closes other apps while MULTISTART does not
            multiflag=False
            if splitcmd[0].upper()=="MULTISTART":
                multiflag=True
            if len(splitcmd) >= 2:
                #Good command
                try:
                    appname=' '.join(splitcmd[1:])
                    #Attempt to start the application with given app
                    print(f"Opening application {appname}")
                    #currapps=self.getCurrentApplications()
                    return self.connectToApp(app=appname, multiconnect=multiflag)
                except Exception as e:
                    #Bad start
                    print("Could not start the application.")
                    return False
            else:
                #Too few inputs
                print(f"START Command has too few ({len(splitcmd)-1}) arguments; must have 1 or more arguments")
                return False
        elif splitcmd[0].upper()=="PEEK":

            #PEEK command
            if len(splitcmd)<=1:
                #Too few arguments
                print("PEEK command must have one or two arguments attached")
                return False
            else:
                resplit=splitcmd[1].split()
                if len(resplit)==1:
                    peekarg=resplit[0].upper()
                #Get the 1st word of splitcmd[1] or 2nd word of command value, ignores beyond
                    try:
                        return self.peek(getInt(peekarg))
                        
                    except Exception as e:
                        print(f"PEEK Command failed: {e}")
                        return False
                elif len(resplit)==2:
                    peekpage=resplit[0].strip()
                    peekarg=resplit[1].strip()
                #Get the 1st word of splitcmd[1] or 2nd word of command value, ignores beyond
                    try:
                        return self.peek(getInt(peekarg), page=getInt(peekpage))
                    except Exception as e:
                        print(f"PEEK Command failed: {e}")
                        return False
                else:
                    print("PEEK command must have one or two arguments")
                    return False

        elif splitcmd[0].upper()=="POKE":
            #POKE command
            if len(splitcmd)<=1:
                #Too few inputs
                print("POKE command must have two arguments attached")
                return False
            else:
                #Split poke arguments
                pokeargs=splitcmd[1].split()
                if len(pokeargs)<=1:
                    #Too few arguments
                    print("POKE command must have two arguments attached")
                    return False
                elif len(pokeargs)==2:
                    #Poke has right amount of inputs; run poke command using first 2 arguments
                    pokeaddr=getInt(pokeargs[0])
                    pokeval=getInt(pokeargs[1])
                    try:
                        return self.poke(pokeaddr, pokeval)
                    except Exception as e:
                        print(f"Poke retured exception {e}")
                        return False
                elif len(pokeargs)==3:
                    pokepage=getInt(pokeargs[0])
                    pokeaddr=getInt(pokeargs[1])
                    pokeval=getInt(pokeargs[2])
                    try:
                        return self.poke(page=pokepage, register=pokeaddr, value=pokeval)
                    except Exception as e:
                        print(f"Poke retured exception {e}")
                        return False
        elif splitcmd[0].upper()=="DELAY":
            #DELAY command
            if len(splitcmd)<=1:
                #Too few arguments
                print("DELAY command must have one argument")
                return False
            else:
                #Run delay command
                print(f'Delaying {float(splitcmd[1].split()[0])} seconds')
                time.sleep(float(splitcmd[1].split()[0]))
                return True
        elif splitcmd[0].upper()=="SCPI":
            #SCPI command
            if len(splitcmd)<=1:
                #Too few arguments
                print("SCPI command must have one argument")
                return False
            else:
                #Run verbose send scpi command
                try:
                    scpival=self.sendscpi(splitcmd[1], verbose=True)
                    print(scpival)
                    return scpival
                except Exception as e:
                    #Command Failed/Bad command
                    print(f"SCPI command failed : {e}")
                    return False
        elif splitcmd[0].upper()=="CLOSEAPP":
            #Close Application based on prompt/app
            if len(splitcmd)>1:
                #apppId argument given; Close application based on selected appId
                appstr=splitcmd[1]
                retstatus = self.closeApplication(appstr)
                currapps=self.getCurrentApplications()
                print("Select new active application")
                for idx in range(len(currapps)):
                    print(f'[{idx+1}] {currapps[idx]}')
                print('[0] No Application')
                appidstr=input("Enter application index:\n")
                try:
                    appidx=int(appidstr)-1
                except Exception as e:
                    #Cannot convert appidstr to int
                    print("Invalid App index")
                    return False
                if appidx in range(len(currapps)):
                #Attempt to close
                    try:
                        apid=currapps[appidx].getAppId()
                        self.selectApp(apid)
                        return True
                    except Exception as e:
                        print(f"Close app command did not complete successfully: {e}")
                        return False
                elif appidx==-1:
                    #"No Application" seleected
                    print("No app opened")
                    return True
            elif not auto:
                #appId not given and not automatic; Close application based on prompt; list all apps
                currapps=self.getCurrentApplications()
                for idx in range(len(currapps)):
                    print(f'[{idx+1}] {currapps[idx]}')
                print('[0] No Application')
                appidstr=input("Enter application index:\n")
                try:
                    appidx=int(appidstr)-1
                except Exception as e:
                    #Cannot convert appidstr to int
                    print("Invalid App index")
                    return False
                if appidx in range(len(currapps)):
                    #Attempt to close
                    try:
                        apid=currapps[appidx].getAppId()
                        self.closeApplication(apid)
                        print("Select new active application")
                        currapps=self.getCurrentApplications()
                        for idx in range(len(currapps)):
                            print(f'[{idx+1}] {currapps[idx]}')
                        print('[0] No Application')
                        appidstr=input("Enter application index:\n")
                        try:
                            appidx=int(appidstr)-1
                        except Exception as e:
                            #Cannot convert appidstr to int
                            print("Invalid App index")
                            return False
                        if appidx in range(len(currapps)):
                        #Attempt to close
                            try:
                                apid=currapps[appidx].getAppId()
                                self.selectApp(apid)
                                return True
                            except Exception as e:
                                print(f"Close app command did not complete successfully: {e}")
                                return False
                        elif appidx==-1:
                            #"No Application" seleected
                            print("No app opened")
                            return True
                    except Exception as e:
                        print(f"Close app command did not complete successfully: {e}")
                        return False
                elif appidx==-1:
                    #"No Application" seleected
                    print("No app closed")
                    return True
                else:
                    #Bad application index
                    print("Application index out of range")
                    return False
            else:
                print("CLOSEAPP must have 1 argument in auto mode")
                return False
        elif splitcmd[0].upper()=="ACTIVE":
            if auto:
                print("ACTIVE command does not work in automatic/file parsing mode")
                return False
            currapps=self.getCurrentApplications()
            if len(currapps)==0:
                print("No current apps open")
                return False
            for idx in range(len(currapps)):
                print(f'[{idx+1}] {currapps[idx]}')
            print(f'[0] Do Not Open App')
            currappidxstr=input("Enter index of desired app:\n")
            try:
                currappidx=int(currappidxstr)-1
                if currappidx>=0 and currappidx<len(currapps):
                    self.selectApp(currapps[currappidx])
                elif currappidx==-1:
                    print("No app selected")
                else:
                    print("Invalid app index selection")
            except Exception as e:
                print(f"Exception finding active apps : {e}")
        elif splitcmd[0].upper()=="GETACTIVE":
            sga=self.getActiveApp()
            print(f"Active App: {sga}")
            return sga
        else:
            #Unrecognized command
            print(f"Command of type {splitcmd[0]} not recognized")
            return False
        return False
        #END of function runCommand1

    def getCurrentApplications(self, timeout=10, verbose=False):
        """getCurrentApplications:
        Returns a list of current applications:
        Inputs: timeout (int) - the timeout time, default 10
                verbose (Boolean) - Verbose mode if True"""
        try:
            olddelay=self.gettimeout()
            self.settimeout(timeout)
            retval= self.sendscpi(":SYST:APPL:CAPP?")
            if retval is None or retval=='' or retval.strip()=='':
                self.settimeout(olddelay)  
                return []
            if verbose:
                print(retval)
            currapplist=[x.strip() for x in retval.split(',')]
            for idx in range(len(currapplist)):
                if(currapplist[idx][-1]==','):
                    currapplist[idx]=currapplist[idx][0:-1]
            #Cast all the app names into Application objects
            currapps=[]
            for x in currapplist:
                if x != '':
                    currapps.append(Application(appId=x))
            self.settimeout(olddelay)                    
            return currapps

        except TimeoutError as te:
            print("SCPI command timed out")
            self.settimeout(olddelay)
            return None
        
    def getLaserStatus(self):
        """Get high level laser status based on the :OUTPUT:OPTIC? SCPI command"""
        return self.sendscpi(":OUTPUT:OPTIC?")
    
    def getLaserOn(self):
        """Returns whether laser is on according to high level status"""
        return self.getLaserStatus == 'ON'
    
    def setLaserOn(self):
        """Sets the laser to on using high level protocol (SCPI)"""
        if not self.laserStatus:
            scpival=self.sendscpi(":OUTPUT:OPTIC ON")
            print(scpival)
            self.laserStatus='0,' in scpival and 'No error' in scpival
            return self.laserStatus
        return self.laserStatus

    def setLaserOff(self):
        """Sets the laser to off using high level protocol (SCPI)"""
        if self.laserStatus:
            scpival = self.sendscpi(':OUTPUT:OPTIC OFF')
            print(scpival)
            self.laserStatus= (not ('0,' in scpival)) or (not ('No error' in scpival))
            if self.laserStatus:
                writelog(scpival)
            return not self.laserStatus
        else:
            return self.laserStatus
    def getActiveApp(self):
        """Returns current app"""
        return self.curr
    
"""
Any question about the script, please contact Brad Sicotte at 
email: bsicotte@teracomm.com
"""