from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk
from ComandiGui import RunControl
from ACQ_nexys import acquisitor
from tkinter import filedialog
from threading import *

def connect():
    RC.Port.porta = Port_rc.get()
    portvalue = RC.Port.Config()
    if portvalue:
        Connect_label.config(text='Connected', fg='#000000', bg='lightgreen')
    elif ~ portvalue:
        messagebox.showerror(title='ERROR', message='Serial not found')
    else:
        pass
    RC.LoopRead()

def endisButton(button, key):
    if button.cget('text') == 'Enabled':
        button.config(text='Disabled', bg='red', relief=SUNKEN)
        RC.LoopRunControll(key=key, dato='D')
    elif button.cget('text') == 'Disabled':
        button.config(text='Enabled', bg='#00b85b', relief=RAISED)
        RC.LoopRunControll(key=key, dato='E')

def checkbutton(value, button):
    if value == 'Enabled':
        button.config(text='Enabled', bg='#00b85b', relief=RAISED)
    elif value == 'Disabled':
        button.config(text='Disabled', bg='red', relief=SUNKEN)


def rst_multychannel():
    if rst_multy.cget('text') == 'Free':
        rst_multy.config(text='Resetted', bg='grey', relief=SUNKEN)
        RC.LoopRunControll(key='6', dato='Y')
    elif rst_multy.cget('text') == 'Resetted':
        rst_multy.config(text='Free', bg='#f0f0f0' , relief=RAISED)
        RC.LoopRunControll(key='6', dato='N')

def calib():
    if calB.cget('text') == 'NO':
        calB.config(text='YES', bg='grey', relief=SUNKEN)
        RC.LoopRunControll(key='8', dato='Y')
    elif calB.cget('text') == 'YES':
        calB.config(text='NO', bg='#f0f0f0' , relief=RAISED)
        RC.LoopRunControll(key='8', dato='N')

def AM():
    if AMB.cget('text') == 'Automatic':
        AMB.config(text='Manual', bg='#f0f0f0')
        RC.LoopRunControll(key='9', dato='M')
    elif AMB.cget('text') == 'Manual':
        AMB.config(text='Automatic', bg='#f0f0f0')
        RC.LoopRunControll(key='9', dato='A')

def EI():
    if EIB.cget('text') == 'External':
        EIB.config(text='Internal', bg='#f0f0f0')
        RC.LoopRunControll(key='10', dato='I')
    elif EIB.cget('text') == 'Internal':
        EIB.config(text='External', bg='#f0f0f0')
        RC.LoopRunControll(key='10', dato='E')

def savelogs():
    new_window = Toplevel()
    new_window.geometry('280x200')
    new_window.title('Save logs')
    Label(new_window, text='File name:').grid(row=0, column=0)
    Label(new_window, text='Save times (at 1 Hz):').grid(row=1, column=0)
    nameEntry = Entry(new_window)
    nameEntry.grid(row=0, column=1)
    rateEntry = Entry(new_window)
    rateEntry.insert(0, '0')
    rateEntry.grid(row=1, column=1)
    okbutton = Button(new_window, text='Save')
    okbutton.grid(row=2, column=1)
    okbutton.config(command=lambda : RC.LoopRunControll(key='slog', dato=rateEntry.get(), name=nameEntry.get()))

def savevalues():
    readvalues()
    new_window = Toplevel()
    new_window.geometry('280x200')
    new_window.title('Save values')
    Label(new_window, text='File name:').grid(row=0, column=0)
    nameEntry = Entry(new_window)
    nameEntry.grid(row=0, column=1)
    okbutton = Button(new_window, text='Save')
    okbutton.grid(row=1, column=1)
    okbutton.config(command=lambda : RC.LoopRunControll(key='save', name=nameEntry.get()))

def openvalues():
    filepath = filedialog.askopenfilename(initialdir='C:/Users/alexa/PycharmProjects/Python_ACQ_tesi/NexysmPMT/RunCrtV3',
                                          filetypes=(('config_files', '*.cfg'),('text_files', '*.txt'),
                                                     ('all_files', '*.*')))
    RC.LoopRunControll(key='open', name=filepath)
    readvalues()


