from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = [message.to_dict() for message in Message.query.order_by(Message.created_at.asc()).all()]
    response = make_response(messages, 200)
    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if message:
        response = make_response(message.to_dict(), 200)
    else:
        response = make_response(jsonify({'error': 'Message not found'}), 404)
    return response

@app.route('/messages', methods=['POST'])
def create_message():
    body = request.json.get('body')
    username = request.json.get('username')

    if not body or not username:
        response = make_response(jsonify({'error': 'Missing required fields: body, username'}), 400)
        return response

    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()

    response = make_response(message.to_dict(), 201)
    response.headers['Location'] = f'/messages/{message.id}'
    return response


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response = make_response(jsonify({'error': 'Message not found'}), 404)
        return response

    body = request.json.get('body')

    if body:
        message.body = body

    db.session.commit()

    response = make_response(message.to_dict(), 200)
    return response


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        response = make_response(jsonify({'error': 'Message not found'}), 404)
        return response

    db.session.delete(message)
    db.session.commit()

    response = make_response(jsonify({'message': 'Message deleted'}), 204)
    return response

    

if __name__ == '__main__':
    app.run(port=5555)
