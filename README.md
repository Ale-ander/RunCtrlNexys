# RunControl Nexys
An interactive GUI for the HyperKamiokande mPMT testing firmware running ona Nexys A7/Nexys 4 FPGA board. The Run control allows for read/writing the FPGA registers, take data and monitor the HV board. It uses 3 seiral connection to configura in the GUI before clicking connect. 

The main file to run is **RunCtrlGUI.py**

## Board setup
To make the GUI work the coputer running it needs 3 serial ports:
- One for **RunControl** that goes to the FPGA PMOD header (the header transmits using UART protocol so an adapter is needed)
- One for **HV** that goes to the FEB microcontroller
- One for **data** that goes to the board and is also used for power

ACQ_Nexys.py is the script for data taking, it can be used also by itself, and adapted for every situation.

hv.py is the script for controlling the HV board using modbus protocol. It uses the cmd package for python.

**NB: use only cmd version 2.1.2**