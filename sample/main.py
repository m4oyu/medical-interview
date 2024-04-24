from __future__ import division

import re
import os
import sys

from google.cloud import speech

import openai

import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


# gets API Key from environment variable OPENAI_API_KEY
openai_client = openai.OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv('OPENAI_API_KEY'),
)


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def send_to_gpt(text, assistant, thread):
    print("send_to_gpt called")
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text,
    )

    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    print("Run completed with status: " + run.status)

    if run.status == "completed":
        messages = openai_client.beta.threads.messages.list(thread_id=thread.id)

        print("messages: ")
        for message in messages:
            assert message.content[0].type == "text"
            print({"role": message.role, "message": message.content[0].text.value})

        openai_client.beta.assistants.delete(assistant.id)


def listen_print_loop(responses, assistant, thread):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            send_to_gpt(transcript, assistant, thread)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./credentials/medical-interview-420407-ce680056c929.json"

    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='ja-JP',
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    assistant = openai_client.beta.assistants.create(
        name="体調不良を訴える患者",
        instructions='''このGPTは、病院へ診療しに来た患者・山本ゆうきとして振る舞う。
        短く、要点を押さえた対話を心がけ、一言か二言での返答を提供する。患者の立場からの質問や心配を簡潔に表現し、医療従事者のトレーニングや練習に役立てる。
        リアルな患者の振る舞いを模倣し、様々な症状や背景ストーリーを持つ患者の役割を果たすが、過度な医療知識の提供や実際の診断、治療に関するアドバイスや質問は避ける。''',
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo",
    )

    thread = openai_client.beta.threads.create()

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses, assistant, thread)


if __name__ == "__main__":
    main()