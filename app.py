import os
from flask import Flask, request, jsonify, render_template

from flask_cors import CORS
from flask_mail import Mail, Message
import stripe
import datetime
stripe.api_key = os.getenv('STRIPE_API_KEY')

app = Flask(__name__,
            static_url_path='',
            static_folder='public')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_ADDRESS')  # Địa chỉ email của bạn
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')         # Mật khẩu ứng dụng Gmail
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_ADDRESS')  # Địa chỉ mặc định khi gửi email
mail = Mail(app)

CORS(app)

SUCCESS_URL = os.getenv('SUCCESS_URL')
CANCEL_URL = os.getenv('CANCEL_URL')



@app.route('/test', methods=['GET'])
def test():
	return jsonify({'message': 'Hello World'}), 200

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
    

def send_email(email, name, address, product, price, payment_type):
    customer_data = {
        "name": name,
        "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "product": product,
        "price": price,
        "address": address,
        "payment_type": payment_type
    }
    
    recipient_email = email
    print("Customer data: ", customer_data)
    
    # Render nội dung email từ template
    email_content = render_template('mail.html', **customer_data)

    # Tạo email
    msg = Message(
        subject="Xác nhận đơn hàng từ Glow & Grow",
        recipients=[recipient_email],
        html=email_content
    )

    try:
        mail.send(msg)
        return jsonify({
			"status": "success",
			"message": "Email đã được gửi"
		}), 200
    except Exception as e:
        return jsonify({
			"status": "error",
			"error": str(e)
		}), 403


@app.route('/api/send-email', methods=['POST'])
def send_email_request():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    address = data.get('address')
    product = data.get('product')
    price = data.get('price')
    payment_type = data.get('payment_type')
    return send_email(email, name, address, product, price, payment_type)



if __name__ == '__main__':
    app.run(port=4242, debug=True)

