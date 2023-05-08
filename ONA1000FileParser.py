"""ONA1000FileParserTest.py: A sample file parser that parses a file using ONA1000Controls.parseInputFile
                    and then runs the proper commands.
"""

helpcommandlist="""
    Input file format:
    
    Input file must be one command per line
    Acceptable commands are:

                START appname : Starts appname and closes all other apps.  
                    appname may be multiple words, including arguments (60 second default timeout)
                    Example: START TermEth100GL2Traffic 1
                MULTISTART appname : Starts appname, not closing any other apps
                    Same Format as START
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
                EXIT or QUIT: Exit program; Exits Remote Mode
                CLOSEAPP appId : Exits app with given appId

                Use MULTIAPP to select an existing app in auto mode.
        All register and page should be 0x?? for hex, 0b???????? for binary, or a decimal integer
"""
from ONA1000Controls import *
import time
import argparse

DEBUG=False
defaultApp="TermEth100GL2Traffic 1"
defaultIP='192.168.1.35'
defaultFileName='testcmd.txt'
parser=argparse.ArgumentParser()
parser.add_argument('--app', '-a', help='ONA1000 Application Name', default=defaultApp)
parser.add_argument('--ipaddr', '-i', help='The IP address of the ONA1000', default=defaultIP)
parser.add_argument('--infile', '-f', help='The input file to read', default=defaultFileName)
parser.add_argument('--outfile', '-o', help='The output file to write to; writes to terminal if none provided')
parser.add_argument('--listcommands', '-l', action='store_true', help='Bring up list of commands')
parser.add_argument('--delay', '-D', help='Default delay between commands')
parser.add_argument('--noapp', '-N', action='store_true', help='Load No Application')
args=parser.parse_args()
#print(args)
if args.listcommands:
    print(helpcommandlist)
#elif args.ipaddr is None or args.infile is None:
#    print('--infile (-f) flags are required for operation')
else:
    if args.noapp:
        appToConnect=None
    else:
        appToConnect=args.app
    #Set application, ip address, input file, and default delay to connect to
    #Test for definition of appToConnect
    inputfile="testcmd.txt"
    if args.infile is not None:
        inputfile=args.infile
    ipaddr=args.ipaddr

    defaultdelay=10
    if args.delay is not None:
        try:
            defaultdelay=int(args.delay)
        except Exception as e:
            print("Invalid delay value, setting default delay of 10")
            defaultdelay=10

    #Parse the input file line by line and get command array
    try:
        fp=open(inputfile, "r")
        commandarray=fp.readlines()
        #Set up ONA1000
        ona1=ONA1000Controls(targetip=ipaddr, timeout=defaultdelay, debug=DEBUG)
        time.sleep(1)
        try:
            ona1.connect()
            writelog("Connecting to App")
            time.sleep(1)
            ona1.setRemoteOn()
            time.sleep(1)
        except Exception as e:
            print(f"ONA1000 Did not connect : Exception {e}")
        #Connect to Application
            
        
        if appToConnect is not None:
            try:
                print(f'Current App: {ona1.getActiveApp()}')
            except Exception as e:
                print(f"Get Active App failed: {e}")
            else:
                try:
                    ona1.connectToApp(appToConnect)
                except Exception as e:
                    print(f"Connect to app {appToConnect} failed : {e}")
                
        time.sleep(1)
        writelog("Sending commands")
        #Send and execute commands one by one
        cmdresults=[]
        idx=0
        cmdlength=len(commandarray)
        for cmd in commandarray:
            idx+=1
            print(f'Current Application: {ona1.getActiveApp()}')
            print(f"command {cmd.strip()} ({idx}/{cmdlength})")
            try:
                
                cmdresults.append(ona1.runCommand(cmd))
            except Exception as e:
                print(f"Run command {cmd.strip()} ({idx}/{cmdlength}) failed : {e}")
                cmdresults.append(False)
        print("Exiting ONA1000 Remote Mode.")
        try:
            ona1.exit() 
        except Exception as e:
            print(f"Exit App Exception : {e}")
        print("Final Results:")
        if args.outfile is not None:
            try:
                fp=open(args.outfile, 'w')
            except Exception as e:
                fp=None
        else:
            fp=None
        #Print results
        for idx in range(len(commandarray)):
            #Iterate through commands in commandarray by index
            if isinstance(cmdresults[idx], bool):
                if fp is not None:
                    fp.write(f"({idx+1}) {commandarray[idx]} returned {cmdresults[idx]}\n")
                print(f"({idx+1}) {commandarray[idx]} returned {cmdresults[idx]}")
            else:
                try:
                    #Try to convert result to hex and print if successful
                    hxr=hex(cmdresults[idx])
                    if fp is not None:
                        fp.write(f"({idx+1}) {commandarray[idx]} returned {hxr}\n")
                    print(f"({idx+1}) {commandarray[idx]} returned {hxr}")
                except Exception as e:
                    #Otherwise print as string
                    if fp is not None:
                        fp.write(f"({idx+1}) {commandarray[idx]} returned {cmdresults[idx]}\n")
                    print(f"({idx+1}) {commandarray[idx]} returned {cmdresults[idx]}")
    except Exception as e:
        print(f'Exception : {e}')
    
    def exit(self, timeout=30):
        """exit:
        Gracefully exits remote mode and re-enables GUI if necessary 
        Base Version for ONA1000"""
        self.settimeout(timeout)
        self.sendscpi(":EXIT")
        self.sendscpi("*GUI")# Must return to gui, returns to default app 
        self.socketClose()

    """
    Any question about the script, please contact Brad Sicotte at 
    email: bsicotte@teracomm.com
    """