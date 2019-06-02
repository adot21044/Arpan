from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3
import config
import datetime
project_dir=os.path.dirname(os.path.abspath(__file__))
database_file="sqlite:///{}".format(os.path.join(project_dir,"arpandatabase.db"))


app= Flask(__name__, static_url_path="/static")
app.config.from_object(config.Config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)
# app.config["SQLALCHEMY_DATABASE_URI"]= database_file

# with app.app_context():
#     db.init_app(app)



from models import Product, Inventory
@app.route("/")
def home():
    db.create_all()
    return render_template("dashboard.html")

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.form:
        print(request.form)
        data=request.form
        inventory=Inventory(product_id=data.get("product"), price=data.get("price"), quantity=data.get("quantity"), description=data.get("description"), date=str(datetime.datetime.now()))
        db.session.add(inventory)
        db.session.commit()
    stock=Inventory.query.all()
    products=Product.query.all()
    return render_template("inventory.html", stock=stock, products=products)

@app.route("/products", methods=["GET", "POST"])
def product():
    if request.form:
        print(request.form)
        data=request.form
        product=Product(name=data.get("name"), type=data.get("type"), mrp=data.get("mrp"), description=data.get("description"), dateadded=str(datetime.datetime.now()), dateupdated=str(datetime.datetime.now()))
        db.session.add(product)
        db.session.commit()
    products=Product.query.all()



    return render_template("product.html", products=products)




if __name__=="__main__":
    app.run(debug=True)