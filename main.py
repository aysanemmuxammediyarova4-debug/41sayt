from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'food_delivery_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modellar
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)          # Masalan: Palov, Burger, Pitssa
    restaurant = db.Column(db.String(100), nullable=False)     # Restoran / Kafe nomi
    category = db.Column(db.String(50), nullable=False)        # Milliy, Fast Food, Osiyo, Desert
    prep_time = db.Column(db.Integer, nullable=False)          # Tayyorlanish vaqti (daqiqa)
    price = db.Column(db.Float, nullable=False)                # Narxi (so'm)
    contact_phone = db.Column(db.String(20), nullable=False)   # Restoran telefoni
    image_url = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)           # Masalliqlar va tavsif
    orders = db.relationship('Order', backref='food', lazy=True, cascade="all, delete")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Food.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter((Food.title.contains(search)) | (Food.restaurant.contains(search)))
        
    foods = query.order_by(Food.id.desc()).all()
    return render_template('index.html', foods=foods, selected_category=category, search=search)

@app.route('/food/<int:food_id>', methods=['GET', 'POST'])
def food_detail(food_id):
    food = Food.query.get_or_404(food_id)
    
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone = request.form['phone']
        address = request.form['address']
        quantity = int(request.form.get('quantity', 1))
        
        order = Order(
            food_id=food.id,
            customer_name=customer_name,
            phone=phone,
            address=address,
            quantity=quantity
        )
        
        db.session.add(order)
        db.session.commit()
        total_price = food.price * quantity
        return render_template('food_detail.html', food=food, success=True, order=order, total_price=total_price)
        
    return render_template('food_detail.html', food=food)

@app.route('/add', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        title = request.form['title']
        restaurant = request.form['restaurant']
        category = request.form['category']
        prep_time = int(request.form['prep_time'])
        price = float(request.form['price'])
        contact_phone = request.form['contact_phone']
        image_url = request.form['image_url']
        description = request.form['description']

        new_food = Food(
            title=title, restaurant=restaurant, category=category,
            prep_time=prep_time, price=price, contact_phone=contact_phone,
            image_url=image_url, description=description
        )
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_food.html')

if __name__ == '__main__':
    app.run(debug=True)