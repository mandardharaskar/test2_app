from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Product %r>' % self.id


# Register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [Validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', message='Password do not match')])
    confirm = PasswordField('Confirm Passsword')

# User reg
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        new_register = RegisterForm(name=name,
                                    email=email,
                                    username=username,
                                    password=password
                                    )

        try:
            db.session.add(new_register)
            db.session.commit()
            return redirect('/login')
        except:
            return 'There is an issue adding your account'

    else:
        form = RegisterForm.query.order_by(RegisterForm.date_created).all()
        return render_template('register.html', form=form)

# user login
@app.route('/login', methods=['Post', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['name']
        product_image = request.form['image']
        product_desc = request.form['desc']
        product_price = request.form['price']
        new_product = Orders(name=product_name,
                             image=product_image,
                             desc=product_desc,
                             price=product_price
                             )

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/index')
        except:
            return 'There is an issue adding your product'

    else:
        products = Orders.query.order_by(Orders.date_created).all()
        return render_template('index.html', products=products)


@app.route('/delete/<int:id>')
def delete(id):
    product_to_delete = Orders.query.get_or_404(id)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect('/index')
    except:
        return 'There was a problem deleting your product'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    product = Orders.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.image = request.form['image']
        product.desc = request.form['desc']
        product.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/index')
        except:
            return 'There was a issue updating your product'
    else:
        return render_template('update.html', product=product)


if __name__ == '__main__':
    app.run(debug=True)
