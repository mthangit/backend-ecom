import os
from flask import Flask, request, jsonify

from flask_cors import CORS
import stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')

app = Flask(__name__,
            static_url_path='',
            static_folder='public')

CORS(app)

SUCCESS_URL = os.getenv('SUCCESS_URL')
CANCEL_URL = os.getenv('CANCEL_URL')

@app.route('/api/create-payment', methods=['POST'])
def payment():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    return create_checkout_session(product_id, quantity)

def create_checkout_session(product_id, quantity):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': product_id,
                    'quantity': quantity,
                },
            ],
            mode='payment',
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )
        return jsonify({
			'status': 'success',
			'url': checkout_session.url,
			'session_id': checkout_session.id
            }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
		}), 403


if __name__ == '__main__':
    app.run(port=4242, debug=True)

