import openai
import os

class ChatGPT():
    def __init__(self, valid_stream) -> None:
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        self.dialogue_history = []
        self.valid_stream = valid_stream # 漸次的に応答を返す機能を有効にするか
        self.thread = client.beta.threads.create()

    def get(self, user_utterance):
        self.dialogue_history.append({"role": "user", "content": user_utterance})
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_utterance,
            stream = self.valid_stream
        )
        run = self.client.beta.threads.runs.create_and_poll( 
            thread_id=thread.id,
            assistant_id="asst_z2nd92qpkV3ktiTDMMwwZEnG",
        )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            print(messages)
        else:
            print(run.status)
                
        return messages

def main():
    agent_utterance = self.llm.get("本日はどうされましたか？")
    print(agent_utterance)


if __name__ == "__main__":
    main()


# # gets API Key from environment variable OPENAI_API_KEY
# client = openai.OpenAI(
#     # This is the default and can be omitted
#     api_key=os.getenv('OPENAI_API_KEY'),
# )

# assistant = client.beta.assistants.create(
#     name="体調不良を訴える患者",
#     instructions='''このGPTは、病院へ診療しに来た患者・山本ゆうきとして振る舞う。
#     短く、要点を押さえた対話を心がけ、一言か二言での返答を提供する。患者の立場からの質問や心配を簡潔に表現し、医療従事者のトレーニングや練習に役立てる。
#     リアルな患者の振る舞いを模倣し、様々な症状や背景ストーリーを持つ患者の役割を果たすが、過度な医療知識の提供や実際の診断、治療に関するアドバイスや質問は避ける。''',
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-3.5-turbo",
# )

# thread = client.beta.threads.create()


# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="本日はどうされましたか？",
# )

# run = client.beta.threads.runs.create_and_poll(
#     thread_id=thread.id,
#     assistant_id=assistant.id,
# )

# print("Run completed with status: " + run.status)

# if run.status == "completed":
#     messages = client.beta.threads.messages.list(thread_id=thread.id)

#     print("messages: ")
#     for message in messages:
#         assert message.content[0].type == "text"
#         print({"role": message.role, "message": message.content[0].text.value})

#     client.beta.assistants.delete(assistant.id)