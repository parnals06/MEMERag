# memerag_gradio_ui.py
# MemeRAG v2.2 Pro — Gradio UI

import gradio as gr
from meme_fns.components import get_rag_manager
from meme_fns.memes_list import meme_examples
import os

MEME_FOLDER = 'memes'  # Adjust if different

rag = get_rag_manager()

def get_meme_path(filename):
    if not filename:
        return None

    # Get the absolute path to avoid relative path problems
    path = os.path.abspath(os.path.join(MEME_FOLDER, filename))
    print(f"[DEBUG] Looking for meme at: {path}")

    if os.path.exists(path):
        print(f"[DEBUG] Meme FOUND at: {path}")
        return path
    else:
        print(f"[WARNING] Meme NOT found at: {path}")
        return None

def respond_to_input(user_input):
    meme_filename = rag.run(user_input)
    meme_path = get_meme_path(meme_filename)

    if meme_path:
        return meme_filename, meme_path
    else:
        return "No meme found.", None

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 MemeRAG v2.2 Pro — Chat with Memes")

    user_input = gr.Textbox(label="Your Message")
    meme_name = gr.Textbox(label="Meme Selected", interactive=False)
    meme_display = gr.Image(label="Meme", type="filepath")

    submit_btn = gr.Button("Generate Meme")

    def on_submit(message):
        filename, path = respond_to_input(message)
        return filename, path

    submit_btn.click(
        fn=on_submit,
        inputs=[user_input],
        outputs=[meme_name, meme_display]
    )

    # Optional Stretch: Like / Dislike buttons can be added here in future.

demo.launch()
