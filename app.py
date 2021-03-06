
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
login_manager = LoginManager()
login_manager.init_app(app)
# model imports here
from models import *


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


LOW_STOCK_THRESHOLD = 100
msg = Message("Dear Admin, An order has been placed, please place a purchase order", sender="arpaninventorymanagement@gmail.com",
              recipients=["fahim@arpan.org.in", "mayur@arpan.org.in"])

msg2 = Message("Dear Team Manager, your quarterly stock is running low", sender="arpaninventorymanagement@gmail.com", recipients=["fahim@arpan.org.in", "mayur@arpan.org.in"])



@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.route("/")
@login_required
def home():
    request_count = ProductRequest.query.count()
    team_pse_request = ProductRequest.query.filter_by(team="pse")
    team_pse_count = (team_pse_request.count())
    team_pe_request = ProductRequest.query.filter_by(team="pe")
    team_pe_count = (team_pe_request.count())
    team_training_request = ProductRequest.query.filter_by(team="training")
    team_training_count = (team_training_request.count())
    requestdata = dict()
    try:
        requestdata["pse"] = round((team_pse_count/request_count)*100, 0)
    except:
        requestdata["pse"] = 0
    try:
        requestdata["pe"] = round((team_pe_count/request_count)*100, 0)
    except:
        requestdata["pe"] = 0
    try:
        requestdata["training"] = round(
            (team_training_count/request_count)*100, 0)
    except:
        requestdata["training"] = 0
    try:
        requestdata["others"] = round(
            ((request_count-team_pse_count-team_pe_count-team_training_count)/request_count)*100, 0)
    except:
        requestdata["others"] = 0
    # product_count = product_request.master_product.name.query.count()
    # print("All: ", product_count)
    top_productdata = dict()
    total_requests = ProductRequest.query.all()
    # No filter applied
    for pr in total_requests:
        product_name = pr.master_product.name +' - '+ str(pr.master_product.language)
        top_productdata[product_name] = top_productdata.get(product_name, 0)+pr.quantity
    product_data = (sorted(top_productdata.items(),
                           key=lambda x: x[1], reverse=True))

    pending_requests = ProductRequest.query.filter_by(status="pending")
    pending_requests = pending_requests

    purchase_order = PurchaseOrders.query.filter_by(status="inproduction")
    purchase_order = purchase_order

    return render_template("dashboard.html", requestdata=requestdata, top_products=product_data, pending_requests=pending_requests, purchase_order=purchase_order)


@app.route("/team-home", methods=["GET", "POST"])
@login_required
def team_home():
    request_count = ProductRequest.query.count()
    team_pse_request = ProductRequest.query.filter_by(team="pse")
    team_pse_count = (team_pse_request.count())
    team_pe_request = ProductRequest.query.filter_by(team="pe")
    team_pe_count = (team_pe_request.count())
    team_training_request = ProductRequest.query.filter_by(team="training")
    team_training_count = (team_training_request.count())
    requestdata = dict()
    try:
        requestdata["pse"] = round((team_pse_count/request_count)*100, 0)
    except:
        requestdata["pse"] = 0
    try:
        requestdata["pe"] = round((team_pe_count/request_count)*100, 0)
    except:
        requestdata["pe"] = 0
    try:
        requestdata["training"] = round(
            (team_training_count/request_count)*100, 0)
    except:
        requestdata["training"] = 0
    try:
        requestdata["others"] = round(
            ((request_count-team_pse_count-team_pe_count-team_training_count)/request_count)*100, 0)
    except:
        requestdata["others"] = 0
    top_productdata = dict()
    total_requests = ProductRequest.query.all()
    # No filter applied
    for pr in total_requests:
        product_name = pr.master_product.name + ' - ' + str(pr.master_product.language)
        top_productdata[product_name] = top_productdata.get(
            product_name, 0)+pr.quantity
    product_data = (sorted(top_productdata.items(),
                           key=lambda x: x[1], reverse=True))
    return render_template("teamdashboard.html", top_products=product_data)


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
    top_productdata = dict()
    total_requests = QuarterlyRequest.query.all()
    # No filter applied
    for pr in total_requests:
        product_name = pr.master_product.name +' - '+ str(pr.master_product.language)
        top_productdata[product_name] = top_productdata.get(product_name, 0)+pr.quantity
    product_data = (sorted(top_productdata.items(),
                           key=lambda x: x[1], reverse=True))
    training_products= QuarterlyRequest.query.filter_by(team='training_team')
    pse_products = QuarterlyRequest.query.filter_by(team='pse')
    pe_products = QuarterlyRequest.query.filter_by(team='pe')
    other_products = QuarterlyRequest.query.filter_by(team='other')

    return render_template("inventory.html", stock=stock, products=products, product_data=product_data, training_products=training_products)


