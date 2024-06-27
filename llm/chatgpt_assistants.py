import openai
import os

class ChatGPT():
    def __init__(self, assistant_id, valid_stream) -> None:
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        self.assistant_id = assistant_id
        self.valid_stream = valid_stream # 漸次的に応答を返す機能を有効にするか
        self.thread = self.client.beta.threads.create()

    def get(self, user_utterance):
        message = self.client.beta.threads.messages.create(
            thread_id= self.thread.id,
            role="user",
            content=user_utterance,
        )
        run = self.client.beta.threads.runs.create_and_poll( 
            thread_id = self.thread.id,
            assistant_id = self.assistant_id,
        )
        if run.status == 'completed': 
            messages = self.client.beta.threads.messages.list(
                thread_id= self.thread.id
            )
            print("messages: " + messages.data[0].content[0].text.value)
        else:
            print("run.status: ")
            print( run.status)
                
        return messages.data[0].content[0].text.value
