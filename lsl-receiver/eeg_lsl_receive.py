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

print(f"Connected to EEG stream. Starting to record data to PostgreSQL database...")
print("Press Ctrl+C to stop recording")

try:
    # Connect to the PostgreSQL database using psycopg3 connection string
    conn_string = " ".join(f"{key}={value}" for key, value in db_params.items())
    with psycopg.connect(conn_string) as conn:
        print("Connected to PostgreSQL database")
        
        # Create a cursor
        with conn.cursor() as cur:
            while running:
                try:
                    sample, timestamp = inlet.pull_sample(timeout=0.5)  # Add timeout to check running flag periodically
                    
                    # If no new sample available during timeout, continue checking running flag
                    if sample is None:
                        continue
                        
                    current_time = datetime.datetime.now(datetime.timezone.utc)
                    
                    # Check if sample length matches columns length
                    if len(sample) != len(columns):
                        print(f"Warning: Sample length ({len(sample)}) doesn't match expected column count ({len(columns)})")
                        continue
                    
                    # Prepare SQL query
                    column_str = ", ".join(["timestamp"] + columns)
                    # Use positional parameters for psycopg3
                    placeholders = ", ".join(["%s"] * (len(columns) + 1))
                    sql = f"INSERT INTO eeg_data ({column_str}) VALUES ({placeholders})"
                    
                    # Prepare data with current timestamp
                    data = [current_time] + sample
                    
                    # Execute the query
                    cur.execute(sql, data)
                    conn.commit()
                    
                    print(f"Inserted data at {current_time}")
                except Exception as e:
                    print(f"Error processing sample: {e}")
                    conn.rollback()
                    if not running:
                        break
            
            print("Recording stopped. Closing database connection...")
                    
except Exception as e:
    print(f"Database connection error: {e}")
finally:
    print("EEG recording terminated")
    sys.exit(0)
