from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import IntegrityError
import uuid
from flask_migrate import Migrate
from flask import session

from flask_login import LoginManager

app = Flask(__name__)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///share_a_meal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the secret key for session management and flash messages
app.secret_key = 'd7fcaf7298f4612c7409723be03caa1e31a294c8b623a4f9444e28ce2cf92a5a'
CORS(app)


# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)  # Pass the Flask app to the login manager

# Static admin credentials (username and password)
ADMIN_USERNAME = 'admin@123'
ADMIN_PASSWORD_HASH = generate_password_hash('mypassword123')  # Use a hashed password for security

# Configuring the uploads folder in your app
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Ensure this matches your desired folder name

# Ensure the uploads folder exists
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Add this field


# NGO model
class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    registration_no = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone_no = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    registration_certificate = db.Column(db.String(255))  # Store file path
    role = db.Column(db.String(50), default='ngo')  # Add role field

    def __repr__(self):
        return '<NGO %r>' % self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    aadhar_no = db.Column(db.String(12), unique=True, nullable=False)  # Aadhar is usually 12 digits
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    id_proof = db.Column(db.String(255))  # Path to uploaded ID proof file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='user')  # Add role field

    def __repr__(self):
        return f"<User {self.name}>"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Replace `User` with your model class
    
 # Sign-in log model with password hash
class SignInLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sign_in_time = db.Column(db.String(50), nullable=False)  # Time of sign-in
    sign_in_day = db.Column(db.String(20), nullable=False)  # Day of sign-in (e.g., Monday)
    sign_in_date = db.Column(db.Date, nullable=False)  # Date of sign-in
    password_hash = db.Column(db.String(128), nullable=False)  # Store password hash
    
    # Relationship with the User model
    user = db.relationship('User', backref=db.backref('sign_in_logs', lazy=True))

    def __repr__(self):
        return f"<SignInLog {self.user_id} - {self.sign_in_date}>"
    
class FoodItem(db.Model):
    __tablename__ = 'food_item'
    
    id = db.Column(db.Integer, primary_key=True)
    food_item = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    pickup_date = db.Column(db.String(255), nullable=False)
    pickup_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(255), nullable=False)
    mobile_number = db.Column(db.String(255), nullable=False)
    pictures = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Set nullable=True
    
    user = db.relationship('User', backref='food_items')  # Optional relationship if needed

       

# Route to serve the homepage
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('submit_feedback.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/ngo_register.html')
def ngo_register():
    return render_template('ngo_register.html')

@app.route('/user_register.html')
def user_register():
    return render_template('user_register.html')

@app.route('/signin.html')
def signin():
    return render_template('signin.html')

