from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "mysecretkey123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Product Table
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.String(300))
    image = db.Column(db.String(100))
    category = db.Column(db.String(50))
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer)

    username = db.Column(db.String(100))

    rating = db.Column(db.Integer)

    comment = db.Column(db.String(500))
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    product_id = db.Column(db.Integer)
@app.route("/")
def home():

    username = session.get("user")

    return render_template(
        "index.html",
        username=username
    )

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return "User Registered Successfully!"

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

           session["user"] = user.username
           session["user_id"] = user.id

           return redirect("/")
        return "Invalid Email or Password"

    return render_template("login.html")

# Products Page
@app.route("/products")
def products():

    search = request.args.get("search")
    category = request.args.get("category")

    products = Product.query

    if search:
        products = products.filter(
            Product.name.contains(search)
        )

    if category:
        products = products.filter_by(
            category=category
        )

    products = products.all()

    return render_template(
        "products.html",
        products=products
    )
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        item.quantity += 1

    else:
        item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=1
        )

        db.session.add(item)

    db.session.commit()

    return redirect("/cart")
@app.route("/cart")
def cart():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    cart_items = Cart.query.filter_by(
        user_id=user_id
    ).all()

    products = []
    total = 0

    for item in cart_items:

        product = Product.query.get(item.product_id)

        if product:
            products.append(product)
            total += product.price * item.quantity

    return render_template(
        "cart.html",
        products=products,
        cart_items=cart_items,
        total=total
    )
@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):

    user_id = session.get("user_id")

    item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect("/cart")
@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    user_id = session.get("user_id")

    cart_items = Cart.query.filter_by(
    user_id=user_id
    ).all()
    total = 0

    for item in cart_items:
        product = Product.query.get(item.product_id)

        if product:
            total += product.price

    if request.method == "POST":

        order = Order(total=total)

        db.session.add(order)

        # Clear Cart
        Cart.query.filter_by(
            user_id=user_id
        ).delete()

        db.session.commit()

        return "Order Placed Successfully!"

    return render_template(
        "checkout.html",
        total=total
    )
@app.route("/orders")
def orders():

    orders = Order.query.all()

    return render_template(
        "orders.html",
        orders=orders
    )
@app.route("/admin")
def admin():

    products = Product.query.all()

    total_products = Product.query.count()
    total_orders = Order.query.count()

    orders = Order.query.all()

    revenue = 0

    for order in orders:
        revenue += order.total

    return render_template(
        "admin.html",
        products=products,
        total_products=total_products,
        total_orders=total_orders,
        revenue=revenue
    )
@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        image = request.form["image"]

        product = Product(
            name=name,
            price=price,
            description=description,
            image=image
        )

        db.session.add(product)
        db.session.commit()

        return "Product Added Successfully!"

    return render_template("add_product.html")
@app.route("/delete_product/<int:product_id>")
def delete_product(product_id):

    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)
        db.session.commit()

    return "Product Deleted Successfully!"
@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    product = Product.query.get(product_id)

    if request.method == "POST":

        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.description = request.form["description"]
        product.image = request.form["image"]

        db.session.commit()

        return "Product Updated Successfully!"

    return render_template(
        "edit_product.html",
        product=product
    )
@app.route("/product/<int:product_id>")
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    reviews = Review.query.filter_by(
        product_id=product_id
    ).all()

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews
    )
@app.route("/increase_quantity/<int:product_id>")
def increase_quantity(product_id):

    user_id = session.get("user_id")

    item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        item.quantity += 1
        db.session.commit()

    return redirect("/cart")
@app.route("/decrease_quantity/<int:product_id>")
def decrease_quantity(product_id):

    user_id = session.get("user_id")

    item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:

        if item.quantity > 1:
            item.quantity -= 1
        else:
            db.session.delete(item)

        db.session.commit()

    return redirect("/cart")
@app.route("/review/<int:product_id>", methods=["POST"])
def add_review(product_id):

    username = request.form["username"]
    rating = int(request.form["rating"])
    comment = request.form["comment"]

    review = Review(
        product_id=product_id,
        username=username,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    return redirect(f"/product/{product_id}")
@app.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("user_id", None)

    return redirect("/")
@app.route("/add_to_wishlist/<int:product_id>")
def add_to_wishlist(product_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    item = Wishlist.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if not item:

        item = Wishlist(
            user_id=user_id,
            product_id=product_id
        )

        db.session.add(item)
        db.session.commit()

    return redirect("/wishlist")
@app.route("/wishlist")
def wishlist():

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    wishlist_items = Wishlist.query.filter_by(
        user_id=user_id
    ).all()

    products = []

    for item in wishlist_items:

        product = Product.query.get(item.product_id)

        if product:
            products.append(product)

    return render_template(
        "wishlist.html",
        products=products
    )
@app.route("/remove_from_wishlist/<int:product_id>")
def remove_from_wishlist(product_id):

    user_id = session.get("user_id")

    item = Wishlist.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect("/wishlist")
@app.route("/move_to_cart/<int:product_id>")
def move_to_cart(product_id):

    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    # Add to cart
    cart_item = Cart.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)

    # Remove from wishlist
    wishlist_item = Wishlist.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if wishlist_item:
        db.session.delete(wishlist_item)

    db.session.commit()

    return redirect("/cart")

import os

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        if Product.query.count() == 0:

            p1 = Product(
                name="Laptop",
                price=55000,
                description="High Performance Laptop",
                image="laptop.jpg",
                category="Electronics"
            )

            p2 = Product(
                name="Mobile",
                price=20000,
                description="Android Smartphone",
                image="mobile.jpg",
                category="Electronics"
            )

            p3 = Product(
                name="Headphones",
                price=3000,
                description="Wireless Headphones",
                image="headphones.jpg",
                category="Electronics"
            )

            db.session.add_all([p1, p2, p3])
            db.session.commit()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)