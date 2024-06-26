from stt import google_stt
from vad import google_vad
from llm import chatgpt
from tts import voicevox
import threading
from playsound import playsound
import time


class Main:

    def __init__(self) -> None:
        self.valid_stream = False
        vad = google_vad.GOOGLE_WEBRTC()
        vad_thread = threading.Thread(target=vad.vad_loop, args=(self.callback_vad,))
        stt_thread = threading.Thread(
            target=google_stt.main,
            args=(
                self.callback_interim,
                self.callback_final,
            ),
        )
        self.llm = chatgpt.ChatGPT(valid_stream=self.valid_stream)

        self.latest_user_utterance = None
        self.finished_user_speeching = False

        # 計測用
        self.time_user_speeching_end = None

        stt_thread.start()
        vad_thread.start()

    def wait(self):
        thread_list = threading.enumerate()
        thread_list.remove(threading.main_thread())
        for thread in thread_list:
            thread.join()

    def callback_interim(self, user_utterance):
        print("callback_interim: " + user_utterance)
        self.latest_user_utterance = user_utterance

    def callback_final(self, user_utterance):
        print("callback_final: " + user_utterance)
        self.latest_user_utterance = user_utterance

    def callback_vad(self, flag):
        if flag == True:  # 発話のはじめ
            if self.latest_user_utterance != None:
                print(
                    "callback_vad flag is true, latest_user_utterance="
                    + self.latest_user_utterance
                )

        elif self.latest_user_utterance != None:  # 発話の終わり
            if self.latest_user_utterance != None:
                print(
                    "callback_vad flag is false, latest_user_utterance="
                    + self.latest_user_utterance
                )
            self.time_user_speeching_end = time.time()
            threading.Thread(
                target=self.main_process, args=(self.latest_user_utterance,)
            ).start()

    def main_process(self, user_utterance):
        llm_result = self.llm.get(user_utterance)
        if self.valid_stream == False:
            agent_utterance = llm_result.choices[0].message.content
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
    ins = Main()
    ins.wait()
