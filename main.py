import os
import chainlit as cl
from openai import AsyncOpenAI 
from agents import Runner, Agent, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

external_client= AsyncOpenAI( 
  api_key=openrouter_api_key,
  base_url="https://openrouter.ai/api/v1/"
 )

# --- CHANGED MODEL TO LLAMA (Less likely to be rate limited) ---
model = OpenAIChatCompletionsModel(
    model="meta-llama/llama-3.2-3b-instruct:free",
    openai_client=external_client,
)
# ---------------------------------------------------------------

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
async def handle_start():                                                                     #history set of user
    cl.user_session.set("history",[])                                                                          

@cl.on_message
async def handle_message(message : cl.Message):


    history = cl.user_session.get("history")
    history.append({"role": "user", "content":message.content})                           #history get of user

    msg = cl.Message(content="")                                                         #steamingg response  1
    await msg.send()

    result = Runner.run_streamed(
        agent,
        input = history,
        run_config=config
    )
    
    # --- THIS HANDLES THE STREAMING CORRECTLY ---
    async for event in result.stream_events():
        if hasattr(event, 'data') and hasattr(event.data, 'delta'):
            delta = event.data.delta
            
    
            if isinstance(delta, str):
                await msg.stream_token(delta)
                
           
            elif hasattr(delta, 'content') and delta.content:
                await msg.stream_token(delta.content)


    history.append({"role":"assistant", "content":msg.content})                   #history get and set of assistant
    cl.user_session.set("history",history)


    await msg.update()