def readvalues():
    RC.LoopRead()
    checkbutton(RC.Poweren0, pw_en0)
    checkbutton(RC.Poweren1, pw_en1)
    checkbutton(RC.Acqen0, acq_en0)
    checkbutton(RC.Acqen1, acq_en1)
    checkbutton(RC.PPSchen, PPSchen)
    ppscount.config(text=f'{RC.PPScount}')
    Tag0ok.config(text=f'{RC.Tag_0ok}')
    rate0.config(text=f'{RC.FreCh0}')
    rate1.config(text=f'{RC.FreCh1}')
    deadtime.config(text=f'{RC.TempoMorto} %')
    fifo.config(text=f'{RC.Fifo}')
    pll.config(text=f'{RC.PLL}')
    ovc0.config(text=f'{RC.Overcurrent0}')
    ovc1.config(text=f'{RC.Overcurrent1}')
    clkstate.config(text=f'{RC.Clkreg}')
    if RC.Rstch == 'No':
        rst_multy.config(text='Free', bg='#f0f0f0' , relief=RAISED)
    elif RC.Rstch== 'Yes':
        rst_multy.config(text='Resetted', bg='grey', relief=SUNKEN)
    if RC.Pfreq == 0:
        puls_freq.delete(0, END)
        puls_freq.insert(0, '0')
    else:
        puls_freq.delete(0, END)
        puls_freq.insert(0, f'{RC.Pfreq.split(" ")[0]}')
    if RC.Calibflag == 'No':
        calB.config(text='NO', bg='#f0f0f0' , relief=RAISED)
    elif RC.Calibflag == 'Yes':
        calB.config(text='YES', bg='grey' , relief=SUNKEN)
    if RC.Clkautman == 'CLK Automatic':
        AMB.config(text='Automatic', bg='#f0f0f0')
    elif RC.Clkautman == 'CLK Manual':
        AMB.config(text='Manual', bg='#f0f0f0')
    if RC.Clkextin == 'CLK Internal':
        EIB.config(text='Internal', bg='#f0f0f0')
    elif RC.Clkextin == 'CLK External':
        EIB.config(text='External', bg='#f0f0f0')
    Tag0_freq.delete(0, END)
    Tag0_freq.insert(0, RC.Starttag0)
    peak0.delete(0, END)
    peak0.insert(0, RC.Peak0)
    peak1.delete(0, END)
    peak1.insert(0, RC.Peak1)
    delay0.delete(0, END)
    delay0.insert(0, RC.Delay0)
    delay1.delete(0, END)
    delay1.insert(0, RC.Delay1)

def acquisition(numevent, port, filename):
    AC = acquisitor(MaxEvent=numevent, port=port, filename=filename)
    x = Thread(target=AC.nexysACQ, args=())
    y = Thread(target=checkacq, args=(AC, numevent))
    x.start()
    y.start()

def checkacq(acquisitor, numevent):
    while acquisitor.NumEvent < numevent:
        bar.start()
    bar.stop()

## Backgorund color
frame_bg = '#c9c9c9'

## Window
window = Tk()
window.geometry('820x725')
window.title('Run Control Nexys')
window.resizable(False, False)
window.config(bg=frame_bg)

## Logo
logo = ImageTk.PhotoImage(file='logo.jpg')
window.iconphoto(True, logo)

## Menubar
menubar = Menu(window)
window.config(menu=menubar)

fileMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=fileMenu)
fileMenu.add_command(label='Save config', command=savevalues)
fileMenu.add_command(label='Open config', command=openvalues)
fileMenu.add_separator()
fileMenu.add_command(label='Exit', command=lambda : quit())

logMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Log', menu=logMenu)
logMenu.add_command(label='Save logs', command=savelogs)

## Serial connection
Label(window, text='Serial port for Run Control: ', bg=frame_bg).place(x=1, y=10)
Port_rc = Entry(window)
Port_rc.insert(0, 'COM8')
Port_rc.place(x=150, y=10)
Button(window, text='Connect', command=connect).place(x=280, y=8)
Connect_label = Label(window, width=15, text='Not connected', bg='red')
Connect_label.place(x=350, y=10)

RC = RunControl()

## Refresh button
Refresh = Button(window, text='Refresh', command=readvalues, width=25)
Refresh.place(x=500, y=10)

## Run control parameters
Label(window, text='Run Control parameters to set:', bg=frame_bg, font=('Helvetica', 14)).place(x=1, y=80)

