# 🤖 MemeRAG v2.2 Pro

Your AI-powered meme retrieval and generation agent.  
Built with modular design, flexible tools, and ready for both console and web interface use.

---

## 📂 Folder Structure

```plaintext
📁 meme_rag/
├── 📁 meme_fns/                  
│   ├── intent_classifier.py
│   ├── smart_meme_rag_manager.py
│   ├── memes_list.py
│   ├── components.py
│
├── 📁 meme_config/               
│   └── openai_key.txt
│
├── 📁 memes/                     
│   └── (All meme images/gifs here)
│
├── memerag_gradio_ui.py         
├── memerag_chat_loop.py         
├── memerag_v2_2pro.py           # Main runner
├── requirements.txt
├── README.md

├── 📁 obsolete/                  
│   ├── 📁 examples/
│   │   └── memerag_integration_example.py
│   ├── memerag_v1_0.py
│   ├── memerag_v2_0.py
│   ├── memerag_v2_1.py

├── 📁 chats/                     
│   ├── memerag_chatlog_v2_2.csv
│   ├── other logs...
````

## 🚀 How to Run
🔹 Option 1 — Main Runner
bash
Copy
Edit
python memerag_v2_2pro.py
Default mode is Gradio web app.

Change mode to "chat" inside the file to use console chat loop.

🔹 Option 2 — Classic Chat Loop
bash
Copy
Edit
python memerag_chat_loop.py
🔹 Option 3 — Gradio Web App
bash
Copy
Edit
python memerag_gradio_ui.py
🧠 How MemeRAG Works
Embedder converts user input into vectors.

Retriever searches memes semantically.

Intent Classifier detects input intent and filters memes.

Selector picks the best meme.

Result is displayed as meme + caption.

📝 Customization
Update memes → memes_list.py

Change intent keywords → intent_classifier.py

Adjust selection logic → smart_meme_rag_manager.py / components.py

🔒 API Keys
Place OpenAI API key in:

plaintext
Copy
Edit
meme_config/openai_key.txt
🗃 Obsolete Versions
Older scripts archived in obsolete/.
Reference examples in obsolete/examples/.

🔗 GitHub + Colab Use
Clone repo:

bash
Copy
Edit
!git clone https://github.com/YourUsername/meme_rag.git
%cd meme_rag
Install requirements:

bash
Copy
Edit
!pip install -r requirements.txt
Run:

python
Copy
Edit
import memerag_gradio_ui  # Or use memerag_v2_2pro.py
All modular imports will work automatically.

👑 Credits
Created and managed by Parnal Sinha.
