import os
from datetime import datetime
from decimal import Decimal

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-before-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///store.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    image = db.Column(db.String(400), nullable=False)
    featured = db.Column(db.Boolean, default=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)


PRODUCTS = [
    ("Cloud Runner", "cloud-runner", "Lightweight everyday trainers with responsive foam cushioning.", "89.00", "Footwear", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80", True),
    ("Arc Everyday Tote", "arc-everyday-tote", "A structured carryall made for commutes, markets, and weekends.", "64.00", "Accessories", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=80", True),
    ("Studio Headphones", "studio-headphones", "Balanced wireless audio with soft memory-foam ear cushions.", "129.00", "Electronics", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80", True),
    ("Linen Overshirt", "linen-overshirt", "Relaxed, breathable layer cut from naturally textured linen.", "72.00", "Apparel", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80", False),
    ("Ceramic Pour Set", "ceramic-pour-set", "Hand-finished ceramic dripper and mug for deliberate mornings.", "48.00", "Home", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80", False),
    ("Field Watch", "field-watch", "A clean, durable timepiece with a brushed steel case.", "145.00", "Accessories", "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=900&q=80", False),
]


def seed_database():
    if not Product.query.first():
        for product in PRODUCTS:
            db.session.add(Product(name=product[0], slug=product[1], description=product[2], price=Decimal(product[3]), category=product[4], image=product[5], featured=product[6]))
        db.session.commit()


def cart_items():
    cart = session.get("cart", {})
    items, total = [], Decimal("0")
    for product_id, quantity in cart.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotal = product.price * quantity
            items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
            total += subtotal
    return items, total


@app.context_processor
def cart_context():
    return {"cart_count": sum(session.get("cart", {}).values())}


@app.template_filter("money")
def money(value):
    return f"${value:,.2f}"


@app.route("/")
def home():
    return render_template("home.html", products=Product.query.filter_by(featured=True).limit(3).all())


@app.route("/shop")
def shop():
    category = request.args.get("category", "")
    products = Product.query.filter_by(category=category).all() if category else Product.query.all()
    categories = [row[0] for row in db.session.query(Product.category).distinct().all()]
    return render_template("shop.html", products=products, categories=categories, active_category=category)


@app.route("/product/<slug>")
def product(slug):
    return render_template("product.html", product=Product.query.filter_by(slug=slug).first_or_404())


@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash(f"{product.name} added to your bag.", "success")
    return redirect(request.referrer or url_for("shop"))


@app.route("/cart")
def cart():
    items, total = cart_items()
    return render_template("cart.html", items=items, total=total)


@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for key in list(cart):
        qty = request.form.get(f"qty_{key}", type=int, default=0)
        if qty > 0:
            cart[key] = min(qty, 10)
        else:
            cart.pop(key)
    session["cart"] = cart
    flash("Your bag has been updated.", "success")
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = cart_items()
    if not items:
        flash("Your bag is empty.", "error")
        return redirect(url_for("shop"))
    if request.method == "POST":
        name, email, address = (request.form.get("name", "").strip(), request.form.get("email", "").strip(), request.form.get("address", "").strip())
        if not name or not email or not address:
            flash("Please complete all delivery details.", "error")
        else:
            order = Order(customer_name=name, email=email, address=address, total=total)
            db.session.add(order)
            db.session.flush()
            for item in items:
                db.session.add(OrderItem(order_id=order.id, product_name=item["product"].name, quantity=item["quantity"], unit_price=item["product"].price))
            db.session.commit()
            session.pop("cart", None)
            return render_template("confirmation.html", order=order)
    return render_template("checkout.html", items=items, total=total)


@app.route("/about")
def about():
    return render_template("about.html")


with app.app_context():
    db.create_all()
    seed_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
