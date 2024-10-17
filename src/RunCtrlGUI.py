from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk
from ComandiGui import RunControl
from ACQ_nexys import acquisitor
from tkinter import filedialog
from threading import *
from linearity import sweep
from hvmodbus import HVModbus
import time


def connect():
    RC.Port.porta = Port_rc.get()
    portvalue = RC.Port.Config()
    if portvalue:
        Connect_label.config(text='Connected', fg='#000000', bg='lightgreen')
    elif not portvalue:
        messagebox.showerror(title='ERROR', message='Serial not found')
    else:
        pass
    try:
        RC.LoopRead()
    except AttributeError:
        pass


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
        RC.LoopRunControll(key='6', dato='N')
    elif rst_multy.cget('text') == 'Resetted':
        rst_multy.config(text='Free', bg='#f0f0f0', relief=RAISED)
        RC.LoopRunControll(key='6', dato='Y')

def rst_FIFO():
    if FIFOrstB.cget('text') == 'Free':
        FIFOrstB.config(text='Resetted', bg='grey', relief=SUNKEN)
        RC.LoopRunControll(key='16', dato='D')
    elif FIFOrstB.cget('text') == 'Resetted':
        FIFOrstB.config(text='Free', bg='#f0f0f0', relief=RAISED)
        RC.LoopRunControll(key='16', dato='E')

def calib():
    RC.LoopRunControll(key='8', dato='Y')
    time.sleep(0.5)
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
    okbutton.config(command=lambda: RC.LoopRunControll(key='slog', dato=rateEntry.get(), name=nameEntry.get()))


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
    okbutton.config(command=lambda: RC.LoopRunControll(key='save', name=nameEntry.get()))


