# memerag_v2_2pro.py
# MemeRAG v2.2 Pro - Main Runner

mode = "gradio"  # Change to "chat" to use the console loop

if mode == "gradio":
    import memerag_gradio_ui
elif mode == "chat":
    import memerag_chat_loop
else:
    print("❌ Invalid mode. Choose 'gradio' or 'chat'.")
