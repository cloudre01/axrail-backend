from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phonebook.db'
CORS(app)

db.init_app(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone
        }

    def __repr__(self):
        return f'<Contact {self.name}>'


with app.app_context():
    db.create_all()


@app.route('/api/contacts', methods=['GET', 'POST'])
def handle_contacts():
    if request.method == 'GET':
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('perPage', default=5, type=int)
        contacts = Contact.query.paginate(page=page, per_page=per_page)
        return jsonify({
            'contacts': [c.serialized for c in contacts.items],
            'total': contacts.total,
            'pages': contacts.pages,
            'page': contacts.page,
            'hasPrev': contacts.has_prev,
            'hasNext': contacts.has_next,
            'prevNum': contacts.prev_num,
            'nextNum': contacts.next_num,
        })
    elif request.method == 'POST':
        data = request.json
        if not data or not data.get('name') or not data.get('phone'):
            return jsonify({'message': 'Invalid input'}), 400
        try:
            contact = Contact(name=data['name'], phone=data['phone'])
            db.session.add(contact)
            db.session.commit()
        except IntegrityError:
            return jsonify({'message': 'Phone number already exists'}), 409

        return jsonify(contact.serialized), 201


@app.route('/api/contacts/<int:contact_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if request.method == 'GET':
        return jsonify(contact.serialized), 201
    elif request.method == 'PUT':
        data = request.json
        contact.name = data['name']
        contact.phone = data['phone']
        db.session.commit()
        return '', 204
    elif request.method == 'DELETE':
        db.session.delete(contact)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run()