@app.route('/donate.html', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        # Capture form data
        food_item = request.form['foodItem']
        description = request.form['description']
        pickup_date = request.form['pickupDate']
        pickup_address = request.form['pickupAddress']
        city = request.form['city']
        contact_person = request.form['contactPerson']
        mobile_number = request.form['mobileNumber']
        pictures = request.form['pictures']  # This might need special handling for file uploads
        
        # Save to the database
        new_food_item = FoodItem(
            food_item=food_item,
            description=description,
            pickup_date=pickup_date,
            pickup_address=pickup_address,
            city=city,
            contact_person=contact_person,
            mobile_number=mobile_number,
            pictures=pictures
        )

        db.session.add(new_food_item)
        db.session.commit()

        flash('Food item donated successfully!', 'success')
        return redirect(url_for('foodlist'))  # Redirect to the food list page after donation
    
    return render_template('donate.html')  # Render the donation form page

@app.route('/request.html')
def requests():
    return render_template('request.html')



@app.route('/foodlist')
def foodlist():
    food_items = FoodItem.query.filter_by(user_id=session['user_id']).all()
    print("Food items in the database:")
    for food in food_items:
        print(f"Food item: {food.food_item}, Picture: {food.pictures}")  # Log the food items and their pictures
    return render_template('foodlist.html', food_items=food_items)

@app.route('/feedback.html', methods=['GET'])
def display_feedbacks():
    feedbacks = Contact.query.all()  # Fetch all feedback entries from the database
    print(feedbacks) 
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    rating = request.form.get('rating')  # Assuming it's passed as a number

    # Create a new feedback object
    new_feedback = Contact(name=name, email=email, message=message, rating=int(rating))
    
    # Save to the database
    db.session.add(new_feedback)
    db.session.commit()

    flash('Thank you for your feedback!', 'success')

    return redirect('index.html')





# Route for NGO registration (POST and GET methods)
@app.route('/user/ngo_register', methods=['POST', 'GET'])
def user_ngo_register():
    if request.method == 'POST':
        try:
            # Fetch form data
            name = request.form.get('name')
            registration_no = request.form.get('registration_no')
            email = request.form.get('email')
            username = request.form.get('username')
            phone_no = request.form.get('phone')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            city = request.form.get('city')
            address = request.form.get('add')

            # Debug: Print form data
            print(f"Form Data: {request.form.to_dict()}")

            # File upload validation
            if 'file' not in request.files or request.files['file'].filename == '':
                flash("No file uploaded. Please upload your registration certificate.", "error")
                return redirect(request.url)
            
            file = request.files.get('file')
            if file:
                print(f"Uploaded file: {file.filename}")
            else:
                print("No file uploaded.")

            # file = request.files['file']
            if not allowed_file(file.filename):
                flash("Invalid file type. Only PDF, JPG, JPEG, and PNG are allowed.", "error")
                return redirect(request.url)

            # Save file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            print(f"File saved at: {file_path}")

            # Password validation
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(request.url)

            hashed_password = generate_password_hash(password)

            # Check for duplicate email or username
            if NGO.query.filter_by(email=email).first():
                flash("Email already exists.", "error")
                return redirect(request.url)

            if NGO.query.filter_by(username=username).first():
                flash("Username already exists.", "error")
                return redirect(request.url)

            # Create and commit new NGO entry
            new_ngo = NGO(
                name=name,
                registration_no=registration_no,
                email=email,
                username=username,
                phone_no=phone_no,
                password_hash=hashed_password,
                city=city,
                address=address,
                registration_certificate=file_path,
                role='ngo' 
            )

            print("Adding NGO entry to the database...")
            db.session.add(new_ngo)
            db.session.commit()
            print("Data successfully committed to the database.")
            flash("Registration successful!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            flash("An unexpected error occurred. Please try again.", "error")
            return redirect(request.url)

    return render_template('ngo_register.html')


# Route for user registration (POST and GET methods)
@app.route('/user_register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        print("Step 1: Received POST request")  # Debugging log

        # Capture form data
        name = request.form.get('name')
        aadhar_no = request.form.get('aadhar-no')
        email = request.form.get('email')
        username = request.form.get('username')
        phone = request.form.get('phone')  # Change 'phone_no' to 'phone'
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        city = request.form.get('city')
        address = request.form.get('add')
        file = request.files.get('file')
        

        print(f"Step 2: Form Data - {request.form}")  # Debugging log

        # Validate data
        if not all([name, aadhar_no, email, username, phone, password, confirm_password, city, address, file]):
            print("Error: Missing data")  # Debugging log
            flash("All fields are required.", "error")
            return redirect(url_for('user_register'))

        if password != confirm_password:
            print("Error: Passwords do not match")  # Debugging log
            flash("Passwords do not match.", "error")
            return render_template('user_register.html')

        # Save file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            print(f"Step 3: File saved at {file_path}")  # Debugging log
        else:
            print("Error: Invalid file upload")  # Debugging log
            flash("Invalid file upload. Only PDF, JPG, JPEG, PNG files are allowed.", "error")
            return redirect(url_for('user_register'))

        # Hash password
        hashed_password = generate_password_hash(password)

        # Add user to database
        new_user = User(
            name=name,
            aadhar_no=aadhar_no,
            email=email,
            username=username,
            phone=phone,  # Change 'phone_no' to 'phone'
            password_hash=hashed_password,
            city=city,
            address=address,
            id_proof=file_path,
            role='user',

        )

        print("Step 4: Adding user to database...")  # Debugging log

        try:
            db.session.add(new_user)
            db.session.commit()
            print("Step 5: User added successfully")  # Debugging log
            flash("User registered successfully!", "success")
            return redirect(url_for('user_register'))
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {e}")  # Debugging log
            flash("A user with this email or username already exists.", "error")
            return redirect(url_for('user_register'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")  # Debugging log
            flash("Error occurred during registration. Please try again.", "error")
            return redirect(url_for('user_register'))

    return render_template('index.html')


@app.route('/ngo_dashboard.html')
def ngo_dashboard():
    if 'username' in session and session['role'] == 'ngo':
        return render_template('ngo_dashboard.html')
    else:
        flash('Please login as NGO first.', 'warning')
        return redirect(url_for('signin_other'))
    

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session.get('role') == 'admin':
        return render_template('admin_dashboard.html')
    flash('Please log in as admin first.', 'warning')
    return redirect(url_for('signin_other'))



@app.route('/donor_dashboard.html')
def donor_dashboard():
    if 'username' in session:
        print("Rendering donor_dashboard.html")  # Debugging log
        return render_template('donor_dashboard.html')
    else:
        flash('Please login first.', 'warning')
        return redirect(url_for('signin_other'))


@app.route('/check')
def check():
    if 'username' in session and 'role' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'ngo':
            return redirect(url_for('ngo_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('signin_other'))


@app.route('/signin_other', methods=['POST', 'GET'])
def signin_other():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Debug: Check received form data
        print(f"Username: {username}, Password: {password}")

        # Admin Login
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            print("admin")
            session['username'] = username
            session['role'] = 'admin'
            print(f"Logged in as admin: {username}")
            return redirect(url_for('admin_dashboard'))

        # User Login
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = user.username
            session['user_id'] = user.id 
            session['role'] = 'user'
            print(f"Logged in as user: {username}")
            return redirect(url_for('donor_dashboard'))

        # NGO Login
        ngo = NGO.query.filter_by(username=username).first()
        if ngo and check_password_hash(ngo.password_hash, password):
            session['username'] = ngo.username
            session['role'] = 'ngo'
            print(f"Logged in as NGO: {username}")
            return redirect(url_for('ngo_dashboard'))

        # Invalid Credentials
        flash('Invalid username or password.', 'error')
        return redirect(url_for('signin_other'))

    return render_template('signin.html')

# Route for admin dashboard
@app.route('/admin_dashboard.html')
def admin_dash():
    # Logic to fetch data for cards (e.g., total cities, users, NGOs, etc.)
    return render_template('admin_dashboard.html')


@app.route('/submit_food', methods=['POST'])
def submit_food():
     

    food_item = request.form['foodItem']
    description = request.form['description']
    pickup_date = request.form['pickupDate']
    pickup_address = request.form['pickupAddress']
    city = request.form['city']
    contact_person = request.form['contactPerson']
    mobile_number = request.form['mobileNumber']
    file = request.files['pictures']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        picture_path = filename
        print(f"File uploaded: {filename}")  # Log the filename for debugging
    else:
        picture_path = None
        print("No file uploaded or invalid file type.")  # Log if file wasn't uploaded

    user_id = session.get('user_id')
    if user_id is None:
        flash('You must be logged in to donate food.', 'danger')
        return redirect(url_for('signin'))

    new_food_item = FoodItem(
        food_item=food_item,
        description=description,
        pickup_date=pickup_date,
        pickup_address=pickup_address,
        city=city,
        contact_person=contact_person,
        mobile_number=mobile_number,
        pictures=picture_path,
        user_id=user_id
    )

    db.session.add(new_food_item)
    db.session.commit()

    flash('Food item donated successfully!', 'success')
    return redirect(url_for('foodlist'))




# Route for total cities
@app.route('/City.html')
def manage_cities():
 return render_template('City.html')


# Route for managing users
@app.route('/manage_user.html')
def manage_user():
    """Display all users in the admin dashboard."""
    users = User.query.filter_by(role='user').all()  # Only fetch users with the role 'user'
    return render_template('manage_user.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.username = request.form['username']
        user.phone = request.form['phone']
        user.city = request.form['city']
        user.address = request.form['address']
        if request.form['password']:
            user.password_hash = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_user'))
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_user.html'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Add a new user."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        phone = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        aadhar_no = request.form['aadhar_no']
        password = generate_password_hash(request.form['password'])

        # Check if email or username already exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists!', 'danger')
            return redirect(url_for('manage_users'))

        new_user = User(
            name=name,
            email=email,
            username=username,
            phone=phone,
            city=city,
            address=address,
            aadhar_no=aadhar_no,
            password_hash=password,
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')  # Create a form for adding users

# search and filter users
@app.route('/users', methods=['GET'])
def get_users():
    city = request.args.get('city', '')
    name = request.args.get('name', '')

    # Debugging output
    print(f"Received request: city={city}, name={name}")

    query = User.query
    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    
    users = query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'aadhar_no': user.aadhar_no,
        'email': user.email,
        'username': user.username,
        'phone': user.phone,
        'city': user.city,
        'address': user.address,
        'id_proof': user.id_proof,
        'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'role': user.role
    } for user in users])


# search and filter ngos
@app.route('/ngos', methods=['GET'])
def get_ngos():
    city = request.args.get('city', '')
    name = request.args.get('name', '')
    query = NGO.query
    if city:
        query = query.filter(NGO.city.ilike(f"%{city}%"))
    if name:
        query = query.filter(NGO.name.ilike(f"%{name}%"))
    ngos = query.all()
    return jsonify([{
        'id': ngo.id,
        'name': ngo.name,
        'registration_no': ngo.registration_no,
        'email': ngo.email,
        'username': ngo.username,
        'phone_no': ngo.phone_no,
        'city': ngo.city,
        'address': ngo.address,
        'registration_certificate': ngo.registration_certificate,
        'role': ngo.role
    } for ngo in ngos])



@app.route('/manage_ngo.html', methods=['GET'])
def manage_ngos():
    ngos = NGO.query.all()  # Get all NGOs from the database
    return render_template('manage_ngo.html', ngos=ngos)





# Route to add a new NGO
@app.route('/add_ngo', methods=['GET', 'POST'])
def add_ngo():
    if request.method == 'POST':
        name = request.form['name']
        registration_no = request.form['registration_no']
        email = request.form['email']
        username = request.form['username']
        phone_no = request.form['phone_no']
        city = request.form['city']
        address = request.form['address']
        registration_certificate = request.files['registration_certificate']
        certificate_filename = secure_filename(registration_certificate.filename)
        registration_certificate.save(os.path.join(app.config['UPLOAD_FOLDER'], certificate_filename))

        # Hash the password before storing it
        password_hash = generate_password_hash(request.form['password'])

        new_ngo = NGO(name=name, registration_no=registration_no, email=email, 
                      username=username, phone_no=phone_no, city=city, 
                      address=address, registration_certificate=certificate_filename, 
                      password_hash=password_hash)

        db.session.add(new_ngo)
        db.session.commit()
        flash('NGO added successfully!', 'success')
        return redirect(url_for('manage_ngo'))

    return render_template('add_ngo.html')

# Route to edit an existing NGO
@app.route('/edit_ngo/<int:id>', methods=['GET', 'POST'])
def edit_ngo(id):
    ngo = NGO.query.get_or_404(id)
    
    if request.method == 'POST':
        ngo.name = request.form['name']
        ngo.registration_no = request.form['registration_no']
        ngo.email = request.form['email']
        ngo.username = request.form['username']
        ngo.phone_no = request.form['phone_no']
        ngo.city = request.form['city']
        ngo.address = request.form['address']
        
        if 'registration_certificate' in request.files:
            registration_certificate = request.files['registration_certificate']
            if registration_certificate:
                certificate_filename = secure_filename(registration_certificate.filename)
                registration_certificate.save(os.path.join(app.config['UPLOAD_FOLDER'], certificate_filename))
                ngo.registration_certificate = certificate_filename

        db.session.commit()
        flash('NGO updated successfully!', 'success')
        return redirect(url_for('manage_ngo'))

    return render_template('edit_ngo.html', ngo=ngo)

# Route to delete an NGO
@app.route('/delete_ngo/<int:id>', methods=['GET', 'POST'])
def delete_ngo(id):
    ngo = NGO.query.get_or_404(id)
    db.session.delete(ngo)
    db.session.commit()
    flash('NGO deleted successfully!', 'success')
    return redirect(url_for('manage_ngo'))



# Route for handling all requests
@app.route('/request.html', methods=['GET', 'POST'])
def all_requests():
    
    return render_template('request.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)  # Remove role from session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create all the tables in the database
    app.run(debug=True)
