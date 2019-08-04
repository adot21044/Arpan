from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import config
import datetime
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'Media')

app = Flask(__name__, static_url_path="/static")
app.config.from_object(config.Config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)
login_manager=LoginManager(app)
login_manager.init_app(app)
# model imports here
from models import *


@login_manager.user_loader 
def load_user(email):
    print(id)
    print(User.get(id))
    return User.get(email)

LOW_STOCK_THRESHOLD = 100
msg = Message("Dear Admin, Your stock is running low, Please restock soon", sender="adit.ganapathy@oberoi-is.net", 
        recipients=["adit.ganapathy@outlook.com"])

@app.route("/")
def home():
   

    request_count = ProductRequest.query.count()
    print("All",request_count)
    team_pse_request = ProductRequest.query.filter_by(team="pse") 
    team_pse_count  = (team_pse_request.count())
    team_pe_request = ProductRequest.query.filter_by(team="pe")
    team_pe_count = (team_pe_request.count())
    team_training_request = ProductRequest.query.filter_by(team="training")
    team_training_count = (team_training_request.count())
    requestdata=dict()
    try:
        requestdata["pse"]=round((team_pse_count/request_count)*100,0)
        requestdata["pe"]=round((team_pe_count/request_count)*100,0)
        requestdata["training"]=round((team_training_count/request_count)*100,0)
        requestdata["others"]=round(((request_count-team_pse_count-team_pe_count-team_training_count)/request_count)*100,0)
    except:
        requestdata["pse"]=0
        requestdata["pe"]=0
        requestdata["training"]=0
        requestdata["others"]=0   

    
    return render_template("dashboard.html", requestdata=requestdata)


#TODO: SHow product name instead of product id
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
            "description"), dateadded=str(datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language=data.get("language"), version
                =data.get("version"))
        if 'file_url' in request.files:
            file_url = request.files['file_url']
            filename = secure_filename(file_url.filename)
            file_url.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.file_url = filename
        db.session.add(product)
        db.session.commit()
    products = Product.query.all()
    vendors = Vendor.query.all()

    return render_template("product.html", products=products, vendors=vendors)


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
        vendor= Vendor(name=data.get("Name"), city=data.get("city"), GST=data.get("gst"), contact_person=data.get
         ("contact_person"), contact_number=str(data.get("contact_number")), remarks=data.get("remarks"))
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
        #TODO remove hardcoded user_id
        product_request=ProductRequest(product_id=data.get("product"), quantity=data.get("quantity"), 
        user_id=2, date=data.get("date"), status=data.get("status"), organisation=data.get("organisation")
            , city=data.get("city"), state=data.get("state"), team=data.get("team"))
    
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(product_id=data.get("product")).first()
            if inventory is not None:
                inventory.quantity = inventory.quantity - int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    mail.send(msg)
                    pass
                db.session.add(inventory)
        db.session.add(product_request)
        db.session.commit()
    products = Product.query.all()
    product_requests=ProductRequest.query.all()
    return render_template("productrequest.html", products=products, product_requests=product_requests)

@app.route("/delete-product-request/<request_id>")
def delete_product_request(request_id):
    productrequest=ProductRequest.query.filter_by(id=request_id).first()
    db.session.delete(productrequest)
    db.session.commit()
    return redirect ("/product-requests")


@app.route("/purchase-orders", methods=["GET", "POST"])
def purchase_orders():
    if request.form:

        data = request.form
        purchase_orders=PurchaseOrders(product_id=data.get("product"), price=data.get("price"), vendor=data.get("vendor"),quantity=data.get(
            "quantity"), remarks=data.get("remarks"), date_added=str(datetime.datetime.now()),date_modified=str(datetime.datetime.now()), status=data.get("status"))
        if data.get("status") == "accepted":
            inventory = Inventory.query.filter_by(product_id=data.get("product"), vendor=data.get("vendor")).first()
            if inventory is not None:
                inventory.quantity = inventory.quantity + int(data.get("quantity"))
            else:
                inventory = Inventory(product_id=data.get("product"), price=data.get("price"), quantity=data.get("quantity"),date=str(datetime.datetime.now()),vendor=data.get("vendor"))
            db.session.add(inventory)
        db.session.add(purchase_orders)
        db.session.commit()
    stock = PurchaseOrders.query.order_by(PurchaseOrders.date_added.desc())
    products = Product.query.all()
    vendors= Vendor.query.all()

    
    return render_template("purchaseorder.html", stock=stock, products=products, vendors=vendors)



    
    
if __name__ == "__main__":
    app.run(debug=True)