def openvalues():
    filepath = filedialog.askopenfilename(
        initialdir='C:/Users/alexa/PycharmProjects/Python_ACQ_tesi/NexysmPMT/RunCrtV3',
        filetypes=(('config_files', '*.cfg'), ('text_files', '*.txt'),
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
        rst_multy.config(text='Free', bg='#f0f0f0', relief=RAISED)
    elif RC.Rstch == 'Yes':
        rst_multy.config(text='Resetted', bg='grey', relief=SUNKEN)
    if RC.Pfreq == 0:
        puls_freq.delete(0, END)
        puls_freq.insert(0, '0')
    else:
        puls_freq.delete(0, END)
        puls_freq.insert(0, f'{RC.Pfreq}')
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
    timeout.delete(0, END)
    timeout.insert(0, RC.timeout)


def acquisition(porta, numevent, port, filename):
    AC = acquisitor(porta=porta, MaxEvent=numevent, port=port, filename=filename)
    try:
        AC.connect()
        AC.rst_fifo()
    except:
        return
    x = Thread(target=AC.nexysACQ, args=())
    x.start()
    checkhtread(x, acqbar)


def checkhtread(thread, bar):
    bar.start()
    if thread.is_alive():
        window.after(100, lambda: checkhtread(thread, bar))
    else:
        bar.stop()
        messagebox.showinfo(title='INFO', message='Measure ended')


def sweepamp():
    x = Thread(target=sweep, args=(int(minvalue.get()), int(maxvalue.get()), int(steps.get()), Port_data.get()))
    x.start()
    checkhtread(x, sweepbar)


def sweeppeakfunc():
    acq = acquisitor(1000, port=Port_data.get())
    minvalue, maxvalue, steps = int(minvaluep.get()), int(maxvaluep.get()), int(stepsp.get())
    acq.connect()
    for amp in range(minvalue, maxvalue + steps, steps):
        RC.LoopRunControll(key='11', dato=amp)
        acq.filename = f'peak_{amp / 1000}mV'
        acq.nexysACQ()
    acq.disconnect()


def sweeppeak():
    x = Thread(target=sweeppeakfunc, args=())
    x.start()
    checkhtread(x, sweepbar)


def connectFEB():
    global FEB
    FEB.open(serial=FEBport.get(), addr=int(FEBaddr.get()))
    month = Thread(target=monitorfeb, args=())
    month.start()


def setth():
    FEB.setThreshold(int(FEBth.get()))


def monitorfeb():
    global FEB
    while True:
        monregs = FEB.readMonRegisters()
        status = monregs['status']
        if status > 1:
            FEBonbutton.configure(state=DISABLED)
        else:
            FEBonbutton.configure(state=NORMAL)
        FEBv.delete(0, END)
        FEBv.insert(0, monregs['V'])
        FEBv.configure(foreground='red')
        FEBi.delete(0, END)
        FEBi.insert(0, monregs['I'])
        FEBi.configure(foreground='red')
        time.sleep(1)


def turnonFEB(button):
    global FEB
    if button.cget('text') == 'ON':
        button.config(text='OFF', bg='red', relief=SUNKEN)
        FEB.powerOff()
    elif button.cget('text') == 'OFF':
        button.config(text='ON', bg='#00b85b', relief=RAISED)
        FEB.powerOn()

FEB = HVModbus()

## Backgorund color
window_bg = '#c9c9c9'
frame_bg = '#d4d4d4'

## Window
window = Tk()
window.geometry('820x790')
window.title('Run Control Nexys')
window.resizable(False, False)
window.config(bg=window_bg)

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
fileMenu.add_command(label='Exit', command=lambda: quit())

logMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Log', menu=logMenu)
logMenu.add_command(label='Save logs', command=savelogs)

## Tabs
notebook = ttk.Notebook(window)
tab_main = Frame(notebook, bg=window_bg)
tab_measure = Frame(notebook, bg=window_bg)
notebook.add(tab_main, text='Main')
notebook.add(tab_measure, text='Measures')
notebook.pack(expand=True, fill='both')

##### MAIN TAB ########

## Frames
Frame(tab_main, bg=frame_bg, height=693, width=390).place(x=5, y=67)
Frame(tab_main, bg=frame_bg, height=450, width=330).place(x=480, y=67)
Frame(tab_main, bg=frame_bg, height=240, width=330).place(x=480, y=520)

## Serial connection
Label(tab_main, text='Serial port for Run Control: ', bg=window_bg).place(x=25, y=10)
Port_rc = Entry(tab_main)
Port_rc.insert(0, 'COM6')
Port_rc.place(x=175, y=10)
Button(tab_main, text='Connect', command=connect).place(x=305, y=8)
Connect_label = Label(tab_main, width=15, text='Not connected', bg='red')
Connect_label.place(x=375, y=10)

Label(tab_main, text='Serial port for data:', bg=window_bg).place(x=25, y=40)
Port_data = Entry(tab_main)
Port_data.insert(0, 'COM7')
Port_data.place(x=175, y=40)

RC = RunControl()

## Refresh button
Refresh = Button(tab_main, text='Refresh parameters', command=readvalues, width=25)
Refresh.place(x=550, y=10)

## Run control parameters
Label(tab_main, text='Run Control parameters to set:', bg=frame_bg, font=('Helvetica', 14)).place(x=25, y=80)

Label(tab_main, text='Power enable CH0:', bg=frame_bg).place(x=25, y=120)
pw_en0 = Button(tab_main, text='Enabled', bg='#00b85b')
pw_en0.config(command=lambda: endisButton(button=pw_en0, key='0'))
pw_en0.place(x=250, y=118)

Label(tab_main, text='Power enable CH1:', bg=frame_bg).place(x=25, y=160)
pw_en1 = Button(tab_main, text='Enabled', bg='#00b85b')
pw_en1.place(x=250, y=158)
pw_en1.config(command=lambda: endisButton(button=pw_en1, key='1'))

Label(tab_main, text='Acq enable CH0:', bg=frame_bg).place(x=25, y=200)
acq_en0 = Button(tab_main, text='Enabled', bg='#00b85b')
acq_en0.place(x=250, y=198)
acq_en0.config(command=lambda: endisButton(button=acq_en0, key='2'))

Label(tab_main, text='Acq enable CH1:', bg=frame_bg).place(x=25, y=240)
acq_en1 = Button(tab_main, text='Enabled', bg='#00b85b')
acq_en1.place(x=250, y=238)
acq_en1.config(command=lambda: endisButton(button=acq_en1, key='3'))

Label(tab_main, text='Pulser frequency:', bg=frame_bg).place(x=25, y=280)
Label(tab_main, text='Hz', bg=frame_bg).place(x=230, y=278)
puls_freq = Entry(tab_main, width=8)
puls_freq.insert(0, '0')
puls_freq.place(x=250, y=278)
puls_freqB = Button(tab_main, text='Set', bg='#f0f0f0')
puls_freqB.config(command=lambda: RC.LoopRunControll(key='4', dato=puls_freq.get()))
puls_freqB.place(x=310, y=275)
puls_offB = Button(tab_main, text='OFF', bg='#f0f0f0')
puls_offB.config(command=lambda: RC.LoopRunControll(key='4', dato=0))
puls_offB.place(x=342, y=275)

Label(tab_main, text='StartTag0:', bg=frame_bg).place(x=25, y=320)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=318)
Tag0_freq = Entry(tab_main, width=8)
Tag0_freq.insert(0, '0')
Tag0_freq.place(x=250, y=318)
Tag0_freqB = Button(tab_main, text='Set', bg='#f0f0f0')
Tag0_freqB.config(command=lambda: RC.LoopRunControll(key='5', dato=Tag0_freq.get()))
Tag0_freqB.place(x=310, y=315)

Label(tab_main, text='Reset multychannel:', bg=frame_bg).place(x=25, y=360)
rst_multy = Button(tab_main, text='Free', command=rst_multychannel, width=8)
rst_multy.place(x=250, y=358)

Label(tab_main, text='PPS channel:', bg=frame_bg).place(x=25, y=400)
PPSchen = Button(tab_main, text='Disabled', bg='red', relief=SUNKEN)
PPSchen.place(x=250, y=398)
PPSchen.config(command=lambda: endisButton(button=PPSchen, key='7'))

Label(tab_main, text='Calibration:', bg=frame_bg).place(x=25, y=440)
calB = Button(tab_main, text='Do calibration', command=calib)
calB.place(x=250, y=438)

Label(tab_main, text='CLK Automatic/Manual:', bg=frame_bg).place(x=25, y=480)
AMB = Button(tab_main, text='Automatic', command=AM, width=8)
AMB.place(x=250, y=478)

Label(tab_main, text='CLK External/Internal:', bg=frame_bg).place(x=25, y=520)
EIB = Button(tab_main, text='Internal', command=EI)
EIB.place(x=250, y=518)

Label(tab_main, text='Time to peak CH0 (min 20 ns):', bg=frame_bg).place(x=25, y=560)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=558)
peak0 = Entry(tab_main, width=8)
peak0.insert(0, '115')
peak0.place(x=250, y=558)
peak0B = Button(tab_main, text='Set', bg='#f0f0f0')
peak0B.config(command=lambda: RC.LoopRunControll(key='11', dato=peak0.get()))
peak0B.place(x=310, y=555)

