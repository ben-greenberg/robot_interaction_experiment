const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Variable to store the state
let currentState = 0;

// Endpoint to receive the page state
app.post('/api/state', (req, res) => {
    const { state } = req.body;

    if (state === 0 || state === 1) {
        currentState = state; // Save the state
        console.log(`Received state: ${state}`);
        res.status(200).send({ message: 'State received successfully' });
    } else {
        res.status(400).send({ error: 'Invalid state value' });
    }
});

// Endpoint for MATLAB to fetch the result
app.get('/api/state', (req, res) => {
    if (currentState === 0 || currentState === 1) {
        console.log(`MATLAB requested state. Current state: ${currentState}`);
        res.status(200).send({ currentState });
    } else {
        res.status(404).send({ error: 'State not set' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