@app.route("/products", methods=["GET", "POST"])
def product():
    if request.form:
        print(request.form)
        data = request.form
        product = Product(name=data.get("name"), type=data.get("type"), mrp=data.get("mrp"), description=data.get(
            "description"), threshold=data.get("threshold"),dateadded=str(datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language=data.get("language"), version=data.get("version"), vendor=data.get("vendor"))
        if 'file_url' in request.files and data.get("file_url", '') != '':
            file_url = request.files['file_url']
            if file_url != '':
                filename = secure_filename(file_url.filename)
                print('FILE URL: ', file_url)# TODO image upload not working
                file_url.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.file_url = filename
        db.session.add(product)
        db.session.commit()
    products = Product.query.order_by(Product.dateupdated.desc())
    vendors = Vendor.query.all()

    return render_template("product.html", products=products, vendors=vendors)


@app.route("/product_edit_<product_id>", methods=["GET", "POST"])
def product_edit(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if request.form:
        data = request.form
        product.name = data.get("name")
        product.type=data.get("type")
        product.mrp=data.get("mrp")
        product.description=data.get("description")
        product.threshold=data.get("threshold")
        product.dateupdated=str(datetime.datetime.now())
        product.language=data.get("language")
        product.version=data.get("version")
        
        # if 'file_url' in request.files:
        #     file_url = request.files['file_url']
        #     filename = secure_filename(file_url.filename)
        #     file_url.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     product.file_url = filename
        # db.session.add(product)
        db.session.commit()
        return redirect(url_for('product'))
    vendors = Vendor.query.all()

    return render_template("product-edit.html", product=product, vendors=vendors)

# @app.route("/delete-product/<product_id>")
# def delete_product(product_id):
#     product = Product.query.filter_by(id=product_id).first()
#     inventory = Inventory.query.filter_by(product_id=product_id).first()
#     # db.session.delete(inventory)
#     db.session.delete(product)
#     db.session.commit()
#     return redirect("/products")


@app.route("/users", methods=["GET", "POST"])
def users():
    if request.form:
        print(request.form)
        data = request.form
        user = User(email=data.get("Email"), role=data.get("Role"),
                    contact_number=data.get("contact_number"), team=data.get("team"))
        user.set_password(data.get("Password"))
        db.session.add(user)
        db.session.commit()

    users = User.query.all()

    return render_template("users.html", users=users)

@app.route("/delete-user/<user_id>")
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect("/users")

@app.route("/reset-password_<user_id>", methods=["GET", "POST"])
def user_password_reset(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.form:
        data = request.form
        print(data)
        new_password = data.get('new_password')
        user.reset_password(new_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('user-password-reset.html', user=user)


@app.route("/vendors", methods=["GET", "POST"])
def vendor():
    if request.form:
        data = request.form
        vendor = Vendor(name=data.get("Name"), city=data.get("city"), gst_number=data.get("gst"), contact_person=data.get
                        ("contact_person"), contact_number=str(data.get("contact_number")), remarks=data.get("remarks"))
        db.session.add(vendor)
        db.session.commit()
    vendors = Vendor.query.all()
    return render_template("vendor.html", vendors=vendors)


@app.route("/login", methods=["GET", "POST"])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for("home"))
    if request.form:
        data = request.form
        user = User.query.filter_by(email=data.get("Email")).first()
        if user is None or not user.check_password(data.get("Password")):
            print("User not present or wrong password")
            return redirect(url_for("login"))
        print("user found")
        login_user(user)  # TODO
        print(user.role)
        if user.role == "admin":
            print('redirecting to home')
            return redirect("/")
        else:
            return redirect(url_for("team_home"))
    # form=Loginform()
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/product-requests", methods=["GET", "POST"])
def product_request():
    products = Product.query.all()
    product_requests = ProductRequest.query.order_by(
        ProductRequest.date.desc())
    quarterly_requests = QuarterlyRequest.query.filter_by(team=current_user.team).order_by(QuarterlyRequest.date.desc())
    if request.form:
        data = request.form
        product_request = ProductRequest(product_id=data.get("product"), quantity=data.get("quantity"),contact_person = data.get('contact_person', ''),
            user_id=current_user.id, date=data.get("date"), status="pending", organisation=data.get("organisation"), city=data.get("city", ""), returns=data.get("returns"), team=current_user.team)
        quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=current_user.team).first()
        if quarterly_product_request is None:
            return render_template("teamproductrequest.html", products=products, product_requests=product_requests, quarterly_requests=quarterly_requests, error='You don\'t have any Quarterly Request for the product, please place quarterly request first.') 
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(
                product_id=data.get("product")).first()
            if inventory is not None:
                quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=data.get("team")).first()
                inventory.quantity = inventory.quantity - \
                    int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    mail.send(msg2) 
                    pass
                quarterly_product_request.quantity = quarterly_product_request.quantity - product_request.quantity    
                db.session.add(inventory)
            else:
                return render_template("productrequest.html", products=products, product_requests=product_requests, error='You don\'t have any Inventory for the product, please place purchase order first to update Inventory.')
        db.session.add(product_request)
        db.session.commit()
    return render_template("productrequest.html", products=products, product_requests=product_requests, error='')


@app.route("/team-product-requests", methods=["GET", "POST"])
def team_product_request():
    products = Product.query.all()
    product_requests = ProductRequest.query.filter_by(team=current_user.team).order_by(
        ProductRequest.date.desc())
    quarterly_requests = QuarterlyRequest.query.filter_by(team=current_user.team).order_by(QuarterlyRequest.date.desc())
    if request.form:
        data = request.form
        product_request = ProductRequest(product_id=data.get("product"), quantity=data.get("quantity"), contact_person = data.get('contact_person', ''),
            user_id=current_user.id, date=data.get("date"), status="pending", organisation=data.get("organisation"), city=data.get("city", ""), returns=data.get("returns"), team=current_user.team)
        quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=current_user.team).first()
        if quarterly_product_request is None:
            return render_template("teamproductrequest.html", products=products, product_requests=product_requests, quarterly_requests=quarterly_requests, error='You don\'t have any Quarterly Request for the product, please place quarterly request first.')
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(
                product_id=data.get("product")).first()
            if inventory is not None:
                quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=data.get("team")).first()
                inventory.quantity = inventory.quantity - \
                    int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    mail.send(msg2) 
                    pass
                quarterly_product_request.quantity = quarterly_product_request.quantity - product_request.quantity    
                db.session.add(inventory)
        db.session.add(product_request)
        db.session.commit()
    return render_template("teamproductrequest.html", products=products, product_requests=product_requests, quarterly_requests=quarterly_requests, error='')

