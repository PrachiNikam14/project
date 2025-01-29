from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///share_a_meal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Models for Donor, Receiver, and Volunteer
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    food_details = db.Column(db.String(200), nullable=False)

class Receiver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(100), nullable=False)




@app.route('/')
def home():
    return render_template('index.html')

# Routes to handle form submissions
@app.route('/api/donors', methods=['POST'])
def add_donor():
    data = request.get_json()
    donor = Donor(name=data['name'], email=data['email'], food_details=data['foodDetails'])
    db.session.add(donor)
    db.session.commit()
    return jsonify({'message': 'Donor added successfully'}), 201

@app.route('/api/receivers', methods=['POST'])
def add_receiver():
    data = request.get_json()
    receiver = Receiver(name=data['name'], email=data['email'])
    db.session.add(receiver)
    db.session.commit()
    return jsonify({'message': 'Receiver added successfully'}), 201

@app.route('/api/volunteers', methods=['POST'])
def add_volunteer():
    data = request.get_json()
    volunteer = Volunteer(name=data['name'], email=data['email'], availability=data['availability'])
    db.session.add(volunteer)
    db.session.commit()
    return jsonify({'message': 'Volunteer added successfully'}), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    # Create the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
