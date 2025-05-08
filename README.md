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

### 🔷 Option 1 — Main Runner

```
bash
python memerag_v2_2pro.py 
```

*Default mode is Gradio web app.*

Change mode to "chat" inside the file to use console chat loop.

---

### 🔷 Option 2 — Classic Chat Loop

```bash
python memerag_chat_loop.py 
```

### 🔷 Option 3 — Gradio Web App

```bash
python memerag_gradio_ui.py
```

🧠 **How MemeRAG Works**

* Embedder converts user input into vectors.
* Retriever searches memes semantically.
* Intent Classifier detects input intent and filters memes.
* Selector picks the best meme.
* Result is displayed as meme + caption.

---

### 📝 Customization

* Update memes → `memes_list.py`
* Change intent keywords → `intent_classifier.py`
* Adjust selection logic → `smart_meme_rag_manager.py` / `components.py`

---

### 🔐 API Keys

Place OpenAI API key in:

```plaintext
meme_config/openai_key.txt
```

🗂 Obsolete versions archived in `obsolete/`. Reference examples in `obsolete/examples/`.

---

### 🐙 GitHub + Colab Usage

Clone repo:

```bash
git clone https://github.com/YourUsername/meme_rag.git
cd meme_rag
```

Install requirements:

```bash
pip install -r requirements.txt
```

Run:

```bash
python memerag_gradio_ui.py 
```

*or use*

```bash
python memerag_v2_2pro.py
```

*All modular imports will work automatically.*

---

### 👑 Credits

Created and managed by **Parnal Sinha**.

# MemeRAG Final Submission

Due to persistent GitHub push errors, file size limits, and LFS upload issues, the full MemeRAG project (including large assets and all code) has been uploaded to Google Drive instead.

**Google Drive Link:** https://drive.google.com/drive/folders/1lMfCqp1raiX_8GPa0onhL8R56cdPgLX6?usp=sharing

GitHub was unable to handle the project structure and size despite multiple attempts using both LFS and standard pushes.

Please refer to the provided Google Drive for the complete project files.

If further access or clarification is needed, please contact me directly.

Thank you for understanding.