Label(tab_main, text='Time to peak CH1 (min 20 ns):', bg=frame_bg).place(x=25, y=600)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=598)
peak1 = Entry(tab_main, width=8)
peak1.insert(0, '115')
peak1.place(x=250, y=598)
peak1B = Button(tab_main, text='Set', bg='#f0f0f0')
peak1B.config(command=lambda: RC.LoopRunControll(key='12', dato=peak1.get()))
peak1B.place(x=310, y=595)

Label(tab_main, text='TDC delay CH0 (125 to 1275 ns):', bg=frame_bg).place(x=25, y=640)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=638)
delay0 = Entry(tab_main, width=8)
delay0.insert(0, '50')
delay0.place(x=250, y=638)
delay0B = Button(tab_main, text='Set', bg='#f0f0f0')
delay0B.config(command=lambda: RC.LoopRunControll(key='13', dato=delay0.get()))
delay0B.place(x=310, y=635)

Label(tab_main, text='TDC delay CH1 (125 to 1275 ns):', bg=frame_bg).place(x=25, y=680)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=678)
delay1 = Entry(tab_main, width=8)
delay1.insert(0, '50')
delay1.place(x=250, y=678)
delay1B = Button(tab_main, text='Set', bg='#f0f0f0')
delay1B.config(command=lambda: RC.LoopRunControll(key='14', dato=delay1.get()))
delay1B.place(x=310, y=675)

