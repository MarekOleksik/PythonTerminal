#
# Serial COM Port terminal program
#
import tkinter as tk
import tkinter.scrolledtext as tkscrolledtext
from tkinter import *
from tkinter import filedialog

import serial

import serial_rx_tx
import _thread
import time
from tkinter import messagebox

# globals
serialPort = serial_rx_tx.SerialPort()
logFile = None

root = tk.Tk() # create a Tk root window
root.title( "TERMINAL - Serial Data Terminal" )
# set up the window size and position
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width/2
window_height = screen_width/3
window_position_x = screen_width/2 - window_width/2
window_position_y = screen_height/2 - window_height/2
root.geometry('%dx%d+%d+%d' % (window_width, window_height, window_position_x, window_position_y))

# scrolled text box used to display the serial data
frame = tk.Frame(root, bg='cyan')
frame.pack(side="bottom", fill='both', expand='no')
textbox = tkscrolledtext.ScrolledText(master=frame, wrap='word', width=180, height=28) #width=characters, height=lines
textbox.pack(side='bottom', fill='y', expand=True, padx=0, pady=0)
textbox.config(font="bold")

#COM Port label
label_comport = Label(root,width=10,height=2,text="COM Port:")
label_comport.place(x=10,y=15)
label_comport.config(font="bold")

#COM Port entry box
comport_edit = Entry(root,width=10)
comport_edit.place(x=100,y=25)
comport_edit.config(font="bold")
comport_edit.insert(END,"COM2")

# serial data callback function
def OnReceiveSerialData(message):
    str_message = message.decode("utf-8")
    textbox.insert('1.0', str_message)

# Register the callback above with the serial port object
serialPort.RegisterReceiveCallback(OnReceiveSerialData)

def sdterm_main():
    root.after(200, sdterm_main)  # run the main loop once each 200 ms

#
#  commands associated with button presses
#
def OpenCommand():
    if button_openclose.cget("text") == 'Otwórz port COM':
        comport = comport_edit.get()
        baudrate = baudrate_edit.get()
        bytesize = bytesize_edit.get()
        print(bytesize)
        parity = parity_edit.get()
        stopbits = stopbits_edit.get()
        serialPort.Open(comport,baudrate,bytesize,parity,stopbits)
        button_openclose.config(text='Zamknij port COM')
        textbox.insert('1.0', "COM Port Otwarty\r\n")
    elif button_openclose.cget("text") == 'Zamknij port COM':
        if button_replaylog.cget('text') == 'Stop Replay Log':
            textbox.insert('1.0',"Stop Log Replay first\r\n")
        else:
            serialPort.Close()
            button_openclose.config(text='Otwórz port COM')
            textbox.insert('1.0',"COM Port Zamknięty\r\n")


def ClearDataCommand():
    textbox.delete('1.0',END)

def SendDataCommand():
    message = senddata_edit.get()
    if serialPort.IsOpen():
        message += '\r\n'
        serialPort.Send(message)
        textbox.insert('1.0',message)
    else:
        textbox.insert('1.0', "Not sent - COM port is closed\r\n")

def ReplayLogFile():
    try:
      if logFile != None:
        readline = logFile.readline()
        global serialPort
        serialPort.Send(readline)
    except:
      print("Exception in ReplayLogFile()")

def ReplayLogThread():
    while True:
        time.sleep(1.0)
        global logFile
        if serialPort.IsOpen():
            if logFile != None:
                ReplayLogFile()

def OpenLogFile():
    if not serialPort.IsOpen():
        textbox.insert('1.0', "Open COM port first\r\n")
    else:
        if button_replaylog.cget('text') == 'Replay Log':
            try:
                root.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                           filetypes=(("log files", "*.log"), ("all files", "*.*")))
                global logFile
                logFile = open(root.filename,'r')
                _thread.start_new_thread(ReplayLogThread, ())
                button_replaylog.config(text='Stop Log Replay')
                textbox.insert('1.0', "Sending to open COM port from: " + root.filename + "\r\n")
            except:
                textbox.insert('1.0', "Could not open log file\r\n")
        else:
            button_replaylog.config(text='Replay Log')
            textbox.insert('1.0', "Stopped sending messages to open COM port\r\n")
            logFile = None

# COM Port open/close button
button_openclose = Button(root,text="Otwórz port COM",width=20,command=OpenCommand)
button_openclose.config(font="bold")
button_openclose.place(x=420,y=30)

#Clear Rx Data button
button_cleardata = Button(root,text="Wyczyść",width=20,command=ClearDataCommand)
button_cleardata.config(font="bold")
button_cleardata.place(x=420,y=72)

#Send Message button
button_senddata = Button(root,text="Wyślij",width=15,command=SendDataCommand)
button_senddata.config(font="bold")
button_senddata.place(x=620,y=30)

#Replay Log button
button_replaylog = Button(root,text="Zapisz logi",width=15,command=OpenLogFile)
button_replaylog.config(font="bold")
button_replaylog.place(x=770,y=30)

#Send Data entry box
senddata_edit = Entry(root,width=34)
senddata_edit.place(x=620,y=78)
senddata_edit.config(font="bold")
senddata_edit.insert(END,"Tekst")

#Baud Rate label
label_baud = Label(root,width=10,height=2,text="Liczba bit/s:")
label_baud.place(x=10,y=50)
label_baud.config(font="bold")

#Baud Rate entry box
baudrate_edit = Entry(root,width=10)
baudrate_edit.place(x=100,y=60)
baudrate_edit.config(font="bold")
baudrate_edit.insert(END,"38400")

#Bytesize label
label_bytesize = Label(root,width=10,height=2,text="Bity danych:")
label_bytesize.place(x=10,y=85)
label_bytesize.config(font="bold")

#Bytesize entry box
bytesize_edit = Entry(root,width=10)
bytesize_edit.place(x=100,y=95)
bytesize_edit.config(font="bold")
bytesize_edit.insert(END, "serial.EIGHTBITS")

#Parity label
label_parity = Label(root,width=10,height=2,text="Parzystość:")
label_parity.place(x=200,y=15)
label_parity.config(font="bold")

#Parity entry box
parity_edit = Entry(root,width=10)
parity_edit.place(x=290,y=25)
parity_edit.config(font="bold")
parity_edit.insert(END,"PARITY_NONE")

#Stopbits label
label_stopbits = Label(root,width=10,height=2,text="Bity stopu:")
label_stopbits.place(x=200,y=50)
label_stopbits.config(font="bold")

#Stopbits entry box
stopbits_edit = Entry(root,width=10)
stopbits_edit.place(x=290,y=60)
stopbits_edit.config(font="bold")
stopbits_edit.insert(END,"STOPBITS_ONE")

#
# The main loop
#
root.after(200, sdterm_main)
root.mainloop()
#
