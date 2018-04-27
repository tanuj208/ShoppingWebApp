from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask import *
from sqlalchemy import *

Base = declarative_base()
engine = create_engine('sqlite:///user.db', echo=True)
Session = sessionmaker(bind=engine)
sqlsession = Session()


class User(Base):
    __tablename__ = "user"

    id = Column('id', Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column('username', String(255))
    name = Column('name', String(255))
    email = Column('email', String(255))
    mobile = Column('mobile', String(15))
    password = Column('password', String(255))
    isFormFilled = Column('isFormFilled', Integer)
    orders = relationship('Order', backref='user')
    logs = relationship('Logs', backref='user')


class Seller(Base):
    __tablename__ = "seller"

    # seller.id is same as user.id
    id = Column('id', Integer, primary_key=True)
    businessname = Column('businessname', String(255))
    shopaddress = Column('shopaddress', String(255))
    products = relationship('Product', backref='seller')
    logs = relationship('Logs', backref='seller')


class Product(Base):
    __tablename__ = 'product'
    # __searchable__ = ['name']

    id = Column('id', Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column('name', String(1000))
    price = Column('price', Integer)
    description = Column('description', String(1000))
    quantity = Column('quantity', Integer)
    imageName = Column('imageName', String(255))
    category_id = Column('category_id', Integer, ForeignKey('category.id'))
    seller_id = Column('seller_id', Integer, ForeignKey('seller.id'))
    orders = relationship('Order', backref='product')
    logs = relationship('Logs', backref='product')


class Category(Base):
    __tablename__ = "category"

    id = Column('id', Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column('name', String(255))
    products = relationship('Product', backref='category')


class Order(Base):
    __tablename__ = "order"

    id = Column('id', Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    product_quantity = Column('product_quantity', Integer)
    date = Column('date', DateTime)
    isOrdered = Column('isOrdered', Integer)
    # one means ordered otherwise in cart


class Logs(Base):
    __tablename__ = 'logs'

    id = Column('id', Integer, Sequence('user_id_seq'), primary_key=True)
    date = Column('date', DateTime)
    seller_id = Column('seller_id', Integer, ForeignKey('seller.id'))
    customer_id = Column('customer_id', Integer, ForeignKey('user.id'))
    product_id = Column('product_id', Integer, ForeignKey('product.id'))
    product_quantity = Column('product_quantity', Integer)
    address1 = Column('address1', String(255))
    address2 = Column('address2', String(255))
    city = Column('city', String(255))
    postcode = Column('postcode', String(255))
    country = Column('country', String(255))
    state = Column('state', String(255))


Base.metadata.create_all(bind=engine)
