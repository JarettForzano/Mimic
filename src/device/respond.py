import re
import requests

DEEPGRAM_URL = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
headers = {
    "Authorization": "Token KEY_HERE",
    "Content-Type": "application/json"
}

def segment_text_by_sentence(text):
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]
    
    segments = []
    start = 0
    for boundary_index in boundaries_indices:
        segments.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    segments.append(text[start:].strip())

    return segments

def synthesize_audio(text, output_file):
    payload = {"text": text}
    with requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload) as r:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                output_file.write(chunk)

def main():
    text = ""
    segments = segment_text_by_sentence(text)

    # Create or truncate the output file
    with open("output.mp3", "wb") as output_file:
        for segment_text in segments:
            synthesize_audio(segment_text, output_file)

    print("Audio file creation completed.")

if __name__ == "__main__":
    main()


