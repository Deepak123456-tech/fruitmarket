from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# In-memory data storage
users = {}                 # username: password (plain text - demo only!)
fruits = [                  # List of fruit dictionaries
    {"id": 1, "name": "Apple",       "price": 1.5, "image": "apple.jpg",       "stock": 100},
    {"id": 2, "name": "Banana",      "price": 0.8, "image": "banana.jpg",      "stock": 150},
    {"id": 3, "name": "Orange",      "price": 1.2, "image": "orange.jpg",      "stock": 80},
    {"id": 4, "name": "Mango",       "price": 2.5, "image": "mango.jpg",       "stock": 60},
    {"id": 5, "name": "Strawberry",  "price": 3.0, "image": "strawberry.jpg",  "stock": 40},
    {"id": 6, "name": "Grapes",      "price": 2.0, "image": "grapes.jpg",      "stock": 70},
    {"id": 7, "name": "Pineapple",   "price": 4.0, "image": "pineapple.jpg",   "stock": 30},
    {"id": 8, "name": "Watermelon",  "price": 5.5, "image": "watermelon.jpg",  "stock": 20},
    {"id": 9, "name": "Kiwi",        "price": 2.8, "image": "kiwi.jpg",        "stock": 50},
    {"id": 10,"name": "Peach",       "price": 2.2, "image": "peach.jpg",       "stock": 45},
]

# Cart: user_id -> list of {"fruit_id": int, "quantity": int}
carts = {}  # Will be like: {1: [{"fruit_id": 1, "quantity": 2}, ...]}

# Helper to get next fruit ID
def get_next_fruit_id():
    return max(fruit["id"] for fruit in fruits) + 1 if fruits else 1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Plain text (demo only!)
        
        if username in users:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        users[username] = password
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            # Create a simple user_id (index in dict keys)
            user_id = len(users)
            session['user_id'] = user_id
            session['username'] = username
            # Initialize empty cart for this user
            if user_id not in carts:
                carts[user_id] = []
            flash('Login successful!', 'success')
            return redirect(url_for('market'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/market')
def market():
    if 'user_id' not in session:
        flash('Please login to access the market.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('market.html', fruits=fruits)

@app.route('/add_to_cart/<int:fruit_id>')
def add_to_cart(fruit_id):
    if 'user_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart = carts[user_id]
    
    # Check if fruit already in cart
    for item in cart:
        if item['fruit_id'] == fruit_id:
            item['quantity'] += 1
            break
    else:
        cart.append({"fruit_id": fruit_id, "quantity": 1})
    
    fruit_name = next(f["name"] for f in fruits if f["id"] == fruit_id)
    flash(f'{fruit_name} added to cart!', 'success')
    return redirect(url_for('market'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to view cart.', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cart = carts.get(user_id, [])
    
    cart_items = []
    total = 0
    for item in cart:
        fruit = next(f for f in fruits if f["id"] == item["fruit_id"])
        subtotal = fruit["price"] * item["quantity"]
        total += subtotal
        cart_items.append({
            "fruit": fruit,
            "quantity": item["quantity"],
            "subtotal": subtotal
        })
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_fruit', methods=['GET', 'POST'])
def add_fruit():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        image = request.form.get('image', f"{name.lower()}.jpg")
        
        new_fruit = {
            "id": get_next_fruit_id(),
            "name": name,
            "price": price,
            "image": image,
            "stock": stock
        }
        fruits.append(new_fruit)
        flash('Fruit added successfully!', 'success')
        return redirect(url_for('market'))
    
    return render_template('add_fruit.html')

if __name__ == '__main__':
    app.run(debug=True)