Label(window, text='Power enable CH0:', bg=frame_bg).place(x=1, y=120)
pw_en0 = Button(window, text='Enabled', bg='#00b85b')
pw_en0.config(command=lambda :endisButton(button=pw_en0, key='0'))
pw_en0.place(x=250, y=118)

Label(window, text='Power enable CH1:', bg=frame_bg).place(x=1, y=160)
pw_en1 = Button(window, text='Enabled', bg='#00b85b')
pw_en1.place(x=250, y=158)
pw_en1.config(command=lambda :endisButton(button=pw_en1, key='1'))

Label(window, text='Acq enable CH0:', bg=frame_bg).place(x=1, y=200)
acq_en0 = Button(window, text='Enabled', bg='#00b85b')
acq_en0.place(x=250, y=198)
acq_en0.config(command=lambda :endisButton(button=acq_en0, key='2'))

Label(window, text='Acq enable CH1:', bg=frame_bg).place(x=1, y=240)
acq_en1 = Button(window, text='Enabled', bg='#00b85b')
acq_en1.place(x=250, y=238)
acq_en1.config(command=lambda :endisButton(button=acq_en1, key='3'))

Label(window, text='Pulser frequency:', bg=frame_bg).place(x=1, y=280)
Label(window, text='Hz', bg=frame_bg).place(x=230, y=278)
puls_freq = Entry(window, width=8)
puls_freq.insert(0, '0')
puls_freq.place(x=250, y=278)
puls_freqB = Button(window, text='Set', bg='#f0f0f0')
puls_freqB.config(command=lambda : RC.LoopRunControll(key='4', dato=puls_freq.get()))
puls_freqB.place(x=310, y=275)
puls_offB = Button(window, text='OFF', bg='#f0f0f0')
puls_offB.config(command=lambda : RC.LoopRunControll(key='4', dato=0))
puls_offB.place(x=342, y=275)

Label(window, text='StartTag0:', bg=frame_bg).place(x=1, y=320)
Label(window, text='ns', bg=frame_bg).place(x=230, y=318)
Tag0_freq = Entry(window, width=8)
Tag0_freq.insert(0, '0')
Tag0_freq.place(x=250, y=318)
Tag0_freqB = Button(window, text='Set', bg='#f0f0f0')
Tag0_freqB.config(command=lambda : RC.LoopRunControll(key='5', dato=Tag0_freq.get()))
Tag0_freqB.place(x=310, y=315)

Label(window, text='Reset multychannel:', bg=frame_bg).place(x=1, y=360)
rst_multy = Button(window, text='Free', command=rst_multychannel, width=8)
rst_multy.place(x=250, y=358)

Label(window, text='PPS channel:', bg=frame_bg).place(x=1, y=400)
PPSchen = Button(window, text='Disabled', bg='red', relief=SUNKEN)
PPSchen.place(x=250, y=398)
PPSchen.config(command=lambda :endisButton(button=PPSchen, key='7'))

Label(window, text='Calibration:', bg=frame_bg).place(x=1, y=440)
calB = Button(window, text='NO', command=calib)
calB.place(x=250, y=438)

Label(window, text='CLK Automatic/Manual:', bg=frame_bg).place(x=1, y=480)
AMB = Button(window, text='Automatic', command=AM, width=8)
AMB.place(x=250, y=478)

Label(window, text='CLK External/Internal:', bg=frame_bg).place(x=1, y=520)
EIB = Button(window, text='Internal', command=EI)
EIB.place(x=250, y=518)

Label(window, text='Time to peak CH0 (min 20 ns):', bg=frame_bg).place(x=1, y=560)
Label(window, text='ns', bg=frame_bg).place(x=230, y=558)
peak0 = Entry(window, width=8)
peak0.insert(0, '120')
peak0.place(x=250, y=558)
peak0B = Button(window, text='Set', bg='#f0f0f0')
peak0B.config(command=lambda : RC.LoopRunControll(key='11', dato=peak0.get()))
peak0B.place(x=310, y=555)

Label(window, text='Time to peak CH1 (min 20 ns):', bg=frame_bg).place(x=1, y=600)
Label(window, text='ns', bg=frame_bg).place(x=230, y=598)
peak1 = Entry(window, width=8)
peak1.insert(0, '120')
peak1.place(x=250, y=598)
peak1B = Button(window, text='Set', bg='#f0f0f0')
peak1B.config(command=lambda : RC.LoopRunControll(key='12', dato=peak1.get()))
peak1B.place(x=310, y=595)

