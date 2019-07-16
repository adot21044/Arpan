from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import config
import datetime
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'Media')

app = Flask(__name__, static_url_path="/static")
app.config.from_object(config.Config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.init_app(app)
# model imports here
from models import *


@login_manager.user_loader 
def load_user(email):
    print(id)
    print(User.get(id))
    return User.get(email)


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.form:
        print(request.form)
        data = request.form
        inventory = Inventory(product_id=data.get("product"), price=data.get("price"), quantity=data.get(
            "quantity"), description=data.get("description"), date=str(datetime.datetime.now()))
        db.session.add(inventory)
        db.session.commit()
    stock = Inventory.query.all()
    products = Product.query.all()
    return render_template("inventory.html", stock=stock, products=products)


@app.route("/products", methods=["GET", "POST"])
def product():
    if request.form:
        print(request.form)
        data = request.form
        product = Product(name=data.get("name"), type=data.get("type"), mrp=data.get("mrp"), description=data.get(
            "description"), dateadded=str(datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language=data.get("language"))
        if 'file_url' in request.files:
            file_url = request.files['file_url']
            filename = secure_filename(file_url.filename)
            file_url.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.file_url = filename
        db.session.add(product)
        db.session.commit()
    products = Product.query.all()

    return render_template("product.html", products=products)


@app.route("/users", methods=["GET", "POST"])
def users():
    if request.form:
        print(request.form)
        data=request.form
        user= User(email=data.get("Email"), role=data.get("Role"), 
            contact_number=data.get("contact_number"), team=data.get("team"))
        user.set_password(data.get("Password"))
        db.session.add(user)
        db.session.commit()

    users = User.query.all()

    return render_template("users.html", users=users)

@app.route("/vendors", methods=["GET", "POST"])
def vendor():
    if request.form:
        data=request.form
        vendor= Vendor(name=data.get("Name"), city=data.get("City_of_Operations"), GST=data.get("gst"), contact_person=data.get
         ("contact_person"), contact_number=data.get("contact_number"), remarks=data.get("remarks"))
        db.session.add(vendor)
        db.session.commit()
    vendors= Vendor.query.all()
    return render_template("vendor.html", vendors=vendors)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.form:
        data=request.form
        user=User.query.filter_by(email=data.get("Email")).first()
        if user is None or not user.check_password(data.get("Password")):
            print("User not present or wrong password")
            return redirect(url_for("login"))
        # login_user(user) # TODO
        return redirect(url_for("home"))
    #form=Loginform()
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/product-requests", methods=["GET", "POST"])
def product_request():
    if request.form:
        data=request.form
        product_request=ProductRequest(product_id=data.get("Product Name"), quantity=data.get("Quantity"), 
        user_id=data.get("Team"), date=data.get("Date"), status=data.get("Status"), organisation=data.get("Organisation")
            , city=data.get("City"), state=data.get("State"))
        db.session.add(product_request)
        db.session.commit()
    product_request=ProductRequest.query.all()
    return render_template("productrequest.html")

@app.route("/purchase-orders", methods=["GET", "POST"])
def purchase_orders():
    if request.form:
        print(request.form)
        data = request.form
        purchase_orders=PurchaseOrders(product_id=data.get("product"), price=data.get("price"), quantity=data.get(
            "quantity"), description=data.get("description"), date=str(datetime.datetime.now()))
        db.session.add(purchase_orders)
        db.session.commit()
    stock = PurchaseOrders.query.all()
    
    return render_template("purchaseorder.html", stock=stock)
    
if __name__ == "__main__":
    app.run(debug=True)


