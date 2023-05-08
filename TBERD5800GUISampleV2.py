"""TBERD5800GuiSample (V2.0)
Provides a simple GUI interface for basic TB5800 Commands
v2.0 : Initialization of TB5000 does not hang up TKinter window
v3.1b : Uses python3.2 and above's concurrent.futures to allow wait for peek
Required Libraries:
TBERD5800Controls
tkinter
concurrent.futures

Python Version must be at least 3.2

Note for mac users.
To gracefully exit TB5800 app, either use file-close or press "Exit App" button
"""
import tkinter
from TBERD5800Controls import *
import time
#from threading import Thread
import concurrent.futures
defaultfont='TkDefaultFont'
stickall="news"
DEFAULT_PAD_X=8
DEFAULT_PAD_Y=3
DEFAULT_FONT_SETTINGS=(defaultfont, 10)
defaultIpAddr='192.168.1.12'
defaultApp="TermEth100GL2Traffic 1"
tb1=TBERD5800Controls(defaultIpAddr)
TEXT_BOX_START_IDX="1.0"
threadManager=concurrent.futures.ThreadPoolExecutor()
currthreads=[]
def get_live_threads(curr=currthreads):
    livethreads=[]
    for thr in curr:
        if isinstance(thr, concurrent.futures.Future) and thr.running():
            livethreads.append(thr)
        #Save for Thread if necessary
    return livethreads
    
def printPeekVal():
    currthreads=get_live_threads()
    #if len(currthreads)>0:
    #    print(f'Error: {len(currthreads)} active threads, must be 0')
    #    write_text_box(f'Error: {len(currthreads)} active threads, must be 0')
    #    return False
    peekval=getInt(peekentry.get())
    peekthread=threadManager.submit(tb1.peek, peekval)
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
    currthreads=get_live_threads()
    if len(currthreads)>0:
        #print(f'Error: {len(currthreads)} active threads, must be 0')
        write_text_box(f'Error: {len(currthreads)} active threads, must be 0')
        return False
    write_text_box("Executing Poke Command")
    pokeaddr=pokeaddrentry.get()
    pokeval=pokevalentry.get()
    time.sleep(0.5)
    #DUMMY LOAD
    pokethread=threadManager.submit(tb1.poke, getInt(pokeaddr), getInt(pokeval))
    currthreads.append(pokethread)
    time.sleep(0.5)
    write_text_box(f'POKE {pokeaddr}, {pokeval} retured {pokethread.result()}')
    return True
 

def readtextbox():
    textboxrawstr=textbox1.get(TEXT_BOX_START_IDX, "end").strip()
    textboxvals=[x.strip() for x in textboxrawstr.split('\n')]
    print(textboxvals)

def scpipressed():
    scpival=scpientry.get().strip()
    scpireturn=tb1.sendscpi(scpival)
    write_text_box(f'SCPI {scpival} returned {scpireturn}')

def write_text_box(str):
    textbox1.config(state=tkinter.NORMAL)
    textbox1.delete("1.0", "end")
    textval=str.strip()
    textbox1.insert('1.0', textval)
    textbox1.config(state=tkinter.DISABLED)

def connect_to_tb():
    try:
        tb1.settimeout(60)
        tb1.connect()
        time.sleep(0.5)
        tb1.setRemoteOn()
        time.sleep(0.5)
        tb1.connectToApp(defaultApp)
    except Exception as e:
        time.sleep(10)
        tb1.connect()
        time.sleep(0.5)
        tb1.setRemoteOn()
        time.sleep(0.5)
        tb1.connectToApp(defaultApp)

def init_tb5800():
    currthreads=get_live_threads()
    write_text_box("Connecting To TB5800")
    time.sleep(0.5)
    timerthread=threadManager.submit(connect_to_tb)
    time.sleep(0.5)
    currthreads.append(timerthread)
    idx=0
    while timerthread.running():
        #print(idx)
        write_text_box(f'Connnecting: {idx}/max 60')
        time.sleep(1)
        idx+=1
    #thread2.join() #Auto joins timerthread
    #time.sleep(1)
    timerthread.cancel()
    write_text_box("App Connected")

def exitApp():
    
    currthreads=get_live_threads()
    write_text_box("Exiting TB5800 App")
    time.sleep(0.5)
    exitthread=threadManager.submit(tb1.exit)
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
    currthreads=get_live_threads()
    thread1=threadManager.submit(func)
    currthreads.append(thread1)
    return thread1
def startPeek():
    write_text_box("Executing PEEK Function")
    startThread(printPeekVal)
def startPoke():
    write_text_box("Executing POKE Function")
    startThread(pokebuttonpressed)
def initfunc():
    startThread(init_tb5800)
def startScpi():
    write_text_box("Executing SCPI Command")  
    startThread(scpipressed)
def startExit():
    write_text_box("Exiting TB5800 App")
    startThread(exitApp)

if __name__=='__main__':
    window=tkinter.Tk()
    
    window.title("TB5800 Peek Poke Test App ")
    window.geometry('800x600')
    frame=tkinter.Frame(window)
    cmdlabel=tkinter.Label(frame, text='TB5800 Commands', font=(defaultfont, 14))
    
    cmdlabel.grid(row=0, column=0, columnspan=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    peeklabel=tkinter.Label(frame, text='Peek', font=DEFAULT_FONT_SETTINGS)
    peeklabel.grid(row=1, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    peekentry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    peekentry.insert(0, "0x00")
    peekentry.grid(row=1, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    peekbutton=tkinter.Button(frame, text="Peek", command=startPeek)
    peekbutton.grid(row=1, column=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    #peekvalreturnlabel=tkinter.Label(frame, text='PEEK return', font=DEFAULT_FONT_SETTINGS)
    #peekvalreturnlabel.grid(row=2, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    #peekvallabel=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    #peekvallabel.grid(row=2, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
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
    pokebutton.grid(row=3, column=2, rowspan=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=5*DEFAULT_PAD_Y)
    #pokereturnlabel=tkinter.Label(frame, text="Poke Return Status", font=DEFAULT_FONT_SETTINGS)
    #pokereturnlabel.grid(row=5, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    #pokereturnval=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    #pokereturnval.insert(0, "False")
    #pokereturnval.grid(row=5, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    scpilabel=tkinter.Label(frame, text="SCPI", font=DEFAULT_FONT_SETTINGS)
    scpilabel.grid(row=6, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    scpientry=tkinter.Entry(frame, font=DEFAULT_FONT_SETTINGS)
    scpientry.grid(row=6, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    scpibutton=tkinter.Button(frame, text="Send SCPI", command=startScpi)
    scpibutton.grid(row=6, column=2, sticky=stickall, padx=5*DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    #CHANGE Row numbers accordingly
    exitbutton=tkinter.Button(frame, text="Exit App", command=startExit)
    exitbutton.grid(row=7, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    textbox1=tkinter.Text(frame, width=80, height=12, state=tkinter.DISABLED)
    textbox1.grid(row=8, column=0, columnspan=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    frame.pack()
    window.after(100, initfunc)
    #write_text_box("Connecting To TB5800")
    window.mainloop()

    tb1.exit()


    """
    Any question about the script, please contact Brad Sicotte at 
    email: bsicotte@teracomm.com
    """