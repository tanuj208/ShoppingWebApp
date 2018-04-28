from flask import *
from sqlalchemy import *
from flask.ext.hashing import Hashing
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from datetime import datetime
from model import *
import os

app = Flask(__name__)
hashing = Hashing(app)
images = UploadSet('images', IMAGES)

app.config['UPLOADED_IMAGES_DEST'] = 'static/img'
configure_uploads(app, images)


@app.route('/')
@app.route('/<username>')
def index(username=None):
    products = sqlsession.query(Product).all()
    return render_template("index.html", products=products, size=len(products))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        password = str(request.form['password'])
        username = str(request.form['username'])
        user = sqlsession.query(User).filter_by(username=username).first()
        if username == '' or hashing.check_value(password, '', salt='abcd'):
            return render_template("register.html", error1="Fields can't be empty", error2=None)
        if user is None:
            return render_template("register.html", error1="Username does not exist!", error2=None)
        elif hashing.check_value(user.password, password, salt='abcd'):
            sqlsession.add(user)
            sqlsession.commit()
            session['user'] = user.username
            return redirect(url_for('index', name=user.username))
        elif not hashing.check_value(user.password, password, salt='abcd'):
            return render_template("register.html", error1="Wrong Password!", error2=None)
    return render_template('register.html', error1=None, error2=None)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        error = None
        user = User()
        user.username = str(request.form['username'])
        user.email = str(request.form['email'])
        user.name = str(request.form['name'])
        user.mobile = str(request.form['tel'])
        password = str(request.form['password'])
        confirm = str(request.form['confirmation'])
        user.isFormFilled = 0

        if user.username == '' or user.email == '' or user.name == '' or user.mobile == '' or password == '' or confirm == '':
            error = "Fields can't be empty"
        elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(password):
            error = "Password can't contain special characters"
        elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.username):
            error = "Username can't contain special characters"
        elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.name):
            error = "Name can't contain special characters"
        elif set('[~!@#$%^&*()-_+={}":;\']+$\\/.,<>').intersection(user.mobile):
            error = "Mobile can't contain special characters"
        elif len(password) < 8:
            error = "Password should be more than 8 characters"
        elif confirm != password:
            error = "Passwords do not match"
        elif sqlsession.query(User).filter_by(username=user.username).first() is not None:
            error = "Username already exists"
        elif sqlsession.query(User).filter_by(email=user.email).first() is not None:
            error = "Email already exists"
        elif sqlsession.query(User).filter_by(mobile=user.mobile).first() is not None:
            error = "Mobile number already exists"
        if error:
            return render_template('register.html', error1=None, error2=error)

        user.password = hashing.hash_value(password, salt='abcd')
        sqlsession.add(user)
        sqlsession.commit()
        session['user'] = user.username
        return redirect(url_for('index', username=user.username))
    return render_template('register.html', error1=None, error2=None)


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        error = None
        seller = Seller()
        user = sqlsession.query(User).filter_by(
            username=session['user']).first()
        seller.id = user.id
        seller.businessname = str(request.form['businessname'])
        seller.shopaddress = str(request.form['shopaddress'])

        if seller.shopaddress == '' or seller.businessname == '':
            error = "Fields can't be empty"
        elif sqlsession.query(Seller).filter_by(businessname=seller.businessname).first() is not None:
            error = "Businessname already exists"
        if error:
            return render_template('sell.html', error=error)

        user.isFormFilled = 1
        sqlsession.add(seller)
        sqlsession.commit()

        return redirect(url_for('addProduct'))
    flag = sqlsession.query(User).filter_by(
        username=session['user']).first().isFormFilled
    if flag == 1:
        return redirect(url_for('addProduct'))
    else:
        return render_template('sell.html', error=None)


