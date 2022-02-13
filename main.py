from flask import Flask, render_template,abort, redirect, url_for, flash,request
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv
from sqlalchemy import ForeignKey, Integer, Column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import Register_user, Login, Item
from flask_gravatar import Gravatar
from functools import wraps
import random
import stripe

stripe.api_key = os.environ['stripe']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('key')
# os.environ.get('SECRET_KEY')
Bootstrap(app)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///shop.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)



gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    print('user is loaded ')
    return User.query.get(user_id)

def admin(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        try:
            user_id = current_user.id
        except:
            print('no user')
            user_id=0
        if user_id != 1 or not current_user.is_authenticated:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function




##CONFIGURE TABLES
class User(db.Model,UserMixin):
    # Parent
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250),nullable=False,unique=True)
    password = db.Column(db.String(250),nullable=False)
    name = db.Column(db.String(250),nullable=False)

    product = relationship('Product', back_populates='owner')

db.create_all()

class Product(UserMixin,db.Model):
    # Child
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = relationship('User',back_populates='product')

    product_name = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Integer,nullable=False)
    product_num =  db.Column(db.Integer,nullable=False)


db.create_all()





@app.route('/')
def home():
    items = Product.query.all()
    return render_template("index.html", items=items)


@app.route('/success')
def success():
    return render_template("success.html")

@app.route('/buyNow/<int:id>')
def buy(id):
    item = Product.query.filter_by(id=id).first()
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product_name,
                },
                'unit_amount': item.price*100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:80/success',
        cancel_url='https://example.com/cancel',
    )

    return redirect(session.url, code=303)
    return render_template("buy.html", item=item)

@app.route('/create',methods=["POST","GET"])
def create():
    form = Item()
    if form.validate_on_submit():
        new_item = Product(
            product_name=form.product_name.data,
            subtitle=form.subtitle.data,
            img_url=form.img_url.data,
            price=form.price.data,
            product_num=random.randint(1,10000),
            owner=current_user,


        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("login.html",title='Create',form=form)

@app.route('/login',methods=["POST","GET"])
def login():
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user=user)
                return redirect(url_for('home', loged_in=True))
            else:
                flash('passwords dont match.', 'error')
                redirect('login')
        else:
            flash('email does not exist.', 'error')
            redirect('login')
    return render_template("login.html",title='Login',form=form)

@app.route('/register',methods=["POST","GET"])
def register():
    form = Register_user()
    if form.validate_on_submit():
        pass_hash = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)
        user=User(
            email=form.email.data,
            password = pass_hash,
            name=form.name.data,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        print('user loged in ')
        return redirect(url_for('home'))
    return render_template("login.html",title='Register',form=form)


@app.route('/logout')
def logout():
    logout_user()
    print('user logged out')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="localhost", port=80, debug=True)
