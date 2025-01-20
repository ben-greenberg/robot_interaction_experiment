const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');  // Import spawn for process control
const fs = require('fs');  // Import fs for file system operations

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Variable to store the state, trialNumber, and the running Python processes
let currentState = 0;
let currentTrialNumber = 0;

// Will hold the running Python processes
let pythonProcess1 = null;
let pythonProcess2 = null;

// Path to the control text file for signaling termination
const controlFilePath = "C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/GSR-Readings/control.txt" 

// Function to terminate the previous Python processes if they're running
const terminatePreviousProcesses = () => {
    if (pythonProcess1) {
        console.log("Sending SIGINT (keyboard interrupt) to the first Python process...");
        pythonProcess1.kill('SIGINT');  // Send SIGINT signal (mimicking Ctrl+C)
    }

    if (pythonProcess2) {
        console.log("Sending SIGINT (keyboard interrupt) to the second Python process...");
        pythonProcess2.kill('SIGINT');  // Send SIGINT signal (mimicking Ctrl+C)
    }
};

// Function to run both Python scripts simultaneously
const runPythonScripts = (trialNumber) => {
    // Paths to your Python scripts
    const pythonScriptPath1 = "C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/GSR-Readings/Get_GSR_Readings.py";
    const pythonScriptPath2 = "C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/GSR-Readings/Get_HeartRate_Readings.py";

    // Terminate any existing Python processes
    terminatePreviousProcesses();

    // Start the first Python process
    pythonProcess1 = spawn('C:/Users/benrg/miniconda3/python.exe', ['-u', pythonScriptPath1, trialNumber]);

    // Capture output from the first Python script
    pythonProcess1.stdout.on('data', (data) => {
        console.log(`Python Script 1 stdout: ${data.toString()}`);
    });

    pythonProcess1.stderr.on('data', (data) => {
        console.error(`Python Script 1 stderr: ${data.toString()}`);
    });

    pythonProcess1.on('close', (code) => {
        console.log(`Python Script 1 exited with code ${code}`);
        pythonProcess1 = null;  // Reset the first pythonProcess after it finishes
    });

    // Start the second Python process
    pythonProcess2 = spawn('C:/Users/benrg/miniconda3/python.exe', ['-u', pythonScriptPath2, trialNumber]);

    // Capture output from the second Python script
    pythonProcess2.stdout.on('data', (data) => {
        console.log(`Python Script 2 stdout: ${data.toString()}`);
    });

    pythonProcess2.stderr.on('data', (data) => {
        console.error(`Python Script 2 stderr: ${data.toString()}`);
    });

    pythonProcess2.on('close', (code) => {
        console.log(`Python Script 2 exited with code ${code}`);
        pythonProcess2 = null;  // Reset the second pythonProcess after it finishes
    });
};

// Function to write the control signal to the text file
const writeControlSignal = (signal) => {
    fs.writeFileSync(controlFilePath, signal, 'utf8');  // Write the signal (terminate or continue)
};

// Endpoint to receive the page state and trialNumber
app.post('/api/state', (req, res) => {
    const { state, trialNumber, loc } = req.body;
    console.log(req.body);
    console.log("Trial NUM: ");
    console.log(trialNumber);
    console.log("LOCATION: ");
    console.log(loc);
    
    if ((state === 0 || state === 1) && loc !== undefined) {
        currentState = state; // Save the state
        console.log(`Received state: ${state}`);

        // If the trial number has changed, run the Python script
        if (trialNumber != currentTrialNumber) {
            currentTrialNumber = trialNumber;  // Update the trial number
            console.log(`Trial number changed: ${trialNumber}`);
            runPythonScripts(trialNumber);  // Call the function to run both Python scripts
        }

        // Write the control signal based on the state
        if (state === 0) {
            // State 0: Write "terminate" to the control file to stop Python scripts
            writeControlSignal('terminate');
        } else if (state === 1) {
            // State 1: Clear the control file to allow Python scripts to continue
            writeControlSignal('');
        }

        res.status(200).send({ message: 'State received successfully' });
    } else {
        res.status(400).send({ error: 'Invalid state value or missing location' });
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