Label(tab_main, text='Round robin timeout (max 2555 ns):', bg=frame_bg).place(x=25, y=720)
Label(tab_main, text='ns', bg=frame_bg).place(x=230, y=718)
timoutB = Button(tab_main, text='Set')
timoutB.config(command=lambda: RC.LoopRunControll(key='15', dato=timeout.get()))
timoutB.place(x=310, y=715)
timeout = Entry(tab_main, width=8)
timeout.insert(0, '1000')
timeout.place(x=250, y=718)

## Only read parameters
Label(tab_main, text='Run Control parameters only read:', bg=frame_bg, font=('Helvetica', 14)).place(x=500, y=80)

Label(tab_main, text='PPS count:', bg=frame_bg).place(x=500, y=120)
ppscount = Label(tab_main, text='0', bg=frame_bg)
ppscount.place(x=730, y=120)

Label(tab_main, text='Tag0:', bg=frame_bg).place(x=500, y=160)
Tag0ok = Label(tab_main, text='OK', bg=frame_bg)
Tag0ok.place(x=730, y=160)

Label(tab_main, text='Ratemeter CH0:', bg=frame_bg).place(x=500, y=200)
rate0 = Label(tab_main, text='0', bg=frame_bg)
rate0.place(x=730, y=200)

Label(tab_main, text='Ratemeter CH1:', bg=frame_bg).place(x=500, y=240)
rate1 = Label(tab_main, text='0', bg=frame_bg)
rate1.place(x=730, y=240)

Label(tab_main, text='Deadtime acq:', bg=frame_bg).place(x=500, y=280)
deadtime = Label(tab_main, text='0 %', bg=frame_bg)
deadtime.place(x=730, y=280)

Label(tab_main, text='FIFO full:', bg=frame_bg).place(x=500, y=320)
FIFOrstB = Button(tab_main, text='Free', command=rst_FIFO, width=8)
FIFOrstB.place(x=660, y=318)
fifo = Label(tab_main, text='NOT Full', bg=frame_bg)
fifo.place(x=730, y=320)

Label(tab_main, text='PLL:', bg=frame_bg).place(x=500, y=360)
pll = Label(tab_main, text='Locked', bg=frame_bg)
pll.place(x=730, y=360)

Label(tab_main, text='Overcurrent CH0:', bg=frame_bg).place(x=500, y=400)
ovc0 = Label(tab_main, text='OK', bg=frame_bg)
ovc0.place(x=730, y=400)

Label(tab_main, text='Overcurrent CH1:', bg=frame_bg).place(x=500, y=440)
ovc1 = Label(tab_main, text='OK', bg=frame_bg)
ovc1.place(x=730, y=440)

Label(tab_main, text='CLK state:', bg=frame_bg).place(x=500, y=480)
clkstate = Label(tab_main, text='CLK OK', bg=frame_bg)
clkstate.place(x=730, y=480)

## Feb connection
Label(tab_main, text='FEB', bg=frame_bg, font=('Helvetica', 14)).place(x=500, y=530)

Label(tab_main, text='Address:', bg=frame_bg).place(x=500, y=570)
FEBaddr = Entry(tab_main, width=8)
FEBaddr.insert(0, '20')
FEBaddr.place(x=680, y=570)
FEBbutton = Button(tab_main, text='Connect', command=connectFEB)
FEBbutton.place(x=745, y=567)

Label(tab_main, text='Serial port:', bg=frame_bg).place(x=500, y=610)
FEBport = Entry(tab_main, width=8)
FEBport.insert(0, 'COM4')
FEBport.place(x=680, y=610)

Label(tab_main, text='Threshold:', bg=frame_bg).place(x=500, y=650)
Label(tab_main, text='mV', bg=frame_bg).place(x=650, y=650)
FEBth = Entry(tab_main, width=8)
FEBth.insert(0, '70')
FEBth.place(x=680, y=650)
FEBthbutton = Button(tab_main, text='Set', command=setth)
FEBthbutton.place(x=745, y=647)

