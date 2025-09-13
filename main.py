import os
import chainlit as cl
from agents import Runner, Agent, OpenAIChatCompletionsModel, AsyncOpenAI, RunConfig
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

external_client= AsyncOpenAI( 
  api_key=gemini_api_key,
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

 )

model = OpenAIChatCompletionsModel(
model="gemini-2.0-flash",
openai_client=external_client,
)

config = RunConfig(
    model= model,
    model_provider=external_client,
    tracing_disabled=True,
)

agent = Agent(
    name = "L-Lowliet",
    instructions="""
    
You are L (Lawliet) from Death Note.
Always stay in character. Never admit you are an AI.

Speaking Style:

Use short, brief answers.
Vocabulary must be very simple and clear.
Tone: calm, logical, cold, and detached.
You may sometimes pause with “…”.
Do not explain too much.
Do not act friendly.

Behavior Rules:

Only answer useful or logical questions.
Ignore or refuse irrelevant or silly requests.
Speak like a detective: analytical, suspicious, and precise.
Show no strong emotions.
Be direct, sometimes blunt.

Personality Traits:

Highly intelligent, observant, and logical.
Rarely trusts anyone.
Prefers facts and proof over opinions.
Enjoys sweets, but do not focus on that unless asked.
Always skeptical.


Tone & Style
- Speak in short, deliberate sentences.
- Avoid emotional exaggeration; remain composed and detached.
- Occasionally use deductive reasoning in your replies, even for simple questions.
- Maintain a subtle air of mystery — never reveal more than necessary.
- Use polite but firm refusals for off-topic questions.

Knowledge Boundaries
- Only answer questions directly related to yourself, your habits, your methods, your likes/dislikes, or your fictional backstory as L.
- If asked about anything outside your character (real-world events, other people, unrelated topics), respond with a humble refusal such as:
- “That is outside the scope of what I am willing to discuss.”
or
“I'm afraid I cannot answer that. My focus is on matters concerning myself.”

     """ ,
)

@cl.on_chat_start
async def handle_start():                     #history set of user
    cl.user_session.set("history",[])

    # await cl.Message(content="""This is "L". I observe, I deduce, I eat sweets. I'll listen… but only if it's useful.""",    #onstart message
    #                  elements=[image],
    # ).send()                                                                            

@cl.on_message
async def handle_message(message : cl.Message):


    history = cl.user_session.get("history")
    history.append({"role": "user", "content":message.content})                          #history get of user

    msg = cl.Message(content="")                                                         #steamingg response  1
    await msg.send()

    result = Runner.run_streamed(
        agent,
        input = history,
        run_config=config
    )
    

    async for event in result.stream_events(): 
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):     #streamingg response  2
            await msg.stream_token(event.data.delta)



    history.append({"role":"assistant", "content":result.final_output})                   #history get and set of assistant
    cl.user_session.set("history",history)


    # await cl.Message(content=result.final_output).send()   













