"""
MemeRAG v2.2 Pro - Integration Example
Shows how to integrate the new components into your existing codebase
"""
import os
import time
import random
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
from IPython.display import HTML, Image, display

# Import the enhanced components
# Assuming you've placed them in the meme_fns directory
from meme_fns.intent_classifier import classify_intent, get_all_intent_tags
from meme_fns.smart_meme_rag_manager import SmartMemeRAGManager, MemeSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("memerag.log"), logging.StreamHandler()]
)
logger = logging.getLogger("memerag_example")

# === 1. Core Components from Original Code (Mostly Unchanged) ===
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    def embed(self, text: str) -> np.ndarray:
        return self.model.encode([text])[0]

class Retriever:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.memes_by_id = {}
        self.next_id = 0

    def add_documents(self, memes: list, embedder: Embedder):
        vecs = []
        ids_to_add = []
        for m in memes:
            vecs.append(embedder.embed(m['caption']))
            current_id = self.next_id
            self.memes_by_id[current_id] = m
            ids_to_add.append(current_id)
            self.next_id += 1

        if vecs:
            self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.index.d))
            self.index.add_with_ids(np.vstack(vecs), np.array(ids_to_add, dtype='int64'))
            logger.info(f"Indexed {len(vecs)} memes")
        else:
            logger.warning("No vectors to add to index")

    def retrieve(self, query_vec: np.ndarray, top_k=10) -> list:
        if self.index.ntotal == 0:
            logger.warning("Index is empty. Cannot retrieve")
            return []

        search_k = min(top_k * 3, self.index.ntotal)
        D, I = self.index.search(np.array([query_vec]), search_k)
        
        results = [self.memes_by_id[idx] for idx in I[0] if idx != -1]
        return results

# === 2. Upgraded MemeAugmentedChatbot ===
class MemeAugmentedChatbot:
    def __init__(self, rag_mgr, openai_key, meme_folder):
        self.rag = rag_mgr
        self.meme_folder = meme_folder
        self.client = OpenAI(api_key=openai_key)
        self.chat_log = []
        self.cooldown = 0
        self.personality = "You are a friendly and witty meme expert who uses humor to lighten conversations."
        
        logger.info("MemeAugmentedChatbot initialized")

    def ask_openai(self, msg):
        """Get response from OpenAI"""
        try:
            logger.info(f"Calling OpenAI API for message: {msg[:30]}...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Adjust based on your preference
                messages=[
                    {"role": "system", "content": self.personality},
                    {"role": "user", "content": msg}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            full_reply = response.choices[0].message.content
            return full_reply
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Sorry, I couldn't generate a response right now."

    def should_meme(self, msg):
        """Determine if we should show a meme for this message"""
        if self.cooldown > 0:
            self.cooldown -= 1
            return False
            
        # Keywords that often indicate emotional content
        emotional_keywords = ["sad", "happy", "angry", "confused", "tired",
                             "stressed", "hype", "excited", "winning", "losing"]
                             
        if any(word in msg.lower() for word in emotional_keywords):
            self.cooldown = 1
            return True
            
        # 60% chance of showing a meme otherwise
        if random.random() < 0.6:
            self.cooldown = 1
            return True
            
        return False

    def show_meme(self, fname):
        """Display a meme"""
        src = os.path.join(self.meme_folder, fname)
        if os.path.exists(src):
            display(Image(filename=src))
        else:
            logger.warning(f"Meme image not found: {src}")
            print(f"⚠️ Meme image not found: {fname}")

    def chat(self, user_msg):
        """Process a user message and respond with text and possibly a meme"""
        # Handle personality switch commands
        if user_msg.startswith("!set personality "):
            new_persona = user_msg.split("!set personality ")[1].strip()
            self.set_personality(new_persona)
            return

        # Display input
        print(f"\n🧠 You said: {user_msg}")
        
        # Get text response from OpenAI
        reply = self.ask_openai(user_msg)
        print(f"\n🤖 {reply}")
        
        # Determine if a meme should be shown
        meme_filename = None
        if self.should_meme(user_msg):
            # Use the enhanced SmartMemeRAGManager
            meme_filename = self.rag.run(user_msg)
            
            if meme_filename:
                print("\n🎭 Meme Reaction:")
                # Allow time for Colab to prepare visual
                time.sleep(0.4)
                self.show_meme(meme_filename)
            else:
                print("\n⚠️ No suitable meme found for this input.")
        else:
            print("\n😎 Chill mode — no meme this time.")
        
        # Log the interaction
        self.chat_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_msg,
            "bot_response": reply,
            "meme": meme_filename if meme_filename else "None"
        })

    def set_personality(self, persona):
        """Change the chatbot's personality"""
        personalities = {
            "default": "You are a friendly and witty meme expert who uses humor to lighten conversations.",
            "sith_lord": "You are a Sith Lord meme master who uses dark humor and ruthless memes to guide the weak.",
            "hype_beast": "You are an over-the-top hype man who uses memes to boost confidence to absurd levels.",
            "sadge_coach": "You are a kind, supportive meme expert who gently lifts users' spirits when they are sad.",
            "evil_genius": "You are an evil mastermind who plots memes to dominate conversations through cunning wit."
        }
        
        if persona in personalities:
            self.personality = personalities[persona]
            print(f"🎭 Personality switched to {persona}!")
        else:
            print(f"⚠️ Unknown personality '{persona}'. Available: {list(personalities.keys())}")

    def save_chatlog(self, filename="chatlog.csv"):
        """Save the chat history to a CSV file"""
        df = pd.DataFrame(self.chat_log)
        df.to_csv(filename, index=False)
        print(f"✅ Chat log saved as {filename}")
        return filename

