import numpy as np
import serial
import time
import csv
import CRC32
from AppSerialPortV1 import COMPort

class acquisitor(COMPort):

    def __init__(self, porta, MaxEvent=10_000, port='COM5', filename='test_spi'):
        super().__init__(porta)
        self.PortRC = COMPort(porta=porta)
        self.MaxEvent = MaxEvent
        self.port = port
        self.filename = filename
        self.NumEvent = 0

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, 115200)
            print('Connected')
        except serial.serialutil.SerialException:
            print('Seriale non trovata per i dati')
            exit()

    def rst_fifo(self):
        self.PortRC.Config()
        self.PortRC.Send_CMD(0xC, 0x4)
        time.sleep(0.5)
        self.PortRC.Send_CMD(0xC, 0x0)

    def disable_pulser(self):
        self.PortRC.Send_CMD(0x7, 0x0)

    def disconnect(self):
        self.ser.flush()
        self.ser.close()
        print('Disconnected')

    def nexysACQ(self):
        STATUS = 0
        data_s = ""

        single_event = []  # this array contains hits in raw format, as read from the serial port. It is reset event by event.
        subhit_event = []  # this array contains subhits in raw format, as read from the serial port. It is reset event by event.
        buffer_array = []  # this array contains all the information of the event (channel, energy, event time, acquisition time). It is reset event by event.
        buffer_matrix = []  # this matrix is filled with a maximum of 100 buffer_array,then it's written on a file and reset.

        Time_c_old = 0

        #### create the output file ####

        folder = "../run_new/"
        file_name = folder + self.filename + '.csv'

        with open(file_name, 'w') as outFile:
            writer = csv.writer(outFile)
            header = ["Channel", "Event type", "Stato FIFO", "Energy LG", "ToT Coarse", "ToT fine", "ToT", "Time Coarse", "Time fine",
                      "Event time (ns)", 'Delta_time', "Acquisition time", "Date", "CRC"]
            writer.writerow(header)

        half_msg, newline, data, bindata, number_sh = 0, 0, 0, 0, 0
        CRCarray = []
        self.NumEvent = 0

        print('Start acquisition')

        while self.NumEvent < self.MaxEvent:
            for line in self.ser.read():  # line = valore decimale del carattere
                if line == 13:  # 13
                    if half_msg == 0:
                        half_msg = 1
                    else:
                        half_msg = 0
                        try:
                            data = int(data_s, 16)
                        except ValueError:
                            print("non-ASCII character")
                            STATUS = 0
                            single_event.clear()
                            pass
                        data_s = ""

                        if ((data >> 30) & 0X3) == 0X2:  # 10 head bit
                            if ((data >> 26) & 0XF) == 0XF: # PPS event
                                STATUS = 4
                                single_event.append(data)
                            else:                      # normal channel event
                                STATUS = 1
                                single_event.append(data)
                        elif STATUS == 1:
                            if ((data >> 30) & 0X3) == 0: # 00 hit message
                                single_event.append(data)
                                STATUS = 2
                            else:
                                half_msg = 1
                                single_event.clear()
                                STATUS = 0
                        elif STATUS == 2:
                            if ((data >> 30) & 0X3) == 0X1: # 01 sub-hit message
                                subhit_event.append(data)
                                STATUS = 2
                            elif ((data >> 30) & 0X3) == 0X03: # 11 tail message
                                single_event.append(data)

                                if len(single_event) == 3 and len(subhit_event) == 0:    # there are not subhits
                                    buffer_array.append((single_event[0] >> 21) & 0X1F)    # channel
                                    buffer_array.append((single_event[0] >> 26) & 0XF)     # event type
                                    buffer_array.append((single_event[-1] >> 23) & 0x1)  # stato FIFO
                                    buffer_array.append(single_event[-1] & 0XFFF)    # energy lg
                                    buffer_array.append((single_event[1] >> 5) & 0X3F)   # tot coarse
                                    buffer_array.append(((single_event[1] >> 11) & 0X1F) - (single_event[1] & 0X1F)) # tot fine
                                    buffer_array.append((float((single_event[1] >> 5) & 0X3F) * 5 -
                                                         float(single_event[1] & 0X1F) * 5 / 17 +
                                                         float((single_event[1] >> 11) & 0X1F) * 5 / 17))
                                    Tcoarse = (single_event[0] & 0X3FFF) + ((single_event[1] >> 16) & 0X3FFF)
                                    Tfine = (single_event[1] >> 11) & 0X1F
                                    Time_c = float(Tcoarse) * 5 - float(Tfine) / 17
                                    buffer_array.append(Tcoarse)  # Time coarse
                                    buffer_array.append(Tfine)  # Time fine
                                    buffer_array.append(Time_c)  # Time

                                    if Time_c > Time_c_old:
                                        buffer_array.append(Time_c - Time_c_old)
                                    else:
                                        buffer_array.append(Time_c + 1000000000 - Time_c_old)
                                    Time_c_old = Time_c
                                    t = time.localtime()
                                    buffer_array.append(time.strftime("%H:%M:%S", t))
                                    buffer_array.append(time.strftime("%Y-%m-%d"))
                                    buffer_array.append(CRC32.crc323check([n_str for n_str in single_event]))

                                    buffer_matrix.append(buffer_array.copy())

                                    buffer_array.clear()
                                    single_event.clear()

                                    self.NumEvent = self.NumEvent + 1  # counter for number of events
                                    if len(buffer_matrix) == 100:
                                        print(self.NumEvent)

                                        outFile = open(file_name, 'a')
                                        writer = csv.writer(outFile)
                                        writer.writerows(buffer_matrix)
                                        outFile.close()

                                        buffer_matrix.clear()
                                        STATUS = 0
                                    else:
                                        single_event.clear()
                                        STATUS = 0

                                elif len(single_event) == 3 and len(subhit_event) != 0:   # there are subhits
                                    CRCarray.append(single_event[0])
                                    CRCarray.append(single_event[1])
                                    buffer_array.append((single_event[0] >> 21) & 0X1F)    # channel
                                    buffer_array.append((single_event[0] >> 26) & 0XF)     # event type
                                    buffer_array.append((single_event[-1] >> 23) & 0x1)  # stato FIFO
                                    buffer_array.append(single_event[-1] & 0XFFF)    # energy lg
                                    buffer_array.append((single_event[1] >> 5) & 0X3F)   # tot coarse
                                    buffer_array.append(((single_event[1] >> 11) & 0X1F) - (single_event[1] & 0X1F)) # tot fine
                                    buffer_array.append((float((single_event[1] >> 5) & 0X3F) * 5) -
                                                        (float(single_event[1] & 0X1F) * 5 / 17) +
                                                        (float((single_event[1] >> 11) & 0X1F) * 5 / 17))
                                    Tcoarse = (single_event[0] & 0X3FFF) + ((single_event[1] >> 16) & 0X3FFF)
                                    Tfine = (single_event[1] >> 11) & 0X1F
                                    Time_c = float(Tcoarse) * 5 - float(Tfine) / 17
                                    buffer_array.append(Tcoarse)  # Time coarse
                                    buffer_array.append(Tfine)  # Time fine
                                    buffer_array.append(Time_c)  # Time

                                    if Time_c > Time_c_old:
                                        buffer_array.append(Time_c - Time_c_old)
                                    else:
                                        buffer_array.append(Time_c + 1000000000 - Time_c_old)
                                    Time_c_old = Time_c
                                    t = time.localtime()
                                    buffer_array.append(time.strftime("%H:%M:%S", t))
                                    buffer_array.append(time.strftime("%Y-%m-%d"))
                                    buffer_matrix.append(buffer_array.copy())

                                    buffer_array.clear()

                                    self.NumEvent = self.NumEvent + 1  # counter for number of events

                                    for i in range(len(subhit_event)):
                                        CRCarray.append(subhit_event[i])
                                        buffer_array.append((single_event[0] >> 21) & 0X1F)  # channel
                                        buffer_array.append('Sub-hit')  # event type
                                        buffer_array.append(np.nan)  # energy hg
                                        buffer_array.append(np.nan)  # energy lg
                                        buffer_array.append((subhit_event[i] >> 5) & 0X3F)  # tot coarse
                                        buffer_array.append(((single_event[1] >> 11) & 0X1F) - (single_event[1] & 0X1F)) # tot fine
                                        buffer_array.append((float((subhit_event[i] >> 5) & 0X3F) * 5 -
                                                             float(subhit_event[i] & 0X1F) * 5 / 17 +
                                                             float((subhit_event[i] >> 11) & 0X1F) * 5 / 17))
                                        Tcoarse = (subhit_event[i] >> 16) & 0X3FFF
                                        Tfine = (subhit_event[i] >> 11) & 0X1F
                                        Time_c = float(Tcoarse) * 5 - float(Tfine) / 17
                                        buffer_array.append(Tcoarse)  # Time coarse
                                        buffer_array.append(Tfine)  # Time fine
                                        buffer_array.append(Time_c)  # Time

                                        if Time_c > Time_c_old:
                                            buffer_array.append(Time_c - Time_c_old)
                                        else:
                                            buffer_array.append(Time_c + 1000000000 - Time_c_old)
                                        Time_c_old = Time_c
                                        t = time.localtime()
                                        buffer_array.append(time.strftime("%H:%M:%S", t))
                                        buffer_array.append(time.strftime("%Y-%m-%d"))
                                        CRCarray.append(single_event[2])
                                        buffer_array.append(CRC32.crc323check(CRCarray))
                                        CRCarray.clear()

                                        buffer_matrix.append(buffer_array.copy())
                                        buffer_array.clear()

                                        self.NumEvent = self.NumEvent + len(subhit_event)

                                    subhit_event.clear()

                                    single_event.clear()

                                    if len(buffer_matrix) >= 100:
                                        print(self.NumEvent)

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
                                    subhit_event.clear()
                                    STATUS = 0

                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 4:
                            if ((data >> 30) & 0X3) == 0: # 00 PPS row 2
                                single_event.append(data)
                                STATUS = 5
                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 5:
                            if ((data >> 30) & 0X3) == 0x1:  # 01 PPS row 3
                                single_event.append(data)
                                STATUS = 6
                            else:
                                single_event.clear()
                                STATUS = 0

                        elif STATUS == 6:
                                if ((data >> 30) & 0X3) == 0x3:  # 01 PPS row 4
                                    single_event.append(data)
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
                                        buffer_array.append(CRC32.crc323check([n_str for n_str in single_event]))

                                        buffer_matrix.append(buffer_array.copy())

                                        buffer_array.clear()
                                        single_event.clear()

                                        self.NumEvent = self.NumEvent + 1  # counter for number of events
                                        if len(buffer_matrix) == 100:
                                            print(self.NumEvent)

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
        self.disconnect()
def main():
    AC = acquisitor(porta='COM6', MaxEvent=10_000, port='COM7', filename='test_spi')
    AC.connect()
    AC.rst_fifo()
    AC.nexysACQ()
    AC.disable_pulser()


if __name__ == "__main__":
    main()
else:
    pass
