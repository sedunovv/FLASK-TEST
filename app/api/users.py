from app.api import bp
from flask import abort, jsonify, request, url_for
from app import db
from app.models import User, Currency, Transaction
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data or 'currency' not in data:
        return bad_request('must include username, email, password and currency fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    currency = Currency.query.filter_by(quote=data['currency']).first()
    if not currency:
        return bad_request('please use a currency that already created')
    user = User()
    user.from_dict(data, new_user=True)
    user.currency = currency.id
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route('/transaction', methods=['POST'])
@token_auth.login_required
def create_transaction():
    data = request.get_json() or {}
    if 'sender' not in data or not isinstance(data['sender'], int):
        return bad_request('Sender must not be empty or incorrect value')
    sender = User.query.get_or_404(data['sender'])
    if token_auth.current_user().id != sender.id:
        abort(403)
    if 'recipient' not in data or data['recipient'] == sender.email or \
            not User.query.filter_by(email=data['recipient']).first():
        return bad_request('You can not transfer yourself or empty value')
    if 'transfer_amount' not in data or not isinstance(data['transfer_amount'], (float, int)) or \
            data['transfer_amount'] <= 0.:
        return bad_request('Incorrect value of transfer amount')
    recipient = User.query.filter_by(email=data['recipient']).first()
    sender.bill = sender.bill - float(data['transfer_amount'])
    transfer_amount_base = float(data['transfer_amount']) / sender.currency_user.rate
    recipient_bill = recipient.bill / recipient.currency_user.rate
    transaction = Transaction(sender=sender.id, recipient=recipient.email, transfer_amount_base=transfer_amount_base,
                              sender_rate=sender.currency_user.rate)
    recipient.bill = (recipient_bill + transfer_amount_base) * recipient.currency_user.rate
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict())
