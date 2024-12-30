const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');  // Import spawn for process control

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Variable to store the state, trialNumber, and the running Python process
let currentState = 0;
let currentTrialNumber = 0;
let pythonProcess = null;  // Will hold the running Python process

// Function to terminate the previous Python process if it's running
const terminatePreviousProcess = () => {
    if (pythonProcess) {
        console.log("Sending SIGINT (keyboard interrupt) to the previous Python process...");
        pythonProcess.kill('SIGINT');  // Send SIGINT signal (mimicking Ctrl+C)
    }
};

// Function to call the Python script
const runPythonScript = (trialNumber) => {
    // Path to your Python script
    const pythonScriptPath = 'C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/GSR-Readings/RunTwoScripts.py';  // Replace with actual path to your Python script

    // Terminate any existing Python process
    terminatePreviousProcess();

    // Start a new Python process
    pythonProcess = spawn('C:/Users/benrg/miniconda3/python.exe', [pythonScriptPath, trialNumber]);

    // Capture output from the Python script
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data.toString()}`);
    });

    // Capture any errors from the Python script
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data.toString()}`);
    });

    // Handle when the Python process finishes
    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        pythonProcess = null;  // Reset the pythonProcess after it finishes
    });
};

// Endpoint to receive the page state and trialNumber
app.post('/api/state', (req, res) => {
    const { state, trialNumber } = req.body;
    console.log(req.body);

    if (state === 0 || state === 1) {
        currentState = state; // Save the state
        console.log(`Received state: ${state}`);

        // If the trial number has changed, run the Python script
        if (trialNumber !== currentTrialNumber) {
            currentTrialNumber = trialNumber;  // Update the trial number
            console.log(`Trial number changed: ${trialNumber}`);
            runPythonScript(trialNumber);  // Call the Python script
        }

        res.status(200).send({ message: 'State received successfully' });
    } else {
        res.status(400).send({ error: 'Invalid state value' });
    }
});

// Endpoint for MATLAB to fetch the result
app.get('/api/state', (req, res) => {
    if (currentState === 0 || currentState === 1) {
        // Provide the current state to MATLAB or any client
        res.status(200).send({ currentState });
    } else {
        res.status(404).send({ error: 'State not set' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
