import logging
import requests
import time
import os
from app.api import bp
from app import db
from app.models import Currency
from app.api.errors import bad_request

logger = logging.getLogger(__name__)

FIXER_URL = os.getenv('FIXER_URL', 'http://data.fixer.io/api/latest')
FIXER_ACCESS_KEY = os.getenv('FIXER_ACCESS_KEY', '0c40013086905c29d4137441e2b4ad52')


@bp.route('/update_currency', methods=['POST'])
def update_currency():
    params = {'access_key': FIXER_ACCESS_KEY, 'format': 2}
    req = requests.get(FIXER_URL, params=params)
    if req.status_code != 200:
        logger.error("Currency API %s return status code %s" % (FIXER_URL, req.status_code))

        # Перезапрос в случае ошибки
        time.sleep(15)
        logger.info('New request...')

        req = requests.get(FIXER_URL, params=params)
        if req.status_code != 200:
            msg = "Currency Pairs API %s return status code %s" % (FIXER_URL, req.status_code)
            logger.error(msg)
            return bad_request(msg)
    data = req.json()
    base = data['base']
    for quote in data['rates']:
        if not Currency.query.filter_by(quote=quote).first():
            curr = Currency(base=base, quote=quote, rate=data['rates'][quote])
        else:
            curr = Currency.query.filter_by(quote=quote).first()
            curr.rate = data['rates'][quote]
        db.session.add(curr)
        db.session.commit()
    msg = 'Updated currency successful'
    logger.info(msg)
    return msg
