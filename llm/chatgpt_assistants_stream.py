import openai
import os
from typing_extensions import override
from typing import List

import openai
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import RunStep, RunStepDelta

class ChatGPT():

    class EventHandler(AssistantEventHandler):    
        def __init__(self, response_buffer: List[str], process_partial_response: callable) -> None:
            super().__init__()
            self.response_buffer = response_buffer
            self.process_partial_response = process_partial_response
            self.partial_response = ""

        @override
        def on_event(self, event: AssistantStreamEvent) -> None:
            print("on_event called: " + event.event + "\n")

            if event.event == "thread.run.step.created":
                details = event.data.step_details
                if details.type == "tool_calls":
                    print("Generating code to interpret:\n\n```py")
            elif event.event == "thread.message.created":
                print("\nResponse:\n")

        @override
        def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
            print("on_text_delta called")
            print(delta.value, end="", flush=True)
            self.response_buffer.append(delta.value)
            self.partial_response += delta.value

            # 区切り文字をチェックして処理
            for split_word in ["、", "。", "？", "！"]:
                if split_word in self.partial_response:
                    print("partial_response" + self.partial_response)
                    self.process_partial_response(self.partial_response)
                    self.partial_response = ""

        # @override
        # def on_run_step_done(self, run_step: RunStep) -> None:
        #     print("on_run_step_done called")
        #     details = run_step.step_details
        #     if details.type == "tool_calls":
        #         for tool in details.tool_calls:
        #             if tool.type == "code_interpreter":
        #                 print("\n```\nExecuting code...")

        # @override
        # def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        #     print("on_run_step_delta called")
        #     details = delta.step_details
        #     if details is not None and details.type == "tool_calls":
        #         for tool in details.tool_calls or []:
        #             if tool.type == "code_interpreter" and tool.code_interpreter and tool.code_interpreter.input:
        #                 print(tool.code_interpreter.input, end="", flush=True)
    
    def __init__(self, valid_stream) -> None:
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
        )
        self.dialogue_history = ""
        self.valid_stream = valid_stream # 漸次的に応答を返す機能を有効にするか
        self.thread = self.client.beta.threads.create()
        self.assistant_id = "asst_z2nd92qpkV3ktiTDMMwwZEnG"


    def stream_responses(self, event_handler: AssistantEventHandler):
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id="asst_z2nd92qpkV3ktiTDMMwwZEnG",
            event_handler=event_handler,
        ) as stream:
            stream.until_done()

    # def get(self, user_utterance):
    #     self.client.beta.threads.messages.create(
    #         thread_id= self.thread.id,
    #         role="user",
    #         content=user_utterance[len(self.dialogue_history):],
    #     )
    #     self.dialogue_history = user_utterance

    #     with self.client.beta.threads.runs.stream(
    #         thread_id=self.thread.id,
    #         assistant_id=self.assistant_id,
    #         event_handler=self.EventHandler(),
    #     ) as stream:
    #         stream.until_done()

    #     return messages.data[0].content[0].text.value
