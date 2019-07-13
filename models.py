
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin


from app import db,login_manager



class Product(db.Model):
    
    __tablename__="products"

    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name= db.Column(db.String(255), nullable=False)
    type= db.Column(db.String(100), nullable=False)
    mrp= db.Column(db.Numeric(6,2), nullable=False)
    description= db.Column(db.String(200), nullable=False)
    dateadded= db.Column(db.String(30), nullable=False)
    dateupdated= db.Column(db.String(30), nullable=False)
    stock=db.relationship("Inventory", backref="product", lazy=True)
    language = db.Column(db.String(100), nullable=True, default="English")
    file_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Inventory(db.Model):
    
    __tablename__="inventories"
    product_id= db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity= db.Column(db.Integer)
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    description= db.Column(db.String(255), nullable=True)
    date= db.Column(db.String(30), nullable=False)
    price= db.Column(db.Integer, nullable=False)

class User(UserMixin,db.Model):

    __tablename__="users"
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    email=db.Column(db.String(100), nullable=False)
    role=db.Column(db.String(100), nullable=False)
    contact_number=db.Column(db.String, nullable=False)
    team=db.Column(db.String(100), nullable=False)
    password_hash=db.Column(db.String(128))
    def set_password(self, password):
        self.password_hash=generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        

class Vendor(db.Model):
    __tablename__="vendors"
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    name= db.Column(db.String(50), nullable=False)
    city= db.Column(db.String(20), nullable=False)
    GST= db.Column(db.Integer, nullable=False)
    contact_person= db.Column(db.String(100), nullable=False)
    contact_number= db.Column(db.String, nullable=False)
    remarks= db.Column(db.String(200), nullable=True)

class ProductRequest(db.Model):
    __tablename__="product_request"
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id= db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity= db.Column(db.Integer, nullable=False)
    user_id= db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date= db.Column(db.String(30), nullable=False)
    status= db.Column(db.String(30), nullable=True)
    organisation= db.Column(db.String(100), nullable=False)
    city= db.Column(db.String(50), nullable=False)
    state= db.Column(db.String(50), nullable=True)


class PurchaseOrders(db.Model):
    
    __tablename__="purchase_orders"
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id= db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity= db.Column(db.Integer)
    price= db.Column(db.Integer, nullable=False)
    vendor= db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    remarks= db.Column(db.String(200), nullable=True)
    date_added= db.Column(db.String(30), nullable=False)
    date_modified= db.Column(db.String(30), nullable=False)