Label(tab_main, text='Monitoring:', bg=frame_bg).place(x=500, y=690)
Label(tab_main, text='V', bg=frame_bg).place(x=672, y=690)
Label(tab_main, text='μA', bg=frame_bg).place(x=772, y=690)
FEBv = Entry(tab_main, width=8)
FEBv.insert(0, '0')
FEBv.place(x=620, y=690)
FEBi = Entry(tab_main, width=8)
FEBi.insert(0, '0')
FEBi.place(x=720, y=690)

Label(tab_main, text='Set HV:', bg=frame_bg).place(x=500, y=730)
FEBvset = Entry(tab_main, width=8)
FEBvset.insert(0, '0')
FEBvset.place(x=580, y=730)
FEBvsetbutton = Button(tab_main, text='Set', command=lambda: FEB.setVoltageSet(int(FEBvset.get())))
FEBvsetbutton.place(x=640, y=727)
FEBonbutton = Button(tab_main, width=10, command=lambda: turnonFEB(FEBonbutton))
FEBonbutton.place(x=700, y=727)
FEBonbutton.config(text='OFF', bg='red', relief=SUNKEN)

##### TAB MEASURES ########
Label(tab_measure, text='Amplitude sweep', bg=window_bg, font=('Helvetica', 14)).place(x=25, y=10)
Label(tab_measure, text='Min value: ', bg=window_bg).place(x=25, y=50)
Label(tab_measure, text='mV', bg=window_bg).place(x=100, y=50)
minvalue = Entry(tab_measure, width=8)
minvalue.place(x=125, y=50)

Label(tab_measure, text='Max value: ', bg=window_bg).place(x=25, y=90)
Label(tab_measure, text='mV', bg=window_bg).place(x=100, y=90)
maxvalue = Entry(tab_measure, width=8)
maxvalue.place(x=125, y=90)

Label(tab_measure, text='Steps: ', bg=window_bg).place(x=25, y=130)
Label(tab_measure, text='mV', bg=window_bg).place(x=100, y=130)
steps = Entry(tab_measure, width=8)
steps.place(x=125, y=130)

sweepB = Button(tab_measure, text='Sart amp', width=20, command=sweepamp)
sweepB.place(x=25, y=170)

sweepbar = ttk.Progressbar(tab_measure, orient=HORIZONTAL, mode='indeterminate', length=350)
sweepbar.place(x=25, y=210)

Label(tab_measure, text='Time to peak sweep', bg=window_bg, font=('Helvetica', 14)).place(x=200, y=10)
Label(tab_measure, text='Min value: ', bg=window_bg).place(x=200, y=50)
Label(tab_measure, text='ns', bg=window_bg).place(x=275, y=50)
minvaluep = Entry(tab_measure, width=11)
minvaluep.place(x=300, y=50)

Label(tab_measure, text='Max value: ', bg=window_bg).place(x=200, y=90)
Label(tab_measure, text='ns', bg=window_bg).place(x=275, y=90)
maxvaluep = Entry(tab_measure, width=11)
maxvaluep.place(x=300, y=90)

Label(tab_measure, text='Steps: ', bg=window_bg).place(x=200, y=130)
Label(tab_measure, text='ns', bg=window_bg).place(x=275, y=130)
stepsp = Entry(tab_measure, width=11)
stepsp.place(x=300, y=130)

sweeppB = Button(tab_measure, text='Sart peak', width=23, command=sweeppeak)
sweeppB.place(x=200, y=170)

## Raccolta dati
Label(tab_measure, text='Acquisition:', bg=window_bg, font=('Helvetica', 14)).place(x=500, y=10)

Label(tab_measure, text='Data to acquire:', bg=window_bg).place(x=500, y=50)
acqEntry = Entry(tab_measure, width=8)
acqEntry.insert(0, '0')
acqEntry.place(x=730, y=50)

Label(tab_measure, text='File name:', bg=window_bg).place(x=500, y=90)
nameEntry = Entry(tab_measure, width=15)
nameEntry.place(x=690, y=90)

acqB = Button(tab_measure, text='Start acquisition', width=40,
              command=lambda: acquisition(Port_rc.get(), int(acqEntry.get()), Port_data.get(), nameEntry.get()))
acqB.place(x=500, y=130)
acqbar = ttk.Progressbar(tab_measure, orient=HORIZONTAL, mode='indeterminate', length=285)
acqbar.place(x=500, y=170)

window.mainloop()
