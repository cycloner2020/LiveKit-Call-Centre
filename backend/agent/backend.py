from __future__ import annotations

import logging
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai
from dotenv import load_dotenv
from api import AssistantFnc
from prompts import INSTRUCTIONS, LOOKUP_VIN_MESSAGE, WELCOME_MESSAGE
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
logger = logging.getLogger("myagent")
logger.setLevel(logging.INFO)

logger.info("Backend module initialized")

async def entrypoint(ctx: JobContext):
    logger.info("Starting entrypoint function")
    
    logger.info("Connecting to context with auto-subscribe")
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    logger.info("Successfully connected to context")

    logger.info("Waiting for participant")
    await ctx.wait_for_participant()
    logger.info("Participant connected")

    logger.info("Initializing OpenAI realtime model")
    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS,
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
    )
    logger.info("Model initialized with instructions and parameters")

    logger.info("Creating assistant function context")
    assistant_fnc = AssistantFnc()
    
    logger.info("Creating multimodal agent")
    assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
    
    logger.info("Starting assistant in room")
    assistant.start(ctx.room)
    logger.info("Assistant started successfully")

    logger.info("Getting initial session")
    session = model.sessions[0]
    logger.info("Creating welcome message in conversation")
    session.conversation.item.create(
      llm.ChatMessage(
        role="assistant",
        content=WELCOME_MESSAGE,
      )
    )
    logger.info("Creating initial response")
    session.response.create()
    logger.info("Initial session setup completed")

    @session.on("user_speech_committed")
    def on_user_speech_committed(msg: llm.ChatMessage):
        logger.info("User speech committed event received")
        
        # convert string lists to strings, drop images
        if isinstance(msg.content, list):
            logger.info("Converting message content from list to string")
            msg.content = "\n".join(
                "[image]" if isinstance(x, llm.ChatImage) else x for x in msg
            )
            logger.info("Converted message content: %s", msg.content)

        if assistant_fnc.has_car():
            logger.info("Car exists in context, handling query")
            handle_query(msg)
        else:
            logger.info("No car in context, finding profile")
            find_profile(msg)

    def find_profile(msg: str):
        logger.info("Finding profile for message: %s", msg)
        logger.info("Creating VIN lookup message")
        session.conversation.item.create(
        llm.ChatMessage(
            role="system",
            content=LOOKUP_VIN_MESSAGE(msg),
            )
        )
        logger.info("Creating response for VIN lookup")
        session.response.create()

    def handle_query(msg: str):
        logger.info("Handling user query: %s", msg.content)
        logger.info("Creating conversation message for query")
        session.conversation.item.create(
        llm.ChatMessage(
            role="user",
            content=msg.content,
            )
        )
        logger.info("Creating response for user query")
        session.response.create()

if __name__ == "__main__":
    logger.info("Starting application")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    logger.info("Application started")
