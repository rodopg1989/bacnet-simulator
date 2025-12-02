import socket
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import (
    AnalogValueObject,
    BinaryValueObject,
    AnalogInputObject,
    AnalogOutputObject
)
from bacpypes.core import run


# ----- 1) Detectar IP automáticamente -----
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # solo se usa para calcular la IP local
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"  # fallback seguro

local_ip = get_local_ip()
print("IP detectada automáticamente:", local_ip)

# ----- CONFIG DEL DISPOSITIVO -----
device = LocalDeviceObject(
    objectName="PythonSimDevice",
    objectIdentifier=1234,
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=999
)

# ----- OBJETOS BACNET -----
ai1 = AnalogInputObject(
    objectIdentifier=("analogInput", 1),
    objectName="TempSensor1",
    presentValue=22.5,
)

av1 = AnalogValueObject(
    objectIdentifier=("analogValue", 1),
    objectName="Setpoint1",
    presentValue=21.0,
)

ao1 = AnalogOutputObject(
    objectIdentifier=("analogOutput", 1),
    objectName="ValvePosition",
    presentValue=50.0,
)

bv1 = BinaryValueObject(
    objectIdentifier=("binaryValue", 1),
    objectName="PumpStatus",
    presentValue=1,
)

# ----- INICIAR BACNET/IP con IP automática -----
app = BIPSimpleApplication(device, f"{local_ip}/24")

# Registrar objetos
app.add_object(ai1)
app.add_object(av1)
app.add_object(ao1)
app.add_object(bv1)

print("Servidor BACnet Python corriendo…")
run()
