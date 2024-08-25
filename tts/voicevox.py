import requests
import json
import time

asap = "http://192.168.1.161:50021"
local = "http://localhost:50021"


def get_audio_query(text, speaker):
    query_payload = {"text": text, "speaker": speaker}
    while True:
        try:
            url = asap + "/audio_query"
            r = requests.post(url, params=query_payload, timeout=(10.0, 300.0))
            if r.status_code == 200:
                return r.json()

        except requests.exceptions.ConnectionError:
            print("fail connect...", url)
            time.sleep(0.1)


def run_synthesis(query_data, speaker):
    synth_payload = {"speaker": speaker}
    while True:
        try:
            url = asap + "/synthesis"
            r = requests.post(
                url,
                params=synth_payload,
                data=json.dumps(query_data),
                timeout=(10.0, 300.0),
            )
            if r.status_code == 200:
                return r.content
        except requests.exceptions.ConnectionError:
            print("fail connect...", url)
            time.sleep(0.1)


def extract_wav_length(query_data):
    length = 0
    for accent_phrase in query_data["accent_phrases"]:
        for mora in accent_phrase["moras"]:
            if mora["consonant_length"] != None:
                length += mora["consonant_length"]
            if mora["vowel_length"] != None:
                length += mora["vowel_length"]
    return length


def get_audio_file_from_text(text, voicevox_id):
    query_data = get_audio_query(text, voicevox_id)
    return run_synthesis(query_data, voicevox_id), extract_wav_length(query_data)
