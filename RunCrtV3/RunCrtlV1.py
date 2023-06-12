#!/usr/bin/python
"""
File : RunCrtlV1.py
Author: SER
Data  : 03/11/20211

File usati:
    AppSerialPortV1.py
    ListaCMD.py
    AppStore.py
Modifiche di Luigi
Modifiche di Alessandro
Version : 1.0
"""
from ListaCMD import RunControl

Cmd = RunControl()
Cmd.Info()
Cmd.LoopRunControll()