@app.route("/product-request_edit<request_id>", methods=["GET", "POST"])
def product_request_edit(request_id):
    product_requests = ProductRequest.query.filter_by(id=request_id).first()
    vendors = Vendor.query.all()
    products = Product.query.all()
    if request.form:
        data = request.form
        product_requests.name = data.get("name")
        product_requests.quantity=int(data.get("quantity"))
        product_requests.price=data.get("price")
        product_requests.vendor=data.get("vendor")
        product_requests.remarks=data.get("remarks")
        product_requests.dateplaced=data.get("dateplaced")
        product_requests.status=data.get("status")
        if data.get("status") == "fulfilled":
            inventory = Inventory.query.filter_by(
                product_id=data.get("product")).first()
            if inventory is not None:
                quarterly_product_request_object = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=data.get("team")).first()
                inventory.quantity = inventory.quantity - \
                    int(data.get("quantity"))
                if inventory.quantity < LOW_STOCK_THRESHOLD:
                    mail.send(msg2) 
                    pass
                quarterly_product_request_object.quantity = int(quarterly_product_request_object.quantity) - product_requests.quantity    
                db.session.add(inventory)
                db.session.add(quarterly_product_request_object)
            else:
                return render_template("product_request_edit.html", products=products, vendors=vendors, product_request=product_requests, error='You don\'t have any Inventory for the product, please place purchase order first to update Inventory.')
        db.session.commit()
        return redirect(url_for('product_request'))
    
    return render_template("product_request_edit.html", products=products, vendors=vendors, product_request=product_requests, error='')  


