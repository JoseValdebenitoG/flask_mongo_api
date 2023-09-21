from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
import os

# Iniciamos flask
app = Flask(__name__)
# Configuramos la conexión a la base de datos
app.config['MONGODB_NAME'] = 'first_flask_api'
# usamos un archivo .env para la variable de entorno.
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
# Usamos PyMongo para conectarnos a la base de datos
mongo = PyMongo(app, tlsCAFile=certifi.where())

# Routes


@app.route('/users', methods=['POST'])
def create_user():
    print(request.json)
    # Recibimos los datos
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    # Verificamos los datos antes de enviarlos a la BD
    if username and password and email:
        hashed_password = generate_password_hash(password)
        id = mongo.db.users.insert_one(
            {'username': username, 'email': email, 'password': hashed_password}
        )
        response = {
            'id': str(id),
            'username': username,
            'password': hashed_password,
            'email': email
        }
        return response
    else:
        return not_found()

    return {'message': 'received'}

# Traer todos los usuarios


@app.route('/users', methods=['GET'])
def get_users():
    users = mongo.db.users.find()  # obtiene todos los datos en formato bson
    # con json_util desde la librería bson lo transformamos a json
    response = json_util.dumps(users)
    # importamos Response desde flask para entregar una respuesta mas elaborada al cliente
    return Response(response, mimetype='application/json')
    # con mimetype le decimos al navegador del cliente que el string es json.

# Traer un usuario


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    # importamos ObjectID desde bson para pedir el usuario por el _id
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')

# Eliminar usuario


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify(
        {'message': 'The User ' + id + ' was Deleted successfully'})
    return response

# Actualizar usuario


@app.route('/users/<id>', methods=['PUT'])
def update_user(id):
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    if username and password and email:
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one({'_id': ObjectId(id)}, {'$set': {
            'username': username,
            'password': hashed_password,
            'email': email
        }})
        response = jsonify(
            {'message': 'The User ' + id + ' was Updated successfully'})
        return response

# controlador de errores


@app.errorhandler(404)
def not_found(error=None):
    message = jsonify({
        'message': 'Resource Not Found: ' + request.url,
        'status': 404
    })
    message.status_code = 404
    return message


# Iniciamos la aplicación
if __name__ == '__main__':
    app.run(debug=True)