Label(window, text='TDC delay CH0 (max 1275 ns):', bg=frame_bg).place(x=1, y=640)
Label(window, text='ns', bg=frame_bg).place(x=230, y=638)
delay0 = Entry(window, width=8)
delay0.insert(0, '50')
delay0.place(x=250, y=638)
delay0B = Button(window, text='Set', bg='#f0f0f0')
delay0B.config(command=lambda : RC.LoopRunControll(key='13', dato=delay0.get()))
delay0B.place(x=310, y=635)

Label(window, text='TDC delay CH1 (max 1275 ns):', bg=frame_bg).place(x=1, y=680)
Label(window, text='ns', bg=frame_bg).place(x=230, y=678)
delay1 = Entry(window, width=8)
delay1.insert(0, '50')
delay1.place(x=250, y=678)
delay1B = Button(window, text='Set', bg='#f0f0f0')
delay1B.config(command=lambda : RC.LoopRunControll(key='14', dato=delay1.get()))
delay1B.place(x=310, y=675)

## Only read parameters
Label(window, text='Run Control parameters only read:', bg=frame_bg, font=('Helvetica', 14)).place(x=500, y=80)
Label(window, text='PPS count:', bg=frame_bg).place(x=500, y=120)
ppscount = Label(window, text='0', bg=frame_bg)
ppscount.place(x=730, y=120)
Label(window, text='Tag0:', bg=frame_bg).place(x=500, y=160)
Tag0ok = Label(window, text='OK', bg=frame_bg)
Tag0ok.place(x=730, y=160)
Label(window, text='Ratemeter CH0:', bg=frame_bg).place(x=500, y=200)
rate0 = Label(window, text='0', bg=frame_bg)
rate0.place(x=730, y=200)
Label(window, text='Ratemeter CH1:', bg=frame_bg).place(x=500, y=240)
rate1 = Label(window, text='0', bg=frame_bg)
rate1.place(x=730, y=240)
Label(window, text='Deadtime acq:', bg=frame_bg).place(x=500, y=280)
deadtime = Label(window, text='0 %', bg=frame_bg)
deadtime.place(x=730, y=280)
Label(window, text='FIFO full:', bg=frame_bg).place(x=500, y=320)
fifo = Label(window, text='FIFO ok', bg=frame_bg)
fifo.place(x=730, y=320)
Label(window, text='PLL:', bg=frame_bg).place(x=500, y=360)
pll = Label(window, text='Locked', bg=frame_bg)
pll.place(x=730, y=360)
Label(window, text='Overcurrent CH0:', bg=frame_bg).place(x=500, y=400)
ovc0 = Label(window, text='0', bg=frame_bg)
ovc0.place(x=730, y=400)
Label(window, text='Overcurrent CH1:', bg=frame_bg).place(x=500, y=440)
ovc1 = Label(window, text='0', bg=frame_bg)
ovc1.place(x=730, y=440)
Label(window, text='CLK state:', bg=frame_bg).place(x=500, y=480)
clkstate = Label(window, text='CLK OK', bg=frame_bg)
clkstate.place(x=730, y=480)

## Raccolta dati
Label(window, text='Acquisition:', bg=frame_bg, font=('Helvetica', 14)).place(x=500, y=520)

Label(window, text='Serial port for data:', bg=frame_bg).place(x=1, y=40)
Port_data = Entry(window)
Port_data.insert(0, 'COM7')
Port_data.place(x=150, y=40)

Label(window, text='Data to acquire:', bg=frame_bg).place(x=500, y=560)
acqEntry = Entry(window, width=8)
acqEntry.insert(0, '0')
acqEntry.place(x=730, y=560)

Label(window, text='File name:', bg=frame_bg).place(x=500, y=600)
nameEntry = Entry(window, width=15)
nameEntry.place(x=690, y=600)

acqB = Button(window, text='Start acquisition', width=40,
              command=lambda : acquisition(int(acqEntry.get()), Port_data.get(), nameEntry.get()))
acqB.place(x=500, y=680)
bar = ttk.Progressbar(window, orient=HORIZONTAL, mode='indeterminate', length=285)
bar.place(x=500, y=640)



window.mainloop()