@app.route("/delete-product-request/<request_id>")
def delete_product_request(request_id):
    productrequest = ProductRequest.query.filter_by(id=request_id).first()
    product_id = productrequest.product_id
    if productrequest.status == "fulfilled":
        quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=product_id, team=productrequest.team).first()
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity + productrequest.quantity
        quarterly_product_request.quantity = quarterly_product_request.quantity + productrequest.quantity
        db.session.add(quarterly_product_request)
        db.session.add(inventory)
    db.session.delete(productrequest)
    db.session.commit()
    return redirect("/product-requests")


@app.route("/team-delete-product-request/<request_id>")
def team_delete_product_request(request_id):
    productrequest = ProductRequest.query.filter_by(id=request_id).first()
    product_id = productrequest.product_id
    if productrequest.status == "fulfilled":
        quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=product_id, team=product_request.team).first()
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity + productrequest.quantity
        quarterly_product_request.quantity = quarterly_product_request + productrequest.quantity
    db.session.delete(productrequest)
    db.session.commit()
    return redirect("/team-product-requests")


@app.route("/purchase-orders", methods=["GET", "POST"])
def purchase_orders():
    if request.form:

        data = request.form
        purchase_orders = PurchaseOrders(product_id=data.get("product"), price=data.get("price"), vendor=data.get("vendor"), quantity=data.get(
            "quantity"), remarks=data.get("remarks"), date_added=str(datetime.datetime.now()), date_modified=str(datetime.datetime.now()), status=data.get("status"), order_number=data.get("ordernumber"))
        if data.get("status") == "accepted":
            inventory = Inventory.query.filter_by(product_id=data.get(
                "product"), vendor=data.get("vendor")).first()
            if inventory is not None:
                inventory.quantity = inventory.quantity + \
                    int(data.get("quantity"))
            else:
                inventory = Inventory(product_id=data.get("product"), price=data.get("price"), quantity=data.get(
                    "quantity"), date=str(datetime.datetime.now()), vendor=data.get("vendor"))
            db.session.add(inventory)
        db.session.add(purchase_orders)
        db.session.commit()
        # Purchase Order Message TODO
    stock = PurchaseOrders.query.order_by(PurchaseOrders.date_added.desc())
    products = Product.query.all()
    vendors = Vendor.query.all()
    top_productdata = dict()
    total_requests = QuarterlyRequest.query.all()
    # No filter applied
    for pr in total_requests:
        product_name = pr.master_product.name +' - '+ str(pr.master_product.language)
        top_productdata[product_name] = top_productdata.get(product_name, 0)+pr.quantity
    product_data = (sorted(top_productdata.items(),
                           key=lambda x: x[1], reverse=True))
    return render_template("purchaseorder.html", stock=stock, products=products, vendors=vendors, product_data = product_data)


@app.route("/delete-purchase-order/<request_id>")
def delete_purchase_order(request_id):
    purchase_orders = PurchaseOrders.query.filter_by(id=request_id).first()
    product_id = purchase_orders.product_id
    if purchase_orders.status == "accepted":
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        inventory.quantity = inventory.quantity - purchase_orders.quantity
    db.session.delete(purchase_orders)
    db.session.commit()
    return redirect("/purchase-orders")

@app.route("/delete-product/<product_id>")
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    db.session.delete(product)
    db.session.commit()
    return redirect("/products")


@app.route("/purchase-order_edit<request_id>", methods=["GET", "POST"])
def purchase_order_edit(request_id):
    purchase_orders = PurchaseOrders.query.filter_by(id=request_id).first()
    if request.form:
        data = request.form
        purchase_orders.name = data.get("name")
        purchase_orders.quantity=data.get("quantity")
        purchase_orders.price=data.get("price")
        purchase_orders.vendor=data.get("vendor")
        purchase_orders.remarks=data.get("remarks")
        purchase_orders.date_added=data.get("date_added")
        purchase_orders.status=data.get("status")
        purchase_orders.order_number=data.get("ordernumber")
        db.session.commit()
        return redirect(url_for('purchase_orders'))
    vendors = Vendor.query.all()
    products= Product.query.all()
    print(purchase_orders.date_added)
    date_added = purchase_orders.date_added.split(' ')[0]
    print(purchase_orders.vendor)
    return render_template("purchase_order_edit.html", products=products, vendors=vendors, purchase_order=purchase_orders, date_added=date_added)  


