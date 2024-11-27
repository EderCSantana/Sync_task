# Importing necessary modules
import os
import time
import shutil
import argparse
import filecmp
from datetime import datetime


def log(msg, log_file):
    """Logs a message to both console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    log_message = f"[{timestamp}] {msg}"  
    print(log_message)  
    with open(log_file, "a") as f:  
        f.write(log_message + "\n")  


def sync_folders(source, replica, log_file):
    """Synchronizes source and replica folders."""
    

    for root, dirs, files in os.walk(source): # Loop on all directories and files
        replica_root = root.replace(source, replica, 1)
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            log(f"Created folder: {replica_root}", log_file)

        for file in files:     # If file differs from the source, copy it
            source_file = os.path.join(root, file)  
            replica_file = os.path.join(replica_root, file)  
            if not os.path.exists(replica_file) or not filecmp.cmp(source_file, replica_file, shallow=False):
                shutil.copy2(source_file, replica_file)  # Copy file to replica
                log(f"Copied/Updated file: {source_file} -> {replica_file}", log_file)

    for root, dirs, files in os.walk(replica): # Map directory from replica to source

        source_root = root.replace(replica, source, 1)
        
        if not os.path.exists(source_root): # If directory not in source, remove from replica
            shutil.rmtree(root)  
            log(f"Removed folder: {root}", log_file)
            continue 

        for file in files: # Loop over files in current directory, get the paths for dir and files
            replica_file = os.path.join(root, file)  
            source_file = os.path.join(source_root, file)
            
            if not os.path.exists(source_file):  # If not in source, remove it from replica
                os.remove(replica_file)  
                log(f"Removed file: {replica_file}", log_file)

def main(): # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Folder Synchronizer")
    parser.add_argument("source_dir", help="Path to the source directory")
    parser.add_argument("replica_dir", help="Path to the replica directory")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()  # Parse the arguments passed in the command line

    # Get paths of the source, replica, and the log file
    source_dir = os.path.abspath(args.source_dir)
    replica_dir = os.path.abspath(args.replica_dir)
    log_file = os.path.abspath(args.log_file)

    if not os.path.exists(source_dir): # Check if the source directory exists
        print(f"Error: Directory '{source_dir}' does not exist.")
        return

    if not os.path.exists(replica_dir):    # If the replica directory doesn't exist, create it
        os.makedirs(replica_dir)
        print(f"Directory '{replica_dir}' was created.")  #

    while True: # Start the sync loop, running until manually interrupted (ctrl + c)
        try:
            sync_folders(source_dir, replica_dir, log_file)  # Call the sync function
            time.sleep(args.sync_interval)  # Wait for the next sync
        except KeyboardInterrupt:
            print("\nSync stopped.")
            break  
        except Exception as e:
            log(f"Error: {e}", log_file)  # Log unexpected errors


if __name__ == "__main__":# Check if it's imported or runned as a command
    main()  
