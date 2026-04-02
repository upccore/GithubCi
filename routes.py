from flask import request, jsonify, abort
from datetime import datetime
from models import db, Client, Parking, ClientParking


def init_routes(app):
    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'surname': c.surname,
            'car_number': c.car_number
        } for c in clients])

    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        client = db.session.get(Client, client_id)
        if not client:
            abort(404)
        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        })

    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.json
        client = Client(
            name=data['name'],
            surname=data['surname'],
            credit_card=data.get('credit_card'),
            car_number=data.get('car_number')
        )
        db.session.add(client)
        db.session.commit()
        return jsonify({'id': client.id}), 201

    @app.route('/parkings', methods=['POST'])
    def create_parking():
        data = request.json
        parking = Parking(
            address=data['address'],
            opened=data.get('opened', True),
            count_places=data['count_places'],
            count_available_places=data['count_places']
        )
        db.session.add(parking)
        db.session.commit()
        return jsonify({'id': parking.id}), 201

    @app.route('/client_parkings', methods=['POST'])
    def car_in():
        data = request.json
        client_id = data['client_id']
        parking_id = data['parking_id']

        parking = db.session.get(Parking, parking_id)
        if not parking:
            abort(404)

        if not parking.opened:
            return jsonify({'error': 'Парковка закрыта'}), 400

        if parking.count_available_places <= 0:
            return jsonify({'error': 'Нет свободных мест'}), 400

        active = ClientParking.query.filter_by(
            client_id=client_id,
            parking_id=parking_id,
            time_out=None
        ).first()
        if active:
            return jsonify({'error': 'Уже на парковке'}), 400

        client_parking = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.now()
        )
        parking.count_available_places -= 1

        db.session.add(client_parking)
        db.session.commit()

        return jsonify({'message': 'Заезд выполнен'}), 200

    @app.route('/client_parkings', methods=['DELETE'])
    def car_out():
        data = request.json
        client_id = data['client_id']
        parking_id = data['parking_id']

        client = db.session.get(Client, client_id)
        if not client:
            abort(404)

        parking = db.session.get(Parking, parking_id)
        if not parking:
            abort(404)

        if not client.credit_card:
            return jsonify({'error': 'Не привязана карта'}), 400

        client_parking = ClientParking.query.filter_by(
            client_id=client_id,
            parking_id=parking_id,
            time_out=None
        ).first()

        if not client_parking:
            return jsonify({'error': 'Автомобиль не на парковке'}), 400

        client_parking.time_out = datetime.now()
        parking.count_available_places += 1

        hours = (client_parking.time_out - client_parking.time_in).total_seconds() / 3600
        price = hours * 100

        db.session.commit()

        return jsonify({
            'message': 'Выезд выполнен',
            'price': price
        }), 200
