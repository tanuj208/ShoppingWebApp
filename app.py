from flask import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from flask.ext.hashing import Hashing
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from datetime import datetime
from whooshalchemy import IndexService
import os

app=Flask(__name__)
Base = declarative_base()
hashing=Hashing(app)
images=UploadSet('images', IMAGES)

app.config['UPLOADED_IMAGES_DEST']='static/img'
# app.config['WHOOSH_BASE'] = 'temp/'
configure_uploads(app,images)
config = {"WHOOSH_BASE": "tmp/whoosh"}

class User(Base):
	__tablename__ = "user"

	id = Column('id', Integer,Sequence('user_id_seq'),primary_key=True)
	username=Column('username',String(255))
	name = Column('name',String(255))
	email = Column('email',String(255))
	mobile = Column('mobile',String(15))
	password = Column('password',String(255))
	isFormFilled=Column('isFormFilled',Integer)
	orders=relationship('Order',backref='user')

class Seller(Base):
	__tablename__="seller"

	# seller.id is same as user.id
	id=Column('id',Integer,primary_key=True)
	businessname=Column('businessname',String(255))
	shopaddress=Column('shopaddress',String(255))
	products=relationship('Product',backref='seller')

class Product(Base):
	__tablename__="product"
	__searchable__ = ['name']

	id=Column('id',Integer,Sequence('user_id_seq'),primary_key=True)
	name=Column('name',String(255))
	price=Column('price',Integer)
	description=Column('description',String(1000))
	quantity=Column('quantity',Integer)
	imageName=Column('imageName',String(255))
	category_id=Column('category_id',Integer,ForeignKey('category.id'))
	seller_id=Column('seller_id',Integer,ForeignKey('seller.id'))
	orders=relationship('Order',backref='product')

class Category(Base):
	__tablename__="category"

	id=Column('id',Integer,Sequence('user_id_seq'),primary_key=True)
	name = Column('name',String(255))
	products=relationship('Product',backref='category')

class Order(Base):
	__tablename__="order"

	id=Column('id',Integer,Sequence('user_id_seq'),primary_key=True)
	user_id=Column('user_id',Integer,ForeignKey('user.id'))
	product_id = Column('product_id',Integer,ForeignKey('product.id'))
	product_quantity = Column('product_quantity',Integer)
	date = Column('date',DateTime)
	isOrdered = Column('isOrdered',Integer)
	# one means ordered otherwise in cart

class Logs(Base):
	__tablename__='logs'
	id=Column('id',Integer,Sequence('user_id_seq'),primary_key=True)
	date = Column('date',DateTime)
	seller_id=Column('seller_id',Integer)
	customer_id=Column('customer_id',Integer)
	product_id=Column('product_id',Integer)
	product_quantity=Column('product_quantity',Integer)
	address1 = Column('address1',String(255))
	address2 = Column('address2',String(255))
	city = Column('city',String(255))
	postcode = Column('postcode',String(255))
	country = Column('country',String(255))
	state = Column('state',String(255))

