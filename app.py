from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import os
import config
import datetime
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
import json
import csv
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
def load_user(user_id):
    return None


LOW_STOCK_THRESHOLD = 100
msg = Message("Dear Admin, Your stock is running low, Please restock soon", sender="adit.ganapathy@oberoi-is.net", 
        recipients=["adit.ganapathy@outlook.com"])

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

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
    except:
        requestdata["pse"]=0
    try:
        requestdata["pe"]=round((team_pe_count/request_count)*100,0)
    except:
        requestdata["pe"]=0
    try:
        requestdata["training"]=round((team_training_count/request_count)*100,0)
    except:
        requestdata["training"]=0
    try:
        requestdata["others"]=round(((request_count-team_pse_count-team_pe_count-team_training_count)/request_count)*100,0)
    except:
        requestdata["others"]=0   
    print(requestdata)
    # product_count = product_request.master_product.name.query.count()
    # print("All: ", product_count)
    return render_template("dashboard.html", requestdata=requestdata)

@app.route("/team-home", methods=["GET", "POST"])
def team_home():
    return render_template("teamdashboard.html")




@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.form:
        print(request.form)
        data = request.form
        inventory = Inventory(product_id=data.get("product"), price=data.get("price"), quantity=data.get(
            "quantity"), description=data.get("description"), date=str(datetime.datetime.now()))
        db.session.add(inventory)
        db.session.commit()
    stock = Inventory.query.order_by(Inventory.date.desc())
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
    # if current_user.is_authenticated:
    #     return redirect(url_for("home"))
    if request.form:
        data=request.form
        user=User.query.filter_by(email=data.get("Email")).first()
        if user is None or not user.check_password(data.get("Password")):
            print("User not present or wrong password")
            return redirect(url_for("login"))
        login_user(user) # TODO
        if user.role == "admin":
            return redirect(url_for("home"))
        else: 
            return redirect(url_for("team_home"))
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
            , city=data.get("city", ""), state=data.get("state"), team=data.get("team"))
    
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(product_id=data.get("product")).first()
            if inventory is not None:
                inventory.quantity = inventory.quantity - int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    # mail.send(msg) TODO
                    pass
                db.session.add(inventory)
        db.session.add(product_request)
        db.session.commit()
    products = Product.query.all()
    product_requests=ProductRequest.query.order_by(ProductRequest.date.desc())
    return render_template("productrequest.html", products=products, product_requests=product_requests)


@app.route("/team-product-requests", methods=["GET", "POST"])
def team_product_request():
    
    if request.form:
        data=request.form
        #TODO remove hardcoded user_id
        product_request=ProductRequest(product_id=data.get("product"), quantity=data.get("quantity"), 
        user_id=2, date=data.get("date"), status="pending", organisation=data.get("organisation")
            , city=data.get("city", ""), state=data.get("state"), team=data.get("team"))
    
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(product_id=data.get("product")).first()
            if inventory is not None:
                inventory.quantity = inventory.quantity - int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    # mail.send(msg) TODO
                    pass
                db.session.add(inventory)
        db.session.add(product_request)
        db.session.commit()
    products = Product.query.all()
    product_requests=ProductRequest.query.order_by(ProductRequest.date.desc())
    return render_template("teamproductrequest.html", products=products, product_requests=product_requests)



@app.route("/delete-product-request/<request_id>")
def delete_product_request(request_id):
    productrequest=ProductRequest.query.filter_by(id=request_id).first()
    product_id=productrequest.product_id
    if productrequest.status == "fulfilled":
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity + productrequest.quantity
    db.session.delete(productrequest)
    db.session.commit()
    return redirect ("/product-requests")

@app.route("/team-delete-product-request/<request_id>")
def team_delete_product_request(request_id):
    productrequest=ProductRequest.query.filter_by(id=request_id).first()
    product_id=productrequest.product_id
    if productrequest.status == "fulfilled":
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity + productrequest.quantity
    db.session.delete(productrequest)
    db.session.commit()
    return redirect ("/team-product-requests")



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


@app.route("/delete-purchase-order/<request_id>")
def delete_purchase_order(request_id):
    purchase_orders=PurchaseOrders.query.filter_by(id=request_id).first()
    product_id=purchase_orders.product_id
    if purchase_orders.status == "accepted":
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity - purchase_orders.quantity
    db.session.delete(purchase_orders)
    db.session.commit()
    return redirect ("/purchase-orders")

@app.route("/monthly-report")
def monthly_report():
    product_requests = ProductRequest.query.all()
    all_data = []
    for pr in product_requests:
        pr_date = datetime.datetime.strptime(pr.date, '%Y-%m-%d').date()
        if pr.status == "fulfilled" and pr_date.month == datetime.datetime.now().month:
            result_data = dict()
            result_data["program"] = pr.team
            result_data["date"] = pr.date 
            result_data["organisation"] = pr.organisation
            result_data["PO name"] = pr.user.email
            # result_data["purpose"] = pr.remarks
            result_data["medium"] = pr.master_product.language
            result_data["materials"] = pr.master_product.name
            result_data["quantity"] = pr.quantity
            all_data.append(result_data)
    keys = all_data[0].keys()

    csv_data = ''
    with open('Media/out.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)
    file_handle = open('Media/out.csv')
    csv_data = file_handle.read()
    return Response(csv_data, mimetype='text/csv', headers={'Content-disposition': 'attachment; filename=out.csv'})

    
    

    
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')


    
# if __name__ == "__main__":
#     app.run(debug=True)
