const { spawn } = require('child_process');
const readline = require('readline');
const path = require('path');

// Path to your Python script (use path.join for better path handling)
const pythonScriptPath = 'C:/Users/benrg/OneDrive - Rutgers University/Documents/Rutgers/Research/Path Curvature Experiment/Phase 2/robot_interaction_experiment/GSR-Readings/RunTwoScripts.py';
// Create a readline interface to handle termination signals
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Function to run the Python script
const runPythonScript = (trialNumber) => {
    console.log(`Running command: "C:/Users/benrg/miniconda3/python.exe" "${pythonScriptPath}" ${trialNumber}`);

    // Spawn the Python process with quotes around the path
    const pythonProcess = spawn('C:/Users/benrg/miniconda3/python.exe', [`${pythonScriptPath}`, trialNumber]);

    // Capture standard output from the Python script
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data.toString()}`);
    });

    // Capture standard error from the Python script
    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data.toString()}`);
    });

    // Log when the Python process closes
    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });

    // Handle errors when spawning the process
    pythonProcess.on('error', (err) => {
        console.error('Failed to start Python process:', err);
    });

    return pythonProcess;  // Return the process for termination later
};

// Run the Python script with a specific trial number (e.g., 1)
let pythonProcess = runPythonScript(1);  // Change this trial number as needed

// Function to handle graceful shutdown and terminate the Python process
const shutdown = () => {
    if (pythonProcess) {
        console.log("Terminating Python process...");
        pythonProcess.kill('SIGINT');  // Send SIGINT (Ctrl+C) to the Python process to stop it
    }
    rl.close();  // Close the readline interface
};

// Listen for termination signals (Ctrl+C) to shut down the process
process.on('SIGINT', () => {
    console.log("Received SIGINT. Shutting down...");
    shutdown();
});

// Optionally, listen for other signals like SIGTERM
process.on('SIGTERM', () => {
    console.log("Received SIGTERM. Shutting down...");
    shutdown();
});

console.log("Python script is running. Press Ctrl+C to terminate.");