@app.route("/monthly-report")
def monthly_report():
    product_requests = ProductRequest.query.all()
    all_data = []
    for pr in product_requests:
        try:
            pr_date = datetime.datetime.strptime(pr.date, '%d/%m/%Y').date()
        except:            
            pr_date = datetime.datetime.strptime(pr.date, '%Y-%m-%d').date()
        if pr.status == "fulfilled" and pr_date.month == datetime.datetime.now().month:
            result_data = dict()
            result_data["program"] = pr.team
            result_data["date"] = pr.date
            result_data["organisation"] = pr.organisation
            result_data["PO name"] = pr.user.email
            result_data["returns"] = pr.returns
            result_data["medium"] = pr.master_product.language
            result_data["materials"] = pr.master_product.name
            result_data["quantity"] = pr.quantity
            result_data["returns"] = pr.returns
            all_data.append(result_data)
    keys = ['program', 'date', 'organisation',
            'PO name', 'purpose', 'medium', 'materials', 'quantity', 'returns']
    print(keys)
    csv_data = ''
    with open('Media/out.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data)
    file_handle = open('Media/out.csv')
    csv_data = file_handle.read()
    return Response(csv_data, mimetype='text/csv', headers={'Content-disposition': 'attachment; filename=out.csv'})


@app.route("/data")
def import_data():
    data = []
    with open('Media/upload_data.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            cost = row[4]
            if(cost == ''):
                cost = '0'
            data.append({
                "Name": row[0],
                "English": row[1],
                "Hindi": row[2],
                "Marathi": row[3],
                "Cost": int(cost),
                "Vendor Details": row[5],
            })
            
        for entry in data:
            if(entry.get("English") != '' and entry.get("English") != '0'):
                product = Product(name=entry.get("Name"), type="Normal", mrp=int(entry.get("Cost")), description="", dateadded=str(
                    datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language="English", version='1')
            if(entry.get("Hindi") != '' and entry.get("Hindi") != '0'):
                product = Product(name=entry.get("Name"), type="Normal", mrp=int(entry.get("Cost")), description="", dateadded=str(
                    datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language="Hindi", version='1')
            if(entry.get("Marathi") != '' and entry.get("Marathi") != '0'):
                product = Product(name=entry.get("Name"), type="Normal", mrp=int(entry.get("Cost")), description="", dateadded=str(
                    datetime.datetime.now()), dateupdated=str(datetime.datetime.now()), language="Marathi", version='1')

            db.session.add(product)
            db.session.commit()
    
    return Response("Done")

@app.route("/quarterly-product-requests", methods=["GET", "POST"])
def quarterly_product_requests():
    if request.form:
        data = request.form
        quarterly_request = QuarterlyRequest(product_id=data.get("product"), quantity=data.get("quantity"),
            user_id=current_user.id, date=data.get("date"),team=current_user.team, quarter_month=data.get("quarter_month"), year=data.get("year"))
        db.session.add(quarterly_request)
        db.session.commit()
    products = Product.query.all()
    quarterly_requests = QuarterlyRequest.query.filter_by(team=current_user.team).order_by(
        QuarterlyRequest.date.desc())
    # quarterly_product_request = QuarterlyRequest.query.filter_by(product_id=data.get("product"), team=data.get("team")).first()
    msg = Message("Dear Admin, An order has been placed, please place a purchase order", sender="arpaninventorymanagement@gmail.com",
              recipients=["fahim@arpan.org.in", "mayur@arpan.org.in"])    
    msg.body = ('A quarterly request has been made by a team, please purchase purchase order')
    mail.send(msg)
    # inventory.quantity = inventory.quantity + quarterly_product_request.quantity
    return render_template("quarterlyproductrequests.html", products=products, quarterly_requests=quarterly_requests)

def send_mail(subject, body):
    msg = Message(subject=subject,body=body, sender="arpaninventorymanagement@gmail.com",
              recipients=["fahim@arpan.org.in", "mayur@arpan.org.in"])    
    mail.send(msg)


if __name__ == "__main__":
    app.run(host='0.0.0.0')


# if __name__ == "__main__":
#     app.run(debug=True)
