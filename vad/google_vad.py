import pyaudio as pa
import webrtcvad
import time

# https://pypi.org/project/webrtcvad-wheels/
# sample_rateは 8000, 16000, 32000 or 48000 Hzのいずれか
RATE = 16000
# duration timeは10, 20, 30 msのいずれか
BUFFER_SIZE = 160  # 10ms


class GOOGLE_WEBRTC:

    def __init__(self):

        # ストリーム準備
        self.audio = pa.PyAudio()
        self.stream = self.audio.open(
            rate=RATE,
            channels=2,
            format=pa.paInt16,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
        )

        if self.stream == None:
            raise EnvironmentError("audio streamが開けませんでした")

        # 無音区間検出
        self.vad = webrtcvad.Vad(3)
        self.thread_alive = True

    def vad_loop(self, callback):
        self.before_result = False
        while self.thread_alive:
            # ストリームからデータを取得
            audio_data = self.stream.read(BUFFER_SIZE, exception_on_overflow=False)
            vad_result = self.vad.is_speech(audio_data, RATE)
            # print(vad_result)
            if vad_result != self.before_result:
                if callback != None:
                    # print("====================vad callback=========================")
                    callback(vad_result)
                self.before_result = vad_result

            time.sleep(0.2)

    def shutdown(self):
        self.thread_alive = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


def on_vad_changed(is_speech):
    if is_speech:
        print("Speech has started...")
    else:
        print("Speech has ended...")


def main():
    try:
        vad_system = GOOGLE_WEBRTC()
        vad_system.vad_loop(on_vad_changed)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        vad_system.shutdown()


if __name__ == "__main__":
    main()
