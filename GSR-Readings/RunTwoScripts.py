import subprocess
import sys
import signal
import time

def run_scripts_in_parallel():
    # Paths to your scripts
    script1_path = r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR-Readings\Get_GSR_Readings.py"  # Update this path
    script2_path = r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR-Readings\Get_HeartRate_Readings.py"  # Update this path

    # Start both scripts as subprocesses
    process1 = subprocess.Popen(["python", script1_path])
    process2 = subprocess.Popen(["python", script2_path])

    try:
        # Wait for both processes to complete
        process1.wait()
        process2.wait()
    except KeyboardInterrupt:
        print("Interrupted by user, terminating processes...")
        
        # Attempt a graceful termination first
        process1.terminate()
        process2.terminate()
        
        # Give the processes a few seconds to terminate gracefully
        time.sleep(2)
        
        # If they haven't terminated, forcefully kill them
        if process1.poll() is None:  # process1 is still running
            print("Forcefully killing process1...")
            process1.kill()
        if process2.poll() is None:  # process2 is still running
            print("Forcefully killing process2...")
            process2.kill()
        
        # Wait for processes to confirm termination
        process1.wait()
        process2.wait()
        print("Both processes terminated.")

if __name__ == "__main__":
    run_scripts_in_parallel()
