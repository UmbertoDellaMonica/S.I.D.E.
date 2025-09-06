"""
Gestione dello store Modbus (registri simulati)
"""

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from configuration_server import NREG


def create_modbus_store(nreg=NREG):
    """
    Crea il contesto Modbus con registri simulati.
    DI = Discrete Inputs
    CO = Coils
    HR = Holding Registers
    IR = Input Registers
    """
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [15] * nreg),
        co=ModbusSequentialDataBlock(0, [16] * nreg),
        hr=ModbusSequentialDataBlock(0, [17] * nreg),
        ir=ModbusSequentialDataBlock(0, [18] * nreg),
    )
    context = ModbusServerContext(slaves=store, single=True)
    return context
