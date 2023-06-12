import numpy as np
import serial
import time
import csv
import CRC32
from tkinter import *

class acquisitor:

    def __init__(self, MaxEvent=100, port='COM7', filename='test' ):
        self.MaxEvent = MaxEvent
        self.port = port
        self.filename = filename
        self.NumEvent = 0

    def nexysACQ(self):
        STATUS = 0
        data_s = ""

        single_event = []  # this array contains data in raw format, as read from the serial port. It is reset event by event.
        buffer_array = []  # this array contains all the information of the event (channel, energy, event time, acquisition time). It is reset event by event.
        buffer_matrix = []  # this matrix is filled with a maximum of 100 buffer_array,then it's written on a file and reset.

        Time_c_old = 0

        #### open serial port ####
        ser = serial.Serial(self.port, 921600)

        #### create the output file ####

        folder = "C:/Users/alexa\PycharmProjects\Python_ACQ_tesi/NexysmPMT/run_new/"
        timestr = time.strftime("%Y_%m_%d-")
        file_name = folder + timestr + '_' + self.filename + '.csv'

        with open(file_name, 'w') as outFile:
            writer = csv.writer(outFile)
            header = ["Channel", "Event type", "Energy HG", "Energy LG", "ToT Coarse", "ToT fine", "ToT", "Time Coarse", "Time fine",
                      "Event time (ns)", 'Delta_time', "Acquisition time", "Date", "CRC"]
            writer.writerow(header)

        half_msg, newline, bindata, number_sh = 0, 0, 0, 0

        while self.NumEvent < self.MaxEvent:
            for line in ser.read():  # line = valore decimale del carattere
                if line == 13:  # 13
                    if half_msg == 0:
                        half_msg = 1
                    else:
                        half_msg = 0
                        try:
                            bindata = '{0:032b}'.format(int(data_s, 16))
                        except ValueError:
                            print("non-ASCII character\n")
                            STATUS = 0
                            single_event.clear()
                            pass
                        data_s = ""

                        if bindata[0:2] == "10":  # 10 head bit
                            if bindata == '10111100000000000000000000000000': # PPS event --> cambiare in bindata[3:7] == "1111"
                                STATUS = 4
                                single_event.append(bindata)
                            else:                      # normal channel event
                                STATUS = 1
                                single_event.append(bindata)

                        elif STATUS == 1:
                            if bindata[0:2] == "00": # 00 hit message
                                single_event.append(bindata)
                                STATUS = 2
                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 2:
                            if bindata[0:2] == "01": # 01 sub-hit message
                                single_event.append(bindata)
                                number_sh = number_sh + 1
                                STATUS = 2
                            elif bindata[0:2] == "11": # 01 sub-hit message
                                single_event.append(bindata)
                                if len(single_event) > 2:
                                    buffer_array.append(int(single_event[0][6:11], 2))    # channel
                                    buffer_array.append(int(single_event[0][2:6], 2))     # event type
                                    buffer_array.append(int(single_event[-1][20:26], 2))  # energy hg
                                    buffer_array.append(int(single_event[-1][27:], 2))    # energy lg
                                    buffer_array.append(int(single_event[1][21:27], 2))   # tot coarse
                                    buffer_array.append(int(single_event[1][14:21], 2) - int(single_event[1][27:], 2)) # tot fine
                                    buffer_array.append((float(int(single_event[1][21:27], 2) - int(single_event[0][15:20], 2) + int(single_event[1][27:], 2)) * 5) / 17)
                                    Tcoarse = int((single_event[0][18:]), 2) + int(single_event[1][2:16], 2)
                                    Tfine = int(single_event[1][16:21], 2)
                                    Time_c = float(Tcoarse) * 5 - float(Tfine) / 17
                                    buffer_array.append(Tcoarse)  # Time coarse
                                    buffer_array.append(Tfine)  # Time fine
                                    buffer_array.append(float(Tcoarse) * 5 - float(Tfine) / 17)  # Time

                                    if Time_c > Time_c_old:
                                        buffer_array.append(Time_c - Time_c_old)
                                    else:
                                        buffer_array.append(Time_c + 1000000000 - Time_c_old)
                                    Time_c_old = Time_c
                                    t = time.localtime()
                                    buffer_array.append(time.strftime("%H:%M:%S", t))
                                    buffer_array.append(time.strftime("%Y-%m-%d"))
                                    buffer_array.append(CRC32.crc323check([int(n_str, 2) for n_str in single_event]))

                                    buffer_matrix.append(buffer_array.copy())

                                    number_sh = 0
                                    buffer_array.clear()
                                    single_event.clear()

                                    self.NumEvent = self.NumEvent + 1  # counter for number of events
                                    if len(buffer_matrix) == 100:

                                        outFile = open(file_name, 'a')
                                        writer = csv.writer(outFile)
                                        writer.writerows(buffer_matrix)
                                        outFile.close()

                                        buffer_matrix.clear()
                                        STATUS = 0
                                    else:
                                        single_event.clear()
                                        STATUS = 0
                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 4:
                            if bindata[0:2] == "00": # 00 PPS row 2
                                single_event.append(bindata)
                                STATUS = 5
                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 5:
                                if bindata[0:2] == "01":  # 01 PPS row 3
                                    single_event.append(bindata)
                                    STATUS = 6
                                else:
                                    single_event.clear()
                                    STATUS = 0

                        elif STATUS == 6:
                                if bindata[0:2] == "11":  # 01 PPS row 4                        print('pps row 1')
                                    single_event.append(bindata)
                                    if len(single_event) == 4:
                                        buffer_array.append(20)
                                        buffer_array.append('PPS')
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        buffer_array.append(np.nan)
                                        t = time.localtime()
                                        buffer_array.append(time.strftime("%H:%M:%S", t))
                                        buffer_array.append(time.strftime("%Y-%m-%d"))
                                        buffer_array.append(CRC32.crc323check([int(n_str, 2) for n_str in single_event]))

                                        buffer_matrix.append(buffer_array.copy())

                                        buffer_array.clear()
                                        single_event.clear()

                                        self.NumEvent = self.NumEvent + 1  # counter for number of events
                                        if len(buffer_matrix) == 100:
                                            outFile = open(file_name, 'a')
                                            writer = csv.writer(outFile)
                                            writer.writerows(buffer_matrix)
                                            outFile.close()

                                            buffer_matrix.clear()
                                            STATUS = 0
                                else:
                                    single_event.clear()
                                    STATUS = 0

                else:
                    data_s = data_s + chr(line)
def main():
    AC = acquisitor(MaxEvent=100, port='COM7', filename='test')
    AC.nexysACQ()

if __name__ == "__main__":
    main()