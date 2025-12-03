from flask import Flask, request
from flask_restx import Api, Resource, fields
from sim_bacnet import app as bacnet_app
from bacpypes.object import AnalogInputObject, AnalogOutputObject, AnalogValueObject, BinaryValueObject
from bacpypes.core import run
import threading

# ------------------------------
# Función para correr BACnet en un hilo
# ------------------------------
def run_bacnet():
    print(f"IP detectada automáticamente: {bacnet_app.localAddress.addrIP}")
    print("Servidor BACnet extendido corriendo...")
    run()  # Esto es bloqueante, por eso va en un hilo

# ------------------------------
# Configuración Flask + Swagger
# ------------------------------
api_app = Flask(__name__)
api = Api(api_app,
          version="1.0",
          title="BACnet Simulator API",
          description="API para manipular objetos BACnet dinámicamente",
          doc="/swagger")  # URL de Swagger UI

# ------------------------------
# Modelo de objeto para Swagger
# ------------------------------
object_model = api.model('BACnetObject', {
    'type': fields.String(required=True, description='Tipo de objeto: AI, AO, AV, BV'),
    'id': fields.Integer(required=True, description='Identificador único'),
    'name': fields.String(required=True, description='Nombre del objeto'),
    'value': fields.Float(default=0, description='Valor inicial')
})

# ------------------------------
# Función auxiliar para crear objetos dinámicamente
# ------------------------------
def create_object(obj_type, obj_id, name, value):
    if obj_type == "AI":
        obj = AnalogInputObject(objectIdentifier=("analogInput", obj_id),
                                objectName=name, presentValue=value)
    elif obj_type == "AO":
        obj = AnalogOutputObject(objectIdentifier=("analogOutput", obj_id),
                                 objectName=name, presentValue=value)
    elif obj_type == "AV":
        obj = AnalogValueObject(objectIdentifier=("analogValue", obj_id),
                                objectName=name, presentValue=value)
    elif obj_type == "BV":
        obj = BinaryValueObject(objectIdentifier=("binaryValue", obj_id),
                                objectName=name, presentValue=value)
    else:
        return None
    return obj

# ------------------------------
# Endpoints de la API
# ------------------------------
@api.route("/objects")
class Objects(Resource):
    def get(self):
        """Listar todos los objetos BACnet existentes"""
        objects = []

        # Iterar sobre la lista oficial de objetos del dispositivo
        for obj_id in bacnet_app.objectIdentifier:
            obj = bacnet_app.get_object_id(obj_id)  # obtener el objeto real

            objects.append({
                "type": obj.objectIdentifier[0],
                "id": obj.objectIdentifier[1],
                "name": obj.objectName,
                "value": getattr(obj, "presentValue", None)
            })

        return objects


    @api.expect(object_model)
    def post(self):
        """Agregar un nuevo objeto BACnet dinámicamente"""
        data = request.json
        obj_type = data.get("type")
        obj_id = data.get("id")
        name = data.get("name")
        value = data.get("value", 0)
        obj = create_object(obj_type, obj_id, name, value)
        if obj is None:
            return {"error": f"Tipo de objeto desconocido: {obj_type}"}, 400
        bacnet_app.add_object(obj)
        return {"status": "ok", "object": data}, 201

@api.route("/objects/<string:obj_type>/<int:obj_id>")
class ObjectItem(Resource):
    def patch(self, obj_type, obj_id):
        """Actualizar el presentValue de un objeto BACnet"""
        data = request.json
        new_value = data.get("value")
        if new_value is None:
            return {"error": "Falta 'value'"}, 400

        obj = bacnet_app.objectIdentifierCache.get((obj_type.lower(), obj_id))
        if not obj:
            return {"error": "Objeto no encontrado"}, 404

        obj.presentValue = new_value
        return {"status": "ok", "object": {"type": obj_type, "id": obj_id, "value": new_value}}

# ------------------------------
# Ejecutar API + simulador BACnet
# ------------------------------
if __name__ == "__main__":
    # Levantar BACnet en hilo separado
    threading.Thread(target=run_bacnet, daemon=True).start()

    # Levantar Flask API
    print("API BACnet corriendo en http://localhost:5000")
    print("Swagger UI disponible en http://localhost:5000/swagger")
    api_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