# whoosh_index(app,Product)
engine=create_engine('sqlite:///user.db',echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
sqlsession = Session()
index_service = IndexService(config=config, session=sqlsession)
index_service.register_class(Product)

@app.route('/')
@app.route('/<username>')
def index(username=None):
	products=sqlsession.query(Product).all()
	return render_template("index.html",products=products,size=len(products))

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method=='POST':
		password=str(request.form['password'])
		username=str(request.form['username'])
		user = sqlsession.query(User).filter_by(username=username).first()
		if username=='' or hashing.check_value(password,'',salt='abcd'):
			return render_template("register.html",error1="Fields can't be empty",error2=None)
		if user is None:
			return render_template("register.html",error1="Username does not exist!",error2=None)
		elif hashing.check_value(user.password,password,salt='abcd'):
			sqlsession.add(user)
			sqlsession.commit()
			session['user']=user.username
			return redirect(url_for('index',name=user.username))
		elif not hashing.check_value(user.password,password,salt='abcd'):
			return render_template("register.html",error1="Wrong Password!",error2=None)
	return render_template('register.html',error1=None, error2=None)

@app.route('/logout')
def logout():
	session.pop('user')
	return redirect(url_for('index'))

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method=='POST':
		error=None
		user = User()
		user.username=str(request.form['username'])
		user.email=str(request.form['email'])
		user.name=str(request.form['name'])
		user.mobile=str(request.form['tel'])
		password=str(request.form['password'])
		confirm=str(request.form['confirmation'])
		user.isFormFilled=0

		if user.username=='' or user.email=='' or user.name=='' or user.mobile=='' or password=='' or confirm=='':
			error="Field can't be empty"
		elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(password):
			error="Password can't contain special charaters"
		elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.username):
			error="Username can't contain special charaters"
		elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.name):
			error="Name can't contain special charaters"
		elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.mobile):
			error="Mobile can't contain special charaters"
		elif len(password)<8:
			error="Password should be more than 8 characters"
		elif confirm!=password:
			error="Passwords do not match"
		elif sqlsession.query(User).filter_by(username=user.username).first() is not None:
			error="Username already exists"
		elif sqlsession.query(User).filter_by(email=user.email).first() is not None:
			error="Email already exists"
		elif sqlsession.query(User).filter_by(mobile=user.mobile).first() is not None:
			error="Mobile number already exists"
		if error:
			return render_template('register.html',error1=None, error2=error)

		user.password=hashing.hash_value(password,salt='abcd')
		sqlsession.add(user)
		sqlsession.commit()
		session['user']=user.username
		return redirect(url_for('index',username=user.username))
	return render_template('register.html',error1=None, error2=None)

@app.route('/sell', methods=['GET','POST'])
def sell():
	if request.method=='POST':
		error=None
		seller=Seller()
		user=sqlsession.query(User).filter_by(username=session['user']).first()
		seller.id=user.id
		seller.businessname=str(request.form['businessname'])
		seller.shopaddress=str(request.form['shopaddress'])

		if seller.shopaddress=='' or seller.businessname=='':
			error="Field can't be empty"
		elif sqlsession.query(Seller).filter_by(businessname=seller.businessname).first() is not None:
			error="Businessname already exists"
		if error:
			return render_template('sell.html',error=error)

		user.isFormFilled=1
		sqlsession.add(seller)
		sqlsession.commit()

		return redirect(url_for('addProduct'))
	flag=sqlsession.query(User).filter_by(username=session['user']).first().isFormFilled
	if flag==1:
		return redirect(url_for('addProduct'))
	else:
		return render_template('sell.html',error=None)

@app.route('/addProduct',methods=['GET','POST'])
def addProduct():
	if request.method=='POST':
		error=None
		product=Product()
		product.name=str(request.form['itemName'])
		product.price=int(request.form['itemPrice'])
		product.description=str(request.form['itemDescription'])
		product.quantity=int(request.form['quantity'])
		categoryName=str(request.form['categoryName'])
		user=sqlsession.query(User).filter_by(username=session['user']).first()
		seller=sqlsession.query(Seller).filter_by(id=user.id).first()

		try:
			product.imageName=images.save(request.files['image'])
		except:
			error="Upload image first"
		if product.name=='' or product.description=='' or categoryName=='':
			error="Fields can't be empty"
		elif product.quantity == 0:
			error = "Add atleast one item"
		elif product.quantity < 0 or product.price < 0:
			error = "negative figures are not allowed"

		if error:
			return render_template('addProduct.html',error=error,categories=sqlsession.query(Category).all())
		
		category=sqlsession.query(Category).filter_by(name=categoryName).first()
		product.category=category
		product.seller=seller

		sqlsession.add(product)
		sqlsession.commit()
		return redirect(url_for('index',username=session['user']))
	return render_template('addProduct.html',error=None,categories=sqlsession.query(Category).all())

