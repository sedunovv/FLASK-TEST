import base64
import os
from datetime import datetime, timedelta
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref='currency_user', lazy='dynamic')
    # базовая валюта
    base = db.Column(db.String(10), nullable=False)
    # курс валюты к USD
    quote = db.Column(db.String(10), index=True, unique=True, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '{}'.format(self.base)

    def to_dict(self):
        data = {
            'base': self.base,
            'quote': self.quote,
            'rate': self.rate
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    bill = db.Column(db.Float)
    transactions = db.relationship('Transaction', backref='user_transaction', lazy='dynamic')
    currency = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)

    def __repr__(self):
        return '{}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bill': self.bill,
            'transactions': [],
            'currency': Currency.query.get(self.currency).to_dict(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
            }
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'bill']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.Column(db.String(120), index=True, nullable=False)
    # храним в базовой валюте
    transfer_amount_base = db.Column(db.Float, nullable=False)
    sender_rate = db.Column(db.Float, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'sender': User.query.get(self.sender).to_dict(),
            'recipient': self.recipient,
            'transfer_amount': self.transfer_amount
        }
        return data
