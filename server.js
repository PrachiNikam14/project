const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');

// Initialize the app
const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(cors());

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/share-a-meal', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.log('Error: ', err));

// Donor Schema and Model
const donorSchema = new mongoose.Schema({
    name: String,
    email: String,
    foodDetails: String,
    createdAt: { type: Date, default: Date.now }
});
const Donor = mongoose.model('Donor', donorSchema);

// Receiver Schema and Model
const receiverSchema = new mongoose.Schema({
    name: String,
    email: String,
    createdAt: { type: Date, default: Date.now }
});
const Receiver = mongoose.model('Receiver', receiverSchema);

// Volunteer Schema and Model
const volunteerSchema = new mongoose.Schema({
    name: String,
    email: String,
    availability: String,
    createdAt: { type: Date, default: Date.now }
});
const Volunteer = mongoose.model('Volunteer', volunteerSchema);

// API Endpoints
app.post('/api/donors', async (req, res) => {
    try {
        const donor = new Donor(req.body);
        await donor.save();
        res.status(201).json({ message: 'Donor registered successfully' });
    } catch (error) {
        res.status(400).json({ message: 'Error registering donor', error });
    }
});

app.post('/api/receivers', async (req, res) => {
    try {
        const receiver = new Receiver(req.body);
        await receiver.save();
        res.status(201).json({ message: 'Receiver registered successfully' });
    } catch (error) {
        res.status(400).json({ message: 'Error registering receiver', error });
    }
});

app.post('/api/volunteers', async (req, res) => {
    try {
        const volunteer = new Volunteer(req.body);
        await volunteer.save();
        res.status(201).json({ message: 'Volunteer registered successfully' });
    } catch (error) {
        res.status(400).json({ message: 'Error registering volunteer', error });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