@app.route('/product_detail',methods=['POST','GET'])
@app.route('/product_detail/<productid>',methods=['POST','GET'])
def product_detail(productid=None):
	if request.method == 'POST':
		error=None
		product = sqlsession.query(Product).filter_by(id=productid).first()
		user = sqlsession.query(User).filter_by(username=session['user']).first()
		order = sqlsession.query(Order).filter_by(user_id=user.id,isOrdered=0,product_id=product.id).first()
		stock = product.quantity
		quantity = int(request.form['product_quantity'])
		if stock == 0:
			error = "Product is out of stock"
		elif stock < quantity:
			error = "Only " + str(stock) +" pieces are left"
		elif quantity <= 0:
			error = "figures can't be negative or zero"
		if error:
			return render_template('product_detail.html',product=product,error=error)
		if order == None:
			order=Order()
			order.user = user
			order.product = product
			order.product_quantity = quantity
			order.isOrdered = 0
			sqlsession.add(order)
		else:
			order.product_quantity += quantity
		sqlsession.commit()
		return render_template('product_detail.html',product=product,error=None)
	product=sqlsession.query(Product).filter_by(id=productid).first()
	return render_template('product_detail.html',product=product,error=None)

@app.route('/category')
@app.route('/category/<category_id>')
@app.route('/category/<category_id>/<page_number>')
def category_filter(category_id=None,page_number=None):
	products=sqlsession.query(Product).filter_by(category_id=category_id).all()
	if page_number == None:
		page_number = 1
		startIndex = 0
	else:
		startIndex=(page_number-1)*9-1;
	return render_template('products.html',products=products,startIndex=startIndex,size=len(products),page_number=page_number)

@app.route('/search',methods=['POST','GET'])
@app.route('/search/<page_number>',methods=['POST','GET'])
def search(page_number=None):
	text=request.form['search']
	products=list(Product.search_query(text))
	# products=sqlsession.query(Product).whoosh_search(text).all()
	if page_number == None:
		page_number = 1
		startIndex = 0
	else:
		startIndex = (page_number-1)*9-1;
	# return render_template('test.html',data1=text,data2="DD")
	return render_template('products.html',products=products,startIndex=startIndex,size=len(products),page_number=page_number)

@app.route('/cart',methods=['POST','GET'])
@app.route('/cart/<username>',methods=['POST','GET'])
def cart(username=None):
	user = sqlsession.query(User).filter_by(username=session['user']).first()
	cartDetails = sqlsession.query(Order).filter_by(user_id=user.id,isOrdered=0).all()
	if request.method == 'POST':
		ids=request.form.getlist("to_delete")
		for itemId in ids:
			toDelete=sqlsession.query(Order).filter_by(id=int(itemId)).first()
			sqlsession.delete(toDelete)
		sqlsession.commit()

	cartDetails = sqlsession.query(Order).filter_by(user_id=user.id,isOrdered=0).all()
	totalPrice = 0
	for item in cartDetails:
		totalPrice=totalPrice+(int(item.product.price)*(int)(item.product_quantity))
	return render_template('cart.html',cartDetails=cartDetails,totalPrice=totalPrice)

@app.route('/checkout',methods=['POST','GET'])
@app.route('/checkout/<username>',methods=['POST','GET'])
def checkout(username=None):
	user = sqlsession.query(User).filter_by(username=session['user']).first()
	cartDetails = sqlsession.query(Order).filter_by(user_id=user.id,isOrdered=0).all()
	totalPrice=0		
	for item in cartDetails:
		totalPrice=totalPrice+(int(item.product.price)*(int)(item.product_quantity))

	if request.method == 'POST':
		date=datetime.now()
		for item in cartDetails:
			item.date=date
			item.isOrdered=1
			product = sqlsession.query(Product).filter_by(id=item.product_id).first()
			product.quantity-=item.product_quantity
		sqlsession.commit()
		return render_template('placed.html',totalPrice=(totalPrice*1.17))

	return render_template('checkout.html',user=user,cartDetails=cartDetails,totalPrice=totalPrice)

@app.route('/usertable')
def usertable():
	user = sqlsession.query(User).all()
	return render_template('table.html',rows=user,message="USERS ::")

@app.route('/sellertable')
def sellertable():
	sellers=sqlsession.query(Seller).all()
	return render_template('sellertable.html',rows=sellers,message="SELLERS ::")

@app.route('/productTable')
def productTable():
	products=sqlsession.query(Product).all()
	return render_template('productTable.html',rows=products,message="PRODUCTS ::")

@app.route('/orderTable')
def orderTable():
	orders=sqlsession.query(Order).all()
	return render_template('orderTable.html',rows=orders,message="ORDERS ::")

if __name__=='__main__':
	app.secret_key=os.urandom(12)
	app.run(debug=True)
