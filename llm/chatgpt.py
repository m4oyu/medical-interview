from openai import OpenAI
import os


class ChatGPT:

    def __init__(self, valid_stream) -> None:
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.dialogue_history = []
        self.valid_stream = valid_stream  # 漸次的に応答を返す機能を有効にするか

    def get(self, user_utterance):
        self.dialogue_history.append({"role": "user", "content": user_utterance})
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.dialogue_history,
            stream=self.valid_stream,
        )
        print(completion.choices[0].message.content)
        return completion

    def set_agent_utterance(self, agent_utterance):
        self.dialogue_history.append({"role": "assistant", "content": agent_utterance})