@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        error = None
        product = Product()
        product.name = str(request.form['itemName'])
        product.price = int(request.form['itemPrice'])
        product.description = str(request.form['itemDescription'])
        product.quantity = int(request.form['quantity'])
        categoryName = str(request.form['categoryName'])
        user = sqlsession.query(User).filter_by(
            username=session['user']).first()
        seller = sqlsession.query(Seller).filter_by(id=user.id).first()

        try:
            product.imageName = images.save(request.files['image'])
        except:
            error = "Upload image first"
        if product.name == '' or product.description == '' or categoryName == '':
            error = "Fields can't be empty"
        elif product.quantity == 0:
            error = "Add atleast one item"
        elif product.quantity < 0 or product.price < 0:
            error = "Negative figures are not allowed"

        if error:
            return render_template('addProduct.html', error=error, categories=sqlsession.query(Category).all())

        category = sqlsession.query(Category).filter_by(
            name=categoryName).first()
        product.category = category
        product.seller = seller

        sqlsession.add(product)
        sqlsession.commit()
        return redirect(url_for('index', username=session['user']))
    return render_template('addProduct.html', error=None, categories=sqlsession.query(Category).all())


@app.route('/product_detail', methods=['POST', 'GET'])
@app.route('/product_detail/<productid>', methods=['POST', 'GET'])
def product_detail(productid=None):
    if request.method == 'POST':
        error = None
        product = sqlsession.query(Product).filter_by(id=productid).first()
        similarProducts = sqlsession.query(Product).filter_by(
            category=product.category).all()
        size = len(similarProducts)
        stock = product.quantity
        quantity = int(request.form['product_quantity'])
        if "user" not in session:
            error = "Please login first"
        elif stock == 0:
            error = "Product is out of stock"
        elif stock < quantity:
            error = "Only " + str(stock) + " pieces are left"
        elif quantity <= 0:
            error = "figures can't be negative or zero"
        if error:
            return render_template('product_detail.html', product=product, similarProducts=similarProducts, size=size, error=error)
        user = sqlsession.query(User).filter_by(
            username=session['user']).first()
        order = sqlsession.query(Order).filter_by(
            user_id=user.id, isOrdered=0, product_id=product.id).first()
        if order == None:
            order = Order()
            order.user = user
            order.product = product
            order.product_quantity = quantity
            order.isOrdered = 0
            sqlsession.add(order)
        else:
            order.product_quantity += quantity
        sqlsession.commit()
        return render_template('product_detail.html', product=product, similarProducts=similarProducts, size=size, error=None)
    product = sqlsession.query(Product).filter_by(id=productid).first()
    similarProducts = sqlsession.query(Product).filter_by(
        category=product.category).all()
    size = len(similarProducts)
    return render_template('product_detail.html', product=product, similarProducts=similarProducts, size=size, error=None)


@app.route('/category')
@app.route('/category/<category_id>')
@app.route('/category/<category_id>/<page_number>')
def category_filter(category_id=None, page_number=None):
    products = sqlsession.query(Product).filter_by(
        category_id=category_id).all()
    if page_number == None:
        page_number = 1
        startIndex = 0
    else:
        page_number = int(page_number)
        startIndex = (page_number-1)*9-1
    url="/category/"+str(category_id)
    return render_template('products.html', products=products, startIndex=startIndex, size=len(products), page_number=page_number,url=url)


@app.route('/price', methods=['POST', 'GET'])
def filter_by_price(start_price=None, end_price=None, page_number=None):
    if request.method == 'POST':
        productIds = request.form.getlist("productIds")

        start_price = request.form["start_price"]
        end_price = request.form["end_price"]

        products = []
        for productId in productIds:
            product = sqlsession.query(Product).filter_by(id=productId).first()
            if int(product.price) >= int(start_price) and int(product.price) <= int(end_price):
                products.append(product)
        if page_number == None:
            page_number = 1
            startIndex = 0
        else:
            startIndex = (page_number-1)*9 - 1
        url="/price"
        return render_template('products.html', products=products, startIndex=startIndex, size=len(products), page_number=page_number,url=url)


@app.route('/search', methods=['POST', 'GET'])
@app.route('/search/<page_number>', methods=['POST', 'GET'])
def search(page_number=None):
    text = request.form['search']
    products = sqlsession.query(Product).filter(
        Product.name.like('%'+text+'%')).all()
    if page_number == None:
        page_number = 1
        startIndex = 0
    else:
        startIndex = (page_number-1)*9-1
    url="/search"
    return render_template('products.html', products=products, startIndex=startIndex, size=len(products), page_number=page_number,url=url)