# === 3. Main Chat Loop with Improved Flow ===
def chat_loop(bot):
    """Run an improved chat loop in Colab"""
    print("🚀 MemeRAG v2.2 Pro - Enhanced Chat Interface 🚀")
    print("Type 'quit' to exit, '!set personality [type]' to change personality")
    print("Available personalities: default, sith_lord, hype_beast, sadge_coach, evil_genius")
    
    while True:
        user_msg = input("\n💬 Type your message: ")
        
        if user_msg.lower() in ['quit', 'exit', 'bye']:
            break
            
        if user_msg.lower() == 'save':
            bot.save_chatlog()
            continue
            
        # Process the message
        bot.chat(user_msg)
    
    # Save chat log on exit
    bot.save_chatlog("memerag_session.csv")
    print("👋 Chat session ended and saved!")

# === 4. Main execution ===
def main():
    """Main entry point with improved organization"""
    # Path configuration (adjust to your environment)
    DRIVE_PATH = '/content/drive/MyDrive/meme_rag'
    MEME_FOLDER = os.path.join(DRIVE_PATH, 'memes')
    CONFIG_PATH = os.path.join(DRIVE_PATH, 'meme_config', 'openai_key.txt')
    
    # Load OpenAI key
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            openai_key = f.read().strip()
    else:
        # Fallback - ask for key via console
        openai_key = input("Enter your OpenAI API key: ")
        # Save for future use
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            f.write(openai_key)
    
    # Here you should use your actual meme_examples list from your code
    # For the purpose of this example, we're assuming it exists
    # from meme_fns.memes_list import meme_examples
    
    # For this example, assume meme_examples is defined elsewhere in your code
    
    # Initialize the components
    emb = Embedder()
    ret = Retriever()
    sel = MemeSelector(strategy="weighted")  # Try different strategies
    
    # Use the improved SmartMemeRAGManager
    rag = SmartMemeRAGManager(emb, ret, sel)
    
    # Configure the fallback mode (optional)
    rag.set_fallback_mode("hybrid")  # Options: strict, hybrid, relaxed
    
    # Index your memes
    ret.add_documents(meme_examples, emb)
    
    # Create the chatbot
    bot = MemeAugmentedChatbot(rag, openai_key, MEME_FOLDER)
    
    # Run the chat loop
    chat_loop(bot)

if __name__ == "__main__":
    main()
