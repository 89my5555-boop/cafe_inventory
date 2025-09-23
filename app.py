from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Product, Purchase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'your-secret-key'  # Flask-Login に必須
db.init_app(app)

# --- User モデルを app.py 内に定義 ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# --- Flask-Login 設定 ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未ログイン時に /login へリダイレクト

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- DB 初期化 ---
with app.app_context():
    db.create_all()


# ✅ ユーザー登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("このユーザー名はすでに使われています")
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("登録成功！ログインしてください")
        return redirect(url_for('login'))

    return render_template('register.html')


# ✅ ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("ログイン成功")
            return redirect(url_for('index'))
        else:
            flash("ユーザー名またはパスワードが違います")

    return render_template('login.html')


# ✅ ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("ログアウトしました")
    return redirect(url_for('login'))


# --- 在庫関連（全部ログイン必須） ---
@app.route('/')
@login_required
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/add_purchase', methods=['GET', 'POST'])
@login_required
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
@login_required
def update_stock(product_id, action):
    product = Product.query.get(product_id)
    if action == "plus":
        product.stock += 1
    elif action == "minus" and product.stock > 0:
        product.stock -= 1
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
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
@login_required
def purchases():
    purchases = Purchase.query.all()
    return render_template('purchases.html', purchases=purchases)


if __name__ == '__main__':
    app.run(debug=True)
