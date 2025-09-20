from flask import Flask, render_template, request, redirect, url_for
from models import db, Product, Purchase

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db.init_app(app)

# DB初期化
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        sample = Product(name="コーヒー豆", unit="kg", supplier="業務スーパー", stock=5)
        db.session.add(sample)
        db.session.commit()

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        purchase = Purchase(product_id=product_id, quantity=quantity, price=price)
        db.session.add(purchase)

        product = Product.query.get(product_id)
        product.stock += quantity
        db.session.commit()

        return redirect(url_for('index'))

    products = Product.query.all()
    return render_template('add_purchase.html', products=products)

@app.route('/update_stock/<int:product_id>/<action>')
def update_stock(product_id, action):
    product = Product.query.get(product_id)
    if action == "plus":
        product.stock += 1
    elif action == "minus" and product.stock > 0:
        product.stock -= 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        unit = request.form['unit']
        supplier = request.form['supplier']
        stock = int(request.form['stock'])

        new_product = Product(name=name, unit=unit, supplier=supplier, stock=stock)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_product.html')

@app.route('/purchases')
def purchases():
    purchases = Purchase.query.all()
    return render_template('purchases.html', purchases=purchases)

if __name__ == '__main__':
    app.run(debug=True)

