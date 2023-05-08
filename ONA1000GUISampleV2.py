"""ONA1000GuiSample (V2.0)
Provides a simple GUI interface for basic ONA1000 Commands
v2.0 : Initialization of ONA1000 does not hang up TKinter window
v3.1b : Uses python3.2 and above's concurrent.futures to allow wait for peek
Required Libraries:
ONA1000Controls (Depends on TBControllerCommon)
tkinter
concurrent.futures

Python Version must be at least 3.2
"""
import tkinter
from ONA1000Controls import *
import time
import concurrent.futures
#Set default settings
defaultfont='TkDefaultFont'
stickall="news"
DEFAULT_PAD_X=8
DEFAULT_PAD_Y=3
DEFAULT_FONT_SETTINGS=(defaultfont, 10)
#Set the IP Address Here
defaultIpAddr='192.168.1.20'
defaultApp="TermEth100GL2Traffic 1"
#Initiate
ona1=ONA1000Controls(defaultIpAddr)
TEXT_BOX_START_IDX="1.0"
threadManager=concurrent.futures.ThreadPoolExecutor()
currthreads=[]
def get_live_threads(curr=currthreads):
    """get_live_threads:
    Checks threads in list curr and appends all live ones to a new array
    Returns new array
    Inputs:
    curr (Array) : The list of threads (currthreads array is default)
    Returns
    List of active threads
    """
    livethreads=[]
    for thr in curr:
        if isinstance(thr, concurrent.futures.Future) and thr.running():
            livethreads.append(thr)
        #Save for Thread if necessary
    return livethreads
    
def printPeekVal():
    """printPeekVal:
    Function to print peek value using threading, receiving input from TKinter GUI"""
    currthreads=get_live_threads()
    #if len(currthreads)>0:
    #    print(f'Error: {len(currthreads)} active threads, must be 0')
    #    write_text_box(f'Error: {len(currthreads)} active threads, must be 0')
    #    return False
    peekval=getInt(peekentry.get())
    
    peekthread=threadManager.submit(ona1.peek, peekval)
    time.sleep(0.5)
    currthreads.append(peekthread)
    idx=0
    while peekthread.running():
        #print(f"Executing Peek Command {idx}")
        write_text_box(f"Executing Peek Command ({idx})")
        time.sleep(1)
        idx+=1
    write_text_box(f'PEEK {hex(peekval)} returned {hex(peekthread.result())}')
    #print("Test button pressed.")

def pokebuttonpressed():
    """pokebuttonpressed
    Function to execute poke command using threading, receiving input
    from TKinter GUI"""
    currthreads=get_live_threads()
    if len(currthreads)>0:
        #print(f'Error: {len(currthreads)} active threads, must be 0')
        write_text_box(f'Error: {len(currthreads)} active threads, must be 0')
        return False
    write_text_box("Executing Poke Command")
    pokeaddr=pokeaddrentry.get()
    pokeval=pokevalentry.get()
    #DUMMY LOAD
    pokethread=threadManager.submit(ona1.poke, getInt(pokeaddr), getInt(pokeval))
    currthreads.append(pokethread)
    write_text_box(f'POKE {pokeaddr}, {pokeval} retured {pokethread.result()}')
    return True
 

def readtextbox():
    """readtextbox:
    Reads the text box"""
    textboxrawstr=textbox1.get(TEXT_BOX_START_IDX, "end").strip()
    textboxvals=[x.strip() for x in textboxrawstr.split('\n')]
    print(textboxvals)

def scpipressed():
    """scpipressed
    A thread-based function to receive scpi info from TKinter GUI
    and run scpi command"""
    scpival=scpientry.get().strip()
    scpireturn=ona1.sendscpi(scpival)
    write_text_box(f'SCPI {scpival} returned {scpireturn}')

def write_text_box(str):
    """Writes to text box
    Inputs:
    str (string) : The string to write"""
    textbox1.config(state=tkinter.NORMAL)
    textbox1.delete("1.0", "end")
    textval=str.strip()
    textbox1.insert('1.0', textval)
    textbox1.config(state=tkinter.DISABLED)

def connect_to_ona():
    """connect_to_ona
    Connects to ONA unit
    """
    try:
        ona1.settimeout(60)
        ona1.connect()
        time.sleep(0.5)
        ona1.setRemoteOn()
        time.sleep(0.5)
        ona1.connectToApp(defaultApp)
    except Exception as e:
        time.sleep(10)
        ona1.connect()
        time.sleep(0.5)
        ona1.setRemoteOn()
        time.sleep(0.5)
        ona1.connectToApp(defaultApp)

