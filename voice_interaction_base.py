from stt import google_stt

# from vad import google_vad
from llm import chatgpt
from tts import voicevox
import threading
from playsound import playsound
import time


class Main:

    def __init__(self) -> None:
        stt_thread = threading.Thread(
            target=google_stt.main,
            args=(
                self.callback_interim,
                self.callback_final,
            ),
        )
        self.llm = chatgpt.ChatGPT(valid_stream=False)

        self.latest_user_utterance = None
        self.finished_user_speeching = False

        # 計測用
        # vad = google_vad.GOOGLE_WEBRTC()
        # vad_thread = threading.Thread(target=vad.vad_loop, args=(self.callback_vad, ))
        # vad_thread.start()
        # self.time_user_speeching_end = None

        stt_thread.start()

    def wait(self):
        thread_list = threading.enumerate()
        thread_list.remove(threading.main_thread())
        for thread in thread_list:
            thread.join()

    def callback_interim(self, user_utterance):
        self.latest_user_utterance = user_utterance

    def callback_final(self, user_utterance):
        self.latest_user_utterance = user_utterance
        threading.Thread(
            target=self.main_process, args=(self.latest_user_utterance,)
        ).start()

    # def callback_vad(self, flag):
    #     if flag == False:
    #         print("vad")
    #         self.time_user_speeching_end = time.time()

    def main_process(self, user_utterance):
        llm_result = self.llm.get(user_utterance)
        wav_data, _ = voicevox.get_audio_file_from_text(
            llm_result.choices[0].message.content
        )
        self.audio_play(wav_data)

    def audio_play(self, wav_data):
        with open("tmp.wav", mode="bw") as f:
            f.write(wav_data)
        # if self.time_user_speeching_end != None:
        #     print("応答までの時間", time.time() - self.time_user_speeching_end)
        self.time_user_speeching_end = None
        playsound("tmp.wav")


if __name__ == "__main__":
    ins = Main()
    ins.wait()