@app.route('/cart', methods=['POST', 'GET'])
@app.route('/cart/<username>', methods=['POST', 'GET'])
def cart(username=None):
    user = sqlsession.query(User).filter_by(username=session['user']).first()
    cartDetails = sqlsession.query(Order).filter_by(
        user_id=user.id, isOrdered=0).all()
    if request.method == 'POST':
        ids = request.form.getlist("to_delete")
        for itemId in ids:
            toDelete = sqlsession.query(
                Order).filter_by(id=int(itemId)).first()
            sqlsession.delete(toDelete)
        sqlsession.commit()
    cartDetails = sqlsession.query(Order).filter_by(
        user_id=user.id, isOrdered=0).all()
    totalPrice = 0
    errorlist = []
    error = None
    for item in cartDetails:
        totalPrice = totalPrice + \
            (int(item.product.price)*(int)(item.product_quantity))
        product = sqlsession.query(Product).filter_by(
            id=item.product_id).first()
        if product.quantity-item.product_quantity < 0:
            errorlist.append(product)
            error = "The Following Products : "
    for item in errorlist:
        error += item.name + "; "
    if error:
        error += "are not available. Please reduce quantity and try again!"
    if len(cartDetails) == 0:
        error = "Cart is Empty!!! Add Products to Checkout"
    return render_template('cart.html', cartDetails=cartDetails, totalPrice=totalPrice, error=error)


@app.route('/checkout', methods=['POST', 'GET'])
@app.route('/checkout/<username>', methods=['POST', 'GET'])
def checkout(username=None):
    user = sqlsession.query(User).filter_by(username=session['user']).first()
    cartDetails = sqlsession.query(Order).filter_by(
        user_id=user.id, isOrdered=0).all()
    totalPrice = 0
    error = None
    for item in cartDetails:
        totalPrice = totalPrice + \
            (int(item.product.price)*(int)(item.product_quantity))

    if request.method == 'POST':
        date = datetime.now()

        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        postcode = request.form['postcode']
        country = request.form['country']
        state = request.form['state']

        if address1 == '' or city == '' or postcode == '' or country == '' or state == '':
            error = "Fields can't be empty"
        if error:
            return render_template('checkout.html', user=user, cartDetails=cartDetails, totalPrice=totalPrice, error=error)

        for item in cartDetails:
            item.date = date
            item.isOrdered = 1
            product = sqlsession.query(Product).filter_by(
                id=item.product_id).first()
            product.quantity -= item.product_quantity

            log = Logs()
            log.date = date
            log.seller = product.seller
            log.user = user
            log.product = product
            log.product_quantity = item.product_quantity
            log.address1 = address1
            log.address2 = address2
            log.city = city
            log.postcode = postcode
            log.country = country
            log.state = state
            sqlsession.add(log)

        sqlsession.commit()
        return render_template('placed.html', totalPrice=(totalPrice*1.17))

    return render_template('checkout.html', user=user, cartDetails=cartDetails, totalPrice=totalPrice, error=None)


@app.route('/usertable')
def usertable():
    user = sqlsession.query(User).all()
    return render_template('table.html', rows=user, message="USERS ::")


@app.route('/sellertable')
def sellertable():
    sellers = sqlsession.query(Seller).all()
    return render_template('sellertable.html', rows=sellers, message="SELLERS ::")


@app.route('/productTable')
def productTable():
    products = sqlsession.query(Product).all()
    return render_template('productTable.html', rows=products, message="PRODUCTS ::")


@app.route('/orderTable')
def orderTable():
    orders = sqlsession.query(Order).all()
    return render_template('orderTable.html', rows=orders, message="ORDERS ::")


@app.route('/logs')
def logs():
    logs = sqlsession.query(Logs).all()
    return render_template('log.html', rows=logs, message="LOGS ::")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
