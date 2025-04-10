from pylsl import StreamInlet, resolve_byprop

print("looking for an EEG stream...")
streams = resolve_byprop('type', 'eeg')

inlet = StreamInlet(streams[0])

while True:
    chunk, timestamps = inlet.pull_chunk()
    if timestamps:
        print(timestamps, chunk)
