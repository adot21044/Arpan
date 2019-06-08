from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import config
import datetime


app = Flask(__name__, static_url_path="/static")
app.config.from_object(config.Config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# model imports here
from models import *
db.create_all()
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
    from models import Product
    if request.form:
        print(request.form)
        data = request.form
        product = Product(name=data.get("name"), type=data.get("type"), mrp=data.get("mrp"), description=data.get(
            "description"), dateadded=str(datetime.datetime.now()), dateupdated=str(datetime.datetime.now()))
        db.session.add(product)
        db.session.commit()
    products = Product.query.all()

    return render_template("product.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)
