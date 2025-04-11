import pandas as pd
from pylsl import StreamInfo, StreamOutlet  # pip install pylsl
import time

# Load data
data_dir = "../000_000.tsv"
df = pd.read_csv(data_dir, sep="\t")

# Create stream
info = StreamInfo("EEG_Stream", 'eeg', 36, 500, 'float32', 'testEEGStream')
outlet = StreamOutlet(info)

while True:
    for index, row in df.iterrows():
        outlet.push_sample(row.iloc[1:].tolist())
        time.sleep(1 / 500)
