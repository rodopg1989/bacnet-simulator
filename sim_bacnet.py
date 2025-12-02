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
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

local_ip = get_local_ip()
print("IP detectada automáticamente:", local_ip)

# ----- 2) Configurar el dispositivo BACnet -----
device = LocalDeviceObject(
    objectName="PythonSimDevice",
    objectIdentifier=1234,
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=999
)

# ----- 3) Crear objetos BACnet simulados -----
# Sensores AI
temperature = AnalogInputObject(objectIdentifier=("analogInput",1),
                                objectName="TemperatureSensor",
                                presentValue=22.5)
humidity = AnalogInputObject(objectIdentifier=("analogInput",2),
                             objectName="HumiditySensor",
                             presentValue=55.0)

# Salidas AO
valve = AnalogOutputObject(objectIdentifier=("analogOutput",1),
                           objectName="ValvePosition",
                           presentValue=50.0)
fan_speed = AnalogOutputObject(objectIdentifier=("analogOutput",2),
                               objectName="FanSpeed",
                               presentValue=75.0)

# Setpoints AV
temp_setpoint = AnalogValueObject(objectIdentifier=("analogValue",1),
                                  objectName="TempSetpoint",
                                  presentValue=21.0)
humidity_setpoint = AnalogValueObject(objectIdentifier=("analogValue",2),
                                      objectName="HumiditySetpoint",
                                      presentValue=50.0)

# Estados BV
pump = BinaryValueObject(objectIdentifier=("binaryValue",1),
                         objectName="PumpStatus",
                         presentValue=1)  # 1=ON, 0=OFF
valve_status = BinaryValueObject(objectIdentifier=("binaryValue",2),
                                 objectName="ValveStatus",
                                 presentValue=0)

# ----- 4) Inicializar BACnet/IP -----
app = BIPSimpleApplication(device, f"{local_ip}/24")

# ----- 5) Registrar objetos -----
for obj in [temperature, humidity, valve, fan_speed,
            temp_setpoint, humidity_setpoint, pump, valve_status]:
    app.add_object(obj)

print("Servidor BACnet extendido corriendo...")
run()
