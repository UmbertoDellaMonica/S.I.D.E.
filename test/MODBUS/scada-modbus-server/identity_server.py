"""
Informazioni descrittive del server Modbus
"""

from pymodbus.device import ModbusDeviceIdentification


def create_identity():
    """
    Crea l'identità del server Modbus
    """
    identity = ModbusDeviceIdentification()
    identity.VendorName = "APMonitor"
    identity.ProductCode = "APM"
    identity.ProductName = "Modbus Server"
    identity.ModelName = "Modbus Server"
    identity.MajorMinorRevision = "3.0.2"
    return identity
