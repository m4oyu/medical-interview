from stt import google_stt
from vad import google_vad
from llm import chatgpt_assistants
from tts import voicevox
import threading
from playsound import playsound
import time
import argparse
import sys
from dotenv import load_dotenv
import recording
from logger import logger

load_dotenv()  # take environment variables from .env.


class Main:

    def __init__(self, assistant_id) -> None:
        self.valid_stream = False

        self.vad = google_vad.GOOGLE_WEBRTC()
        self.vad_thread = threading.Thread(
            target=self.vad.vad_loop,
            args=(self.callback_vad,),
        )
        self.stt_thread = threading.Thread(
            target=google_stt.main,
            args=(
                self.callback_interim,
                self.callback_final,
            ),
        )
        self.llm = chatgpt_assistants.ChatGPT(
            assistant_id=assistant_id, valid_stream=self.valid_stream
        )

        # 対話履歴の差分で発話を認識する
        self.latest_user_utterance = None
        self.dialogue_history = ""

        # 計測用
        self.time_user_speeching_end = None
        self.turn_taking_count = 0

        # 排他制御用のロック
        self.dialogue_history_lock = threading.Lock()
        self.main_process_lock = threading.Lock()

        self.stt_thread.start()
        self.vad_thread.start()

    def wait(self):
        thread_list = threading.enumerate()
        thread_list.remove(threading.main_thread())
        for thread in thread_list:
            thread.join()

    def callback_interim(self, user_utterance):
        with self.dialogue_history_lock:
            logger.debug("callback_interim: " + user_utterance)
            logger.debug("dialogue_history: " + self.dialogue_history)
            self.latest_user_utterance = user_utterance

    def callback_final(self, user_utterance):
        with self.dialogue_history_lock:
            logger.debug("callback_final: " + user_utterance)
            logger.debug("dialogue_history: " + self.dialogue_history)
            self.dialogue_history = self.dialogue_history[len(user_utterance) :]

    def callback_vad(self, flag):
        if flag == True:  # 発話のはじめ
            if self.latest_user_utterance != None:
                logger.debug(
                    "callback_vad flag is true, latest_user_utterance="
                    + self.latest_user_utterance
                )
        elif self.latest_user_utterance != None:  # 発話の終わり
            if self.latest_user_utterance != None:
                logger.debug(
                    "callback_vad flag is false, latest_user_utterance="
                    + self.latest_user_utterance
                )

            self.time_user_speeching_end = time.time()

            with self.dialogue_history_lock:
                user_utt = self.latest_user_utterance[len(self.dialogue_history) :]
                self.dialogue_history = self.latest_user_utterance

            if user_utt.strip() == "終了":
                print("プログラムを終了します。")
                logger.info("会話ターン数: " + str(self.turn_taking_count) + "\n")
                self.vad.shutdown()
                recording.stop()
                sys.exit(0)

            if len(user_utt) <= 0:
                return

            logger.info("User:   " + user_utt)

            threading.Thread(
                target=self.main_process,
                args=(user_utt,),
            ).start()

    def main_process(self, user_utterance):
        with self.main_process_lock:
            agent_utterance = self.llm.get(user_utterance)
            logger.info("System: " + agent_utterance)
            if self.valid_stream == False:
                self.turn_taking_count += 1
                wav_data, _ = voicevox.get_audio_file_from_text(agent_utterance)
                self.audio_play(wav_data)

    def audio_play(self, wav_data):
        start_time = time.time()
        with open("tmp.wav", mode="bw") as f:
            f.write(wav_data)
        if self.time_user_speeching_end != None:
            print("応答までの時間", time.time() - self.time_user_speeching_end)
        self.time_user_speeching_end = None
        playsound("tmp.wav")  # ./doc/playsound_issue.md


if __name__ == "__main__":
    recording.start()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "assistant",
        type=str,
        choices=["okada", "sakamoto", "tanaka"],
        help="対話相手となるアシスタントの名前を指定します。利用可能なアシスタントは、okada、sakamoto、tanaka です。",
    )
    args = parser.parse_args()
    assistant_ids = {
        "okada": "asst_naZAtdVwSUKvWQdEqwsTxVTn",
        "sakamoto": "asst_8c8S3HjgZnRlBocIGYKtgQPn",
        "tanaka": "asst_pZJeMVb6yEC6232AGzhMa5Bm",
    }
    selected_assistant_id = assistant_ids[args.assistant]
    print("Selected assistant:", args.assistant)

    ins = Main(selected_assistant_id)
    ins.wait()
