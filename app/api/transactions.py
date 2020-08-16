from app.api import bp
from flask import abort, jsonify, request
from app import db
from app.models import User, Transaction
from app.api.auth import token_auth
from app.api.errors import bad_request


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


@bp.route('/transactions/user/<int:id>', methods=['GET'])
@token_auth.login_required
def get_transactions(id):
    if token_auth.current_user().id != id:
        abort(403)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Transaction.to_collection_dict(Transaction.query.filter_by(sender=id), page, per_page,
                                          'api.get_transactions', id=id)
    return jsonify(data)
