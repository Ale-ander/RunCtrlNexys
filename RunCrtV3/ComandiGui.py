#!/usr/bin/python

"""
File : ListaCMD.py
Author: SER
Data  : 03/11/2021
Version : 3.0
"""


from typing import Match
from AppSerialPortV1 import COMPort
import configparser

import sys
import time
from pytimedinput import timedKey


# ---------------------
class RunControl:
    def __init__(self, comport='COM1'):
        self.comport = comport
        self.Port = COMPort(porta=self.comport)
        self.count = 0
        self.Config()
    # - Ogetti usati


    def Config(self):
        # Variabile per il menu di stampa
        self.Overcurrent0 = 0
        self.Overcurrent1 = 0
        self.Poweren0 = "Enable"
        self.Poweren1 = "Enable"
        self.Acqen0 = "Enable"
        self.Acqen1 = "Enable"
        self.PPScount = 0
        self.Pfreq = "OFF"
        self.Starttag0 = 0
        self.Rstch = 0
        self.PPSchen = "Enable"
        self.Calibflag = "Yes"
        self.Clkextin = "Interno"
        self.Clkautman = "Automatico"
        self.Peak0 = 24    # Time to peak
        self.Peak1 = 24    # Time to peak
        self.Delay0 = 10   # TDC delay
        self.Delay1 = 10   # TDC delay
        self.PLL = "Locked" # PLl locked
        self.Fifo = "Empty" #Global FIFO full
        self.FreCh0 = 0   # Ratemeter
        self.FreCh1 = 0   # Ratemeter
        self.TempoMorto = 0 # Deadtime total
        self.Clkreg = "CLK OK"  # Clk found, lost, ok
        self.Tag_0ok = "OK" # Tag_0

        # Variabili che contengono lo stato localmente
        self.PowerEnable = 0xffff
        self.AcqEnable = 0xffff
        self.Misc = 0x0000
        self.CLKsafe = 0x0000

        #-- Elenco indirizzi di letture
        self.addrElenco = { "OverCurrent": 1, # overcurrent flag
                            "PwrEn": 2,       # bit0 = powenable Ch0 e bit1 = powenable Ch1
                            "ChEn": 4,        # bit0 = acqenable Ch0 e bit1 = acqenable Ch1
                            "PPSCount": 6,    # seconds from power on
                            "PFreq": 7,       # pulser frequency in ms
                            "StartTag0": 8,   # start value of the @200MHz counter
                            "Misc": 9,        # bit0 = PLLlock, bit1 = unused, bit2 = reset multychannel,
                                              # bit3 = enable pps channel, bit4 = calibration flag, bit5 = full global fifo
                            "CLKreg": 10,     # bit0 = CLK FOUND, bit1 = CLK LOST , bit2 = CLK OK
                            "CLKmux": 11,     # bit0 = external/internale CLK, bit1 = automatic/manual CLK
                            "Tag0_ok": 12,    # bit0 = Tag_0 OK, bit1 = unused
                            "Rate_ch0": 13,   # ratemeter channel 0
                            "Rate_ch1": 14,   # ratemeter channel 1
                            "Deadtime": 32,   # total deadtime
                            "Peak_ch0": 33,   # time to peak channel 0
                            "Peak_ch1": 34,   # time to peak channel 1
                            "Delay_ch0": 52,  # delay channel 0
                            "Delay_ch1": 53,  # delay channel 1
                            }
        #-- Elenco letture  non usata                 
        self.DatiLetture =self.addrElenco.copy()
    """ Lettura parametri:
        Seguenza di invio dei comandi.
        Per aggiornare la schermata di visualizzazione
    """
    def LoopRead(self):
        for x in range(0,len(self.addrElenco)):
            v = list(self.DatiLetture.items())[x][1]        # indirizzo del comando dal dizionario
            Comando = list(self.DatiLetture.items())[x][0]  # Nome del comando dal dizionario

            dati = self.Port.Send_CMD(v,-1)                 # legge l'indirizzo v

            self.EstrazioneParametri(Comando,dati)
    """
        Gestione Tastiera:
        Ciclo di attesa comandi dalla tastiera
    """
    def LoopRunControll(self, key='', dato='', name=''):
            #--- Selezione CMD 0
            if key == '0':
                if dato  == "D":
                    self.PowerEnable =  self.PowerEnable & 0xfffe
                elif dato  == "E":
                    self.PowerEnable =  self.PowerEnable | 0x0001
                self.Port.Send_CMD(2, self.PowerEnable)
            #--- Selezione CMD 1
            elif key == '1':
                if dato  == "D":
                    self.PowerEnable =  self.PowerEnable & 0xfffd
                elif dato  == "E":
                    self.PowerEnable =  self.PowerEnable | 0x0002
                self.Port.Send_CMD(2,self.PowerEnable)
            #--- Selezione CMD 2
            elif key == '2':
                if dato  == "D":
                    self.AcqEnable =  self.AcqEnable & 0xfffe
                elif dato  == "E":
                    self.AcqEnable =  self.AcqEnable | 0x0001
                self.Port.Send_CMD(4,self.AcqEnable)
            #--- Selezione CMD 3
            elif key == '3':
                if dato  == "D":
                    self.AcqEnable =  self.AcqEnable & 0xfffd
                elif dato  == "E":
                    self.AcqEnable =  self.AcqEnable | 0x0002
                self.Port.Send_CMD(4,self.AcqEnable)
            #--- Selezione CMD 4
            elif key == '4':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 0.0
                    pass
                if fdato <= 1000 and fdato != 0:
                    self.Pulser = int(1000/fdato)
                elif fdato == 0:
                    self.Pulser = 0
                self.Port.Send_CMD(0x07,self.Pulser)
            #--- Selezione CMD 5
            elif key == '5':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 0.0
                    pass
                if (fdato <= 1000) and (fdato>0.007):
                    self.Starttag0 = int(fdato/5)
                elif fdato == 0:
                    self.Starttag0 = 0
                self.Port.Send_CMD(0x08,self.Starttag0)
            #---- Selezione CMD 6
            elif key == '6':
                if dato  == "Y":
                    self.Misc =  self.Misc | 0x0004
                elif dato  == "N":
                    self.Misc =  self.Misc & 0x000b
                self.Port.Send_CMD(9,self.Misc)
            #---- Selezione CMD 7
            elif key == '7':
                if dato  == "E":
                    self.Misc =  self.Misc | 0x0008
                elif dato  == "D":
                    self.Misc =  self.Misc & 0x0007
                self.Port.Send_CMD(9,self.Misc)
            #---- Selezione CMD 8
            elif key == '8':
                if dato  == "Y":
                    self.Misc =  self.Misc | 0x0010
                elif dato  == "N":
                    self.Misc =  self.Misc & 0x000f
                self.Port.Send_CMD(9,self.Misc)
            #---- Selezione CMD 9
            elif key == '9':
                if dato  == "A":
                    self.CLKsafe =  self.CLKsafe | 0x0002
                elif dato  == "M":
                    self.CLKsafe =  self.CLKsafe & 0x0001
                self.Port.Send_CMD(11,self.CLKsafe)
            #---- Selezione CMD 10
            elif key == '10':
                if dato  == "E":
                    self.CLKsafe =  self.CLKsafe | 0x0001
                elif dato  == "I":
                    self.CLKsafe =  self.CLKsafe & 0x0002
                self.Port.Send_CMD(11,self.CLKsafe)
            #---- Selezione CMD 11
            elif key == '11':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 24
                    pass
                if fdato >= 20:
                    self.Peak0 = int(fdato/5)
                else:
                    self.Peak0 = 24
                self.Port.Send_CMD(0x21,self.Peak0)
            #---- Selezione CMD 12
            elif key == '12':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 24
                    pass
                if fdato >= 20:
                    self.Peak1 = int(fdato/5)
                else:
                    self.Peak1 = 24
                self.Port.Send_CMD(0x22,self.Peak1)
            #---- Selezione CMD 13
            elif key == '13':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 35.0
                    pass
                if fdato <= 1275:
                    self.Delay0 = int(fdato/5)
                else:
                    self.Delay0 = 10
                self.Port.Send_CMD(0x34,self.Delay0)
            #---- Selezione CMD 14
            elif key == '14':
                try:
                    fdato = float(dato)
                except ValueError:
                    fdato = 35.0
                    pass
                if fdato <= 1275:
                    self.Delay1 = int(fdato/5)
                else:
                    self.Delay1 = 10
                self.Port.Send_CMD(0x35,self.Delay1)
            # Salvataggio dati
            elif key == 'slog':
                    Save_Rate = int(dato)
                    folder = "log/"
                    timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
                    Save_Nome_File = folder + name + "_" + timestr + ".csv"
                    f = open(Save_Nome_File, "w")
                    f.write("Time,Freq_CH0,Freq_CH1,DeadTime,FifoFull\n")
                    f.close()
                    self.count = 0
                    while self.count != Save_Rate:
                        self.LoopRead()
                        f = open(Save_Nome_File, "a")
                        f.write(str(time.strftime("%Y_%m_%d-%H_%M_%S")) + "," + \
                            str(self.FreCh0) + "," + str(self.FreCh1) + "," + \
                            str(self.TempoMorto) + "," + str(self.Fifo)+ "\n")
                        f.close()
                        self.count += 1
                        time.sleep(1)
                #salvataggio configurazione
            elif key == 'save':
                folder = './'
                Save_Nome_File = folder + name + ".cfg"
                config = configparser.ConfigParser()
                config['DEFAULT'] = {
                    'Pwen0' : self.Poweren0,
                    'Pwen1' : self.Poweren1,
                    'Acqen0' : self.Acqen0,
                    'Acqen1' : self.Acqen1,
                    'Pulsfreq' : self.Pfreq,
                    'StartTag0' : self.Starttag0,
                    'Rstmulty' : self.Rstch,
                    'PPSchen' : self.PPSchen,
                    'Calibration' : self.Calibflag,
                    'CLK A/M' : self.Clkautman,
                    'CLK E/I' : self.Clkextin,
                    'Peak0' : self.Peak0,
                    'Peak1' : self.Peak1,
                    'Delay0' : self.Delay0,
                    'Delay1' : self.Delay1
                }
                with open(Save_Nome_File, 'w') as configfile:
                    config.write(configfile)
            elif key == 'open':
                config = configparser.ConfigParser()
                config.read(name)

                if config['DEFAULT']['pwen0'] == 'Enabled':
                    self.PowerEnable =  self.PowerEnable | 0x0001
                elif config['DEFAULT']['pwen0'] == 'Disabled':
                    self.PowerEnable =  self.PowerEnable & 0xfffe
                if config['DEFAULT']['pwen1'] == 'Enabled':
                    self.PowerEnable =  self.PowerEnable | 0x0002
                elif config['DEFAULT']['pwen1'] == 'Disabled':
                    self.PowerEnable =  self.PowerEnable & 0xfffd
                self.Port.Send_CMD(2, self.PowerEnable)

                if config['DEFAULT']['acqen0'] == 'Enabled':
                    self.PowerEnable = self.PowerEnable | 0x0001
                elif config['DEFAULT']['acqen0'] == 'Disabled':
                    self.PowerEnable = self.PowerEnable & 0xfffe
                if config['DEFAULT']['acqen1'] == 'Enabled':
                    self.PowerEnable = self.PowerEnable | 0x0002
                elif config['DEFAULT']['acqen1'] == 'Disabled':
                    self.PowerEnable = self.PowerEnable & 0xfffd
                self.Port.Send_CMD(4, self.PowerEnable)

                pulserfrequenza = float(config['DEFAULT']['Pulsfreq'].split(" ")[0])

                if pulserfrequenza <= 1000 and pulserfrequenza != 0:
                    self.Pulser = int(1000/pulserfrequenza)
                elif pulserfrequenza == 0:
                    self.Pulser = 0
                self.Port.Send_CMD(0x07,self.Pulser)

                if int(config['DEFAULT']['StartTag0']) <= 1000:
                    self.Starttag0 = int(int(config['DEFAULT']['StartTag0'])/5)
                elif int(config['DEFAULT']['StartTag0']) == 0:
                    self.Starttag0 = 0
                self.Port.Send_CMD(0x08,self.Starttag0)

                if config['DEFAULT']['Rstmulty']  == "Yes":
                    self.Misc =  self.Misc | 0x0004
                elif config['DEFAULT']['Rstmulty']  == "N0":
                    self.Misc =  self.Misc & 0x000b
                self.Port.Send_CMD(9,self.Misc)

                if config['DEFAULT']['PPSchen']  == "Enabled":
                    self.Misc =  self.Misc | 0x0008
                elif config['DEFAULT']['PPSchen']  == "Disabled":
                    self.Misc =  self.Misc & 0x0007
                self.Port.Send_CMD(9,self.Misc)

                if config['DEFAULT']['Calibration']  == "Yes":
                    self.Misc =  self.Misc | 0x0010
                elif config['DEFAULT']['Calibration']  == "No":
                    self.Misc =  self.Misc & 0x000f
                self.Port.Send_CMD(9,self.Misc)

                if config['DEFAULT']['CLK A/M']  == "Automatic":
                    self.CLKsafe =  self.CLKsafe | 0x0002
                elif config['DEFAULT']['CLK A/M']  == "Manual":
                    self.CLKsafe =  self.CLKsafe & 0x0001
                self.Port.Send_CMD(11,self.CLKsafe)

                if dato  == "External":
                    self.CLKsafe =  self.CLKsafe | 0x0001
                elif dato  == "Internal":
                    self.CLKsafe =  self.CLKsafe & 0x0002
                self.Port.Send_CMD(11,self.CLKsafe)

                if int(config['DEFAULT']['Peak0']) >= 20:
                    self.Peak0 = int(int(config['DEFAULT']['Peak0'])/5)
                else:
                    self.Peak0 = 24
                self.Port.Send_CMD(0x21,self.Peak0)

                if int(config['DEFAULT']['Peak1']) >= 20:
                    self.Peak1 = int(int(config['DEFAULT']['Peak1'])/5)
                else:
                    self.Peak1 = 24
                self.Port.Send_CMD(0x22,self.Peak1)

                if int(config['DEFAULT']['Delay0']) <= 1275:
                    self.Delay0 = int(int(config['DEFAULT']['Delay0'])/5)
                else:
                    self.Delay0 = 10
                self.Port.Send_CMD(0x34,self.Delay1)

                if int(config['DEFAULT']['Delay1']) <= 1275:
                    self.Delay1 = int(int(config['DEFAULT']['Delay1'])/5)
                else:
                    self.Delay1 = 10
                self.Port.Send_CMD(0x35,self.Delay1)
            else:
                print('Key Value Error!!!!!')
    """
        Estrae le informazioni dai valori letti
        con la seriale
    """
    def EstrazioneParametri(self,Cmd,Valore):
         # - codifica cmd PwrEn
        if list(self.DatiLetture.items())[0][0] == Cmd :
            binNum = '{0:16b}'.format(int(Valore))
            if binNum[15] == "0":
                self.Overcurrent0 = 0
            elif binNum[15] == "1":
                self.Overcurrent0 = 1
            else:
                pass

            if binNum[14] == "0":
                self.Overcurrent1 = 0
            elif binNum[14] == "1":
                self.Overcurrent1 = 1
            else:
                pass

         # - codifica cmd PwrEn
        elif list(self.DatiLetture.items())[1][0] == Cmd :
            binNum = '{0:16b}'.format(int(Valore))
            if binNum[15] == "0":
                self.Poweren0 = "Disabled"
            elif binNum[15] == "1":
                self.Poweren0 = "Enabled"
            else:
                pass

            if binNum[14] == "0":
                self.Poweren1 = "Disabled"
            elif binNum[14] == "1":
                self.Poweren1 = "Enabled"
            else:
                pass

        # - codifica cmd ChEn
        elif list(self.DatiLetture.items())[2][0] == Cmd:
            binNum = '{0:16b}'.format(int(Valore))
            if binNum[15] == "0":
                self.Acqen0 = "Disabled"
            elif binNum[15] == "1":
                self.Acqen0 = "Enabled"
            else:
                pass

            if binNum[14] == "0":
                self.Acqen1 = "Disabled"
            elif binNum[14] == "1":
                self.Acqen1 = "Enabled"
            else:
                pass

        # - codifica PPS contati
        elif list(self.DatiLetture.items())[3][0] == Cmd:
            intNum = int(Valore)
            self.PPScount = intNum

        # - codifica frequenza pulser
        elif list(self.DatiLetture.items())[4][0] == Cmd :
            intNum = int(Valore)
            if intNum == 0:
                self.Pfreq = "OFF"
            else:
               self.Pfreq = '{} Hz'.format(1000/intNum)

        # - codifica start @200MHz counter
        elif list(self.DatiLetture.items())[5][0] == Cmd:
            intNum = int(Valore*5)
            self.Starttag0 = intNum

        # - codifica cmd Misc
        elif list(self.DatiLetture.items())[6][0] == Cmd:
            binNum = '{0:06b}'.format(int(Valore))
            if binNum[5] == "0":
                self.PLL = "Error"
            elif binNum[5] == "1":
                self.PLL = "Locked"
            else:
                pass

            if binNum[3] == "0":
                self.Rstch = "No"
            elif binNum[3] == "1":
                self.Rstch = "Yes"
            else:
                pass

            if binNum[2] == "0":
                self.PPSchen = "Disabled"
            elif binNum[2] == "1":
                self.PPSchen = "Enabled"
            else:
                pass

            if binNum[1] == "0":
                self.Calibflag = "No"
            elif binNum[1] == "1":
                self.Calibflag = "Yes"
            else:
                pass

            if binNum[0] == "0":
                self.Fifo = "FIFO ok"
            elif binNum[0] == "1":
                self.Fifo = "FIFO full"
            else:
                pass

        # - codifica cmd CLK reg
        elif list(self.DatiLetture.items())[7][0] == Cmd:
            binNum = '{0:03b}'.format(int(Valore))
            if binNum[2:0] == "001":
                self.CLKreg = "CLK Found"
            elif binNum[2:0] == "010":
                self.CLKreg = "CLK Lost"
            elif binNum[2:0] == "100":
                self.CLKreg = "CLK OK"
            else:
                pass

        # - codifica cmd CLK mux
        elif list(self.DatiLetture.items())[8][0] == Cmd:
            binNum = '{0:02b}'.format(int(Valore))
            if binNum[1] == "0":
                self.Clkextin = "CLK Internal"
            elif binNum[1] == "1":
                self.Clkextin = "CLK External"
            else:
                pass

            if binNum[0] == "0":
                self.Clkautman = "CLK Manual"
            elif binNum[0] == "1":
                self.Clkautman = "CLK Automatic"
            else:
                pass

        # - codifica cmd Tag_0
        elif list(self.DatiLetture.items())[9][0] == Cmd:
            binNum = bin(int(Valore))
            if binNum[0] == "1":
                self.Tag_0ok = "Bho"
            elif binNum[0] == "0":
                self.Tag_0ok = "Bho"
            else:
                pass

        # - codifica cmd FREQ_CH0 ricevuto
        elif list(self.DatiLetture.items())[10][0] == Cmd :
            intNum = int(Valore)
            if intNum <0XFFFE:
                self.FreCh0 = intNum
            elif intNum == 0XFFFE :
                self.FreCh0 = "ALERT! Overflow"
            else:
                self.FreCh0 = "ALERT! threshold too low"

        # - codifica cmd FREQ_CH1 ricevuto
        elif list(self.DatiLetture.items())[11][0] == Cmd : #
            intNum = int(Valore)
            if intNum <0XFFFE:
                self.FreCh1 = intNum
            elif intNum == 0XFFFE :
                self.FreCh1 = "ALERT! Overflow"
            else:
                self.FreCh1 = "ALERT! threshold too low"
        
        # - codifica cmd Picco ch0 ricevuto
        elif list(self.DatiLetture.items())[13][0] == Cmd :
            intNum = int(Valore)
            self.Peak0 = intNum*5

        # - codifica cmd Picco ch1 ricevuto
        elif list(self.DatiLetture.items())[14][0] == Cmd:
            intNum = int(Valore)
            self.Peak1 = intNum * 5

        # - codifica cmd TempoMorto ricevuto
        elif list(self.DatiLetture.items())[12][0] == Cmd:
            intNum = int(Valore)
            a = 100 - (100 * (intNum / 48829))
            self.TempoMorto = '{:.2f}'.format(a)

        # - codifica cmd Delay ch ricevuto
        elif list(self.DatiLetture.items())[15][0] == Cmd:
            intNum = int(Valore)
            self.Delay0 = intNum * 5

        # - codifica cmd Delay ch1 ricevuto
        elif list(self.DatiLetture.items())[16][0] == Cmd:
            intNum = int(Valore)
            self.Delay1 = intNum * 5

         # - altrimenti (se non è negativo)
        else:
            pass
