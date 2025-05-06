# memerag_chat_loop.py
# MemeRAG v2.2 Pro — Simple Chat Loop

from meme_fns.components import get_rag_manager
from meme_fns.memes_list import meme_examples

import os
from IPython.display import Image
import pandas as pd
from datetime import datetime
import time

# ---- INIT ----

MEME_FOLDER = 'memes'  # Adjust if different

rag = get_rag_manager()

# ---- Chat Log ----
chat_log = []

def show_meme(filename):
    path = os.path.join(MEME_FOLDER, filename)
    if os.path.exists(path):
        display(Image(filename=path))
    else:
        print(f"⚠️ Meme image not found: {path}")

def save_chatlog(log, filename="chatlog.csv"):
    df = pd.DataFrame(log)
    df.to_csv(filename, index=False)
    print(f"✅ Chat log saved as {filename}")

# ---- CHAT LOOP ----

print("🎉 MemeRAG Chat Ready! Type 'quit' to exit.")

while True:
    user_input = input("\n📝 You: ")

    if user_input.lower() in ['quit', 'exit']:
        break

    meme_filename = rag.run(user_input)

    if meme_filename:
        print(f"🤖 Meme selected: {meme_filename}")
        show_meme(meme_filename)
    else:
        print("⚠️ No meme found for this input.")

    chat_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "meme_selected": meme_filename if meme_filename else "None"
    })

# ---- SAVE LOG ----
save_chatlog(chat_log, filename="chats/memerag_chatlog_v2_2.csv")
