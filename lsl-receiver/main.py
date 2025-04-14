from pylsl import StreamInlet, resolve_byprop
import psycopg
import datetime
import os
import signal
import sys
from dotenv import load_dotenv

# Flag to indicate if the program should continue running
running = True

# Signal handler function
def signal_handler(sig, frame):
    global running
    print(f"\nReceived signal {sig}. Shutting down gracefully...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler) # Handle termination signal

# Load environment variables from .env file if it exists
load_dotenv()

# Database connection parameters from environment variables with fallback defaults
db_params = {
    "host": os.environ["DB_HOST"],
    "dbname": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "port": os.environ["DB_PORT"]
}

print("Looking for an EEG stream...")
streams = resolve_byprop('type', 'eeg')

if not streams:
    raise RuntimeError("No EEG stream found")

inlet = StreamInlet(streams[0])

# Column names that match the database table structure (without timestamp)
columns = [
    "fp1", "fz", "f3", "f7", "ft9", "fc5", "fc1", "c3", "t7", "tp9", 
    "cp5", "cp1", "pz", "p3", "p7", "o1", "oz", "o2", "p4", "p8", 
    "tp10", "cp6", "cp2", "cz", "c4", "t8", "ft10", "fc6", "fc2", 
    "f4", "f8", "fp2", "x_dir", "y_dir", "z_dir", "mkidx"
]

# Batch size for processing chunks of data
BATCH_SIZE = 32  # Adjust based on your data rate and system capabilities
CHUNK_SIZE = BATCH_SIZE  # Set chunk size to match batch size

print(f"Connected to EEG stream. Starting to record data to PostgreSQL database...")
print(f"Using batch size of {BATCH_SIZE} samples")
print("Press Ctrl+C to stop recording")

try:
    # Connect to the PostgreSQL database using psycopg3 connection string
    conn_string = " ".join(f"{key}={value}" for key, value in db_params.items())
    with psycopg.connect(conn_string) as conn:
        print("Connected to PostgreSQL database")
        
        # Create a cursor
        with conn.cursor() as cur:
            # Prepare SQL query - done once outside the loop
            column_str = ", ".join(["timestamp"] + columns)
            placeholders = ", ".join(["%s"] * (len(columns) + 1))
            sql = f"INSERT INTO eeg_data ({column_str}) VALUES ({placeholders})"
            
            while running:
                try:
                    # Pull chunks of samples at once
                    samples, timestamps = inlet.pull_chunk(max_samples=CHUNK_SIZE, timeout=0.5)
                    
                    # If no new samples available during timeout, continue checking running flag
                    if not samples or len(samples) == 0:
                        continue
                    
                    batch_data = []  # Collect data for batch insert
                    
                    # Get the current time for the last sample in the chunk
                    current_time = datetime.datetime.now(datetime.timezone.utc)
                    
                    # Calculate the time delta between samples
                    if len(timestamps) > 1:
                        # If we have multiple timestamps, calculate precise timing for each sample
                        # The last timestamp corresponds to current_time
                        last_timestamp = timestamps[-1]
                        
                        # Process each sample with its own timestamp
                        for i, (sample, ts) in enumerate(zip(samples, timestamps)):
                            # Check if sample length matches columns length
                            if len(sample) != len(columns):
                                print(f"Warning: Sample length ({len(sample)}) doesn't match expected column count ({len(columns)})")
                                continue
                            
                            # Calculate the precise timestamp for this sample
                            # Time difference in seconds from the last sample
                            time_delta = last_timestamp - ts
                            # Convert to timedelta and subtract from current_time
                            sample_time = current_time - datetime.timedelta(seconds=time_delta)
                            
                            # Prepare data with precise timestamp for each sample
                            data = [sample_time] + sample
                            batch_data.append(data)
                    else:
                        # If there's only one sample, use current_time
                        sample = samples[0]
                        if len(sample) != len(columns):
                            print(f"Warning: Sample length ({len(sample)}) doesn't match expected column count ({len(columns)})")
                        else:
                            data = [current_time] + sample
                            batch_data.append(data)
                    
                    if batch_data:
                        # Execute batch insert
                        cur.executemany(sql, batch_data)
                        conn.commit()
                        
                        print(f"Inserted batch of {len(batch_data)} samples at {current_time}")
                
                except Exception as e:
                    print(f"Error processing samples: {e}")
                    conn.rollback()
                    if not running:
                        break
            
            print("Recording stopped. Closing database connection...")
                    
except Exception as e:
    print(f"Database connection error: {e}")
finally:
    print("EEG recording terminated")
    sys.exit(0)
