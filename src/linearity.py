import pyvisa
import time
from ACQ_nexys import acquisitor

def sweep(minvalue, maxvalue, step, port='COM7'):  # vedere valori default
    rm = pyvisa.ResourceManager()
    pulser = rm.open_resource('TCPIP0::172.16.0.3::inst0::INSTR')
    pulser.write(":OUTP:STAT ON")
    pulser.write(":AFGControl:START")
    pulser.write(f':VOLTage:AMPLitude {minvalue}')
    acq = acquisitor(MaxEvent=5000, port=port)
    acq.connect()


    for amp in range(minvalue, maxvalue+step, step):
        pulser.write(f':VOLTage:AMPLitude {amp/1000}')
        print(f'Set voltage to {amp} mV')
        time.sleep(1)
        acq.filename = f'sweepA_{amp/1000}mV'
        acq.nexysACQ()

    acq.disconnect()
    pulser.write(":AFGControl:STOP")
    pulser.write(":OUTP:STAT OFF")

def main():
    sweep(60, 120, 60)

if __name__ == '__main__':
    main()
else:
    pass

