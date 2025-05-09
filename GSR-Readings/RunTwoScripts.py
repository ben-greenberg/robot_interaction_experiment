import subprocess
import os
import signal
import time
import sys

# Signal handler for SIGUSR1
def handle_sigusr1(sig, frame):
    print("Received SIGUSR1 from Node.js. Gracefully shutting down...")
    # Perform any cleanup (e.g., save data to CSV)
    sys.exit(0)  # Exit the script gracefully

# Register the signal handler for SIGUSR1
signal.signal(signal.SIGINT, handle_sigusr1)

def run_scripts_in_parallel():
    # Paths to your scripts
    script1_path = r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR-Readings\Get_GSR_Readings.py"
    script2_path = r"C:\Users\benrg\OneDrive - Rutgers University\Documents\Rutgers\Research\Path Curvature Experiment\Phase 2\robot_interaction_experiment\GSR-Readings\Get_HeartRate_Readings.py"

    # Start both scripts with unbuffered mode
    process1 = subprocess.Popen(["python", "-u", script1_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.getpid)
    process2 = subprocess.Popen(["python", "-u", script2_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.getpid)

    try:
        # Continuously read from the processes' stdout
        while True:
            # Read outputs from both processes
            output1 = process1.stdout.readline().decode('utf-8').strip()
            output2 = process2.stdout.readline().decode('utf-8').strip()

            if output1:
                print(f"Script1 Output: {output1}")
            if output2:
                print(f"Script2 Output: {output2}")

            # Check if both processes have finished
            if process1.poll() is not None and process2.poll() is not None:
                break

            # Small delay to prevent high CPU usage
            time.sleep(0.1)

    except Exception as e:
        print(f"Exception occurred: {e}")
        print("Terminating subprocesses...")
        # Send SIGUSR1 to child processes' process groups for graceful shutdown
        os.killpg(os.getpgid(process1.pid), signal.SIGINT)
        os.killpg(os.getpgid(process2.pid), signal.SIGINT)


    finally:
        # Wait for processes to terminate gracefully
        process1.wait()
        process2.wait()
        print("Both processes terminated.")

if __name__ == "__main__":
    print("Python script is running. Waiting for termination signals...")
    run_scripts_in_parallel()
