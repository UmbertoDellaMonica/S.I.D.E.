"""
Gestione dello store Modbus (registri simulati)
"""

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from configuration_server import NREG


def create_modbus_store(
    nreg=NREG, units=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]
):
    """
    Crea il contesto Modbus con registri simulati per più unit_id.
    DI = Discrete Inputs
    CO = Coils
    HR = Holding Registers
    IR = Input Registers
    """
    context_dict = {}
    for unit_id in units:
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [15] * nreg),
            co=ModbusSequentialDataBlock(0, [16] * nreg),
            hr=ModbusSequentialDataBlock(0, [17] * nreg),
            ir=ModbusSequentialDataBlock(0, [18] * nreg),
        )
        context_dict[unit_id] = store

    # single=False permette di distinguere i vari unit_id
    context = ModbusServerContext(slaves=context_dict, single=False)
    return context
