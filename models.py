
from sqlalchemy.dialects.postgresql import JSON



from app import db
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
