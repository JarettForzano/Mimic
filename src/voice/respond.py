import re
from deepgram import (
    DeepgramClient,
    SpeakOptions,
)
from pydub import AudioSegment
from pydub.playback import play


def chunk_text_by_sentence(text):
    # Find sentence boundaries using regular expression
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]

    chunks = []
    start = 0
    # Split the text into chunks based on sentence boundaries
    for boundary_index in boundaries_indices:
        chunks.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    chunks.append(text[start:].strip())

    return chunks

def synthesize_audio(text, api_Key):
    # Create a Deepgram client using the API key
    deepgram = DeepgramClient(api_key=api_Key)
    # Choose a model to use for synthesis
    options = SpeakOptions(
            model="aura-luna-en",
        )
    speak_options = {"text": text}
    # Synthesize audio and stream the response
    response =  deepgram.speak.v("1").stream(speak_options, options)
    # Get the audio stream from the response
    audio_buffer = response.stream
    audio_buffer.seek(0)
    # Load audio from buffer using pydub
    audio = AudioSegment.from_mp3(audio_buffer)

    return audio

"""
def main():
    # Chunk the text into smaller parts
    chunks = chunk_text_by_sentence(input_text)

    # Synthesize each chunk into audio and play the audio
    for chunk_text in chunks:
        audio = synthesize_audio(chunk_text, "API_KEY")
        play(audio)

if __name__ == "__main__":
    main()

"""