def init_ona1000():
    """init_ona1000:
    Thread-based function to connect to ONA and print timer 
    on the text box"""
    currthreads=get_live_threads()
    write_text_box("Connecting To ONA1000")
    time.sleep(0.5)
    timerthread=threadManager.submit(connect_to_ona)
    time.sleep(0.5)
    currthreads.append(timerthread)
    idx=0
    while timerthread.running():
        #print(idx)
        write_text_box(f'Connnecting: {idx}/max 90')
        time.sleep(1)
        idx+=1
    #thread2.join() #Auto joins timerthread
    #time.sleep(1)
    timerthread.cancel()
    write_text_box("App Connected")

def exitApp():
    
    currthreads=get_live_threads()
    write_text_box("Exiting ONA1000 App")
    time.sleep(0.5)
    exitthread=threadManager.submit(ona1.exit)
    time.sleep(0.5)
    currthreads.append(exitthread)
    idx=0
    while exitthread.running():
        #print(idx)
        write_text_box(f'Exiting: {idx}/max 60')
        time.sleep(1)
        idx+=1
    #thread2.join() #Auto joins timerthread
    #time.sleep(1)
    write_text_box("App Exited")


def startThread(func):
    """startThread:
    Start a new thread given func
    Inputs:
    func (function) :  the function to execute"""
    currthreads=get_live_threads()
    thread1=threadManager.submit(func)
    currthreads.append(thread1)
    return thread1
def startPeek():
    """startPeek
    Start the PEEK thread"""
    write_text_box("Executing PEEK Function")
    startThread(printPeekVal)
def startPoke():
    """startPoke
    Start the POKE thread"""
    write_text_box("Executing POKE Function")
    startThread(pokebuttonpressed)
def initfunc():
    """initfunc
    Start the init thread"""
    startThread(init_ona1000)
def startScpi():
    """startScpi
    Start the SCPI thread"""
    write_text_box("Executing SCPI Command")  
    startThread(scpipressed)
def startExit():
    write_text_box("Exiting ONA App")
    startThread(exitApp)

if __name__=='__main__':
    #Define main window
    window=tkinter.Tk()
    
    window.title("ONA1000 Peek Poke Test App ")
    window.geometry('800x600')
    #Use auto-centering frame, with grid inside
    frame=tkinter.Frame(window)

    cmdlabel=tkinter.Label(frame, text='ONA1000 Commands', font=(defaultfont, 14))
    cmdlabel.grid(row=0, column=0, columnspan=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    peeklabel=tkinter.Label(frame, text='Peek', font=DEFAULT_FONT_SETTINGS)
    peeklabel.grid(row=1, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    peekentry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    peekentry.insert(0, "0x00")
    peekentry.grid(row=1, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    peekbutton=tkinter.Button(frame, text="Peek", command=startPeek)
    peekbutton.grid(row=1, column=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    pokeaddrlabel=tkinter.Label(frame, text="Poke Address", font=DEFAULT_FONT_SETTINGS)
    pokeaddrlabel.grid(row=3, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    pokeaddrentry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    pokeaddrentry.insert(0, "0x00")
    pokeaddrentry.grid(row=3, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    pokevallabel=tkinter.Label(frame, text="Poke Value", font=DEFAULT_FONT_SETTINGS)
    pokevallabel.grid(row=4, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    pokevalentry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    pokevalentry.insert(0, "0x00")
    pokevalentry.grid(row=4, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    pokebutton=tkinter.Button(frame,  text="Poke", command=startPoke)
    pokebutton.grid(row=3, column=2, rowspan=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=4*DEFAULT_PAD_Y)
  
    scpilabel=tkinter.Label(frame, text="SCPI", font=DEFAULT_FONT_SETTINGS)
    scpilabel.grid(row=6, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    scpientry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    scpientry.grid(row=6, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    scpibutton=tkinter.Button(frame, text="Send SCPI", command=startScpi)
    scpibutton.grid(row=6, column=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)

    exitbutton=tkinter.Button(frame, text="Exit App", command=startExit)
    exitbutton.grid(row=7, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    textbox1=tkinter.Text(frame, width=80, height=12, state=tkinter.DISABLED)
    textbox1.grid(row=8, column=0, columnspan=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    
    #Pack the frame centered in the window
    frame.pack()
    #Wait 100ms and then call initfunc
    window.after(100, initfunc)
    #Main loop : Blocks until window is closed
    window.mainloop()
    #Exit ONA after window is closed
    ona1.exit()


    """
    Any question about the script, please contact Brad Sicotte at 
    email: bsicotte@teracomm.com
    """