#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
NeProMahBot is a sophisticated Telegram assistant powered by GPT.
Designed to help users with various tasks, it offers quick answers, scheduling assistance, and engaging conversations.
NeProMahBot understands and responds accurately and efficiently, enhancing your Telegram experience for both personal and professional use.

Usage:
"""

import logging
import os


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater

import openai
import json

# TBD remove
from functools import partial


# Set up logging library
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)



# Function to be called when messages are received
async def process_msg(update: Update, context: ContextTypes.DEFAULT_TYPE, gpt_client, assistant_id) -> None:
    
    # Receive message from user
    user_tg_msg_text = update.message.text
    logger.info(
        f"User {update._effective_user.id} {update._effective_user.full_name} message: {user_tg_msg_text}")


    # tbd
    thread = gpt_client.beta.threads.create()
    message = gpt_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_tg_msg_text,
    )   
    
    run = gpt_client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant_id)
    print("Run completed with status: " + run.status)
    
    print("Message created with ID: " + message.id)
    
    if run.status == "completed":
        messages = gpt_client.beta.threads.messages.list(thread_id=thread.id)
        gpt_responce = messages.data[0].content[0].text.value
    else:
        gpt_responce = "I'm sorry, I couldn't understand your message."

    await update.message.reply_text(gpt_responce)
    
    # send log to admin
    admin_log_responce = f"User {update._effective_user.full_name} ID {update._effective_user.id} said: {user_tg_msg_text}\nGPT respond: {gpt_responce}"
    await context.bot.send_message(chat_id="242426387", text=admin_log_responce)
            


def main() -> None:
    """Start the bot."""
    # Retrieve environment variables
    TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
    GPT_API_TOKEN = os.getenv('GPT_API_TOKEN')

    GPT_ASSISTANT_ID = os.getenv('GPT_ASSISTANT_ID') # ChatGPT Acc: klimdos, Default project, assistant Name: RIFFEL‘STUDIO
    
    # Check if environment variables are set
    if TG_BOT_TOKEN is None:
        raise ValueError("TG_BOT_TOKEN environment variable is not set")
    if GPT_API_TOKEN is None:
        raise ValueError("GPT_API_TOKEN environment variable is not set")
    if GPT_ASSISTANT_ID is None:
        raise ValueError("GPT_ASSISTANT_ID environment variable is not set")
    
    # Create the OpenAI client
    gpt_client = openai.OpenAI(api_key=GPT_API_TOKEN)
    

    # Create Telegram application and pass your bot's token.
    tg_app = Application.builder().token(TG_BOT_TOKEN).build()

    # handle commands
    #application.add_handler(CommandHandler("about", lambda update, context: about(update, context, markdown_string)))

    # execute process_msg func on every message on Telegram
    # add /start handler
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, partial(process_msg, gpt_client=gpt_client, assistant_id=GPT_ASSISTANT_ID)))

    # Run the bot until the user presses Ctrl-C
    tg_app.run_polling()


if __name__ == "__main__":
    main()
