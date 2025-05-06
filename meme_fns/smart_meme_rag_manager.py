"""
Enhanced SmartMemeRAGManager for MemeRAG v2.2 Pro
Core retrieval logic for meme selection based on user queries
"""
import logging
import random
import numpy as np
import csv
from datetime import datetime
from meme_fns.intent_classifier import classify_intent, get_all_intent_tags

# Mapping from high-level intents to meme tags that actually exist
INTENT_TO_MEME_TAG = {
    "mockery": "sarcastic",
    "motivational": "confident",
    "fail": "sad",
    "confusion": "confused",
    "agreement": "agreement",
    "rejection": "rejection",
    "victory": "victory",
    "proud": "proud",
    "surprise": "shock",
    "funny": "funny",
    "clever": "smart",
    "thinking": "thoughtful",
    "support": "approving"
    # Add more mappings as needed
}


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("memerag_manager.log"), logging.StreamHandler()]
)
logger = logging.getLogger("meme_rag_manager")

class SmartMemeRAGManager:
    """
    Enhanced RAG Manager that combines:
    1. Semantic similarity matching
    2. Intent classification for context-aware retrieval
    3. Fallback mechanisms for when no perfect match exists
    4. Feedback integration (optional)
    """
    def __init__(self, embedder, retriever, selector):
        self.embedder = embedder
        self.retriever = retriever
        self.selector = selector
        self.fallback_mode = "hybrid"  # Options: "strict", "hybrid", "relaxed"
        self.feedback_history = {}     # For tracking user feedback
        self.valid_tags = self._extract_valid_tags()
        
        # Log initialization status
        num_valid_tags = len(self.valid_tags) if self.valid_tags else 0
        logger.info(f"SmartMemeRAGManager initialized with {num_valid_tags} valid tags")
    
    def _extract_valid_tags(self):
        """
        Extract all unique context tags from the indexed memes
        """
        all_tags = set()
        if hasattr(self.retriever, 'memes_by_id'):
            for meme_id, meme in self.retriever.memes_by_id.items():
                if 'context_tags' in meme and isinstance(meme['context_tags'], list):
                    all_tags.update(meme['context_tags'])
        
        # Convert to list for easy use
        return list(all_tags) if all_tags else None
    
    def run(self, user_query, top_k=10, debug=False):
        """
        Process a user query and select the most appropriate meme.

        Steps:
            1. Classify the user query to detect the high-level intent.
            2. Map that intent to a meme context tag (using INTENT_TO_MEME_TAG).
            3. Embed the query for semantic similarity search.
            4. Retrieve candidate memes using the retriever.
            5. Filter candidates by context tags (if possible).
            6. If no exact matches, apply fallback logic.
            7. Select the final meme using the MemeSelector.
            8. Return the result (and debug info if requested).

        Args:
            user_query (str): The user's input message.
            top_k (int): Number of candidates to retrieve.
            debug (bool): If True, return detailed debug info.

        Returns:
            str: Filename of the selected meme.
            dict: Debug info (if debug=True).
        """

        # -------------------------------------
        # 1. Classify user query → get intent
        # -------------------------------------
        intent_tag = classify_intent(user_query, self.valid_tags)

        # Map the intent to a known meme context tag (fallback to the intent itself if no mapping)
        context_tag = INTENT_TO_MEME_TAG.get(intent_tag, intent_tag)

        # Logging what we detected
        log_msg = f"Intent tag '{intent_tag}' mapped to context tag '{context_tag}' for query '{user_query[:30]}...'"
        logger.info(log_msg)

        # If debugging, keep track of the chosen context tag
        debug_info = {"query": user_query} if debug else None
        if debug:
            debug_info["context_tag"] = context_tag

        # -------------------------------------
        # 2. Embed the user query
        # -------------------------------------
        query_vector = self.embedder.embed(user_query)

        # -------------------------------------
        # 3. Retrieve candidates using semantic similarity
        # -------------------------------------
        initial_candidates = self.retriever.retrieve(query_vector, top_k=top_k)
        if debug:
            debug_info["initial_candidates_count"] = len(initial_candidates)

        # -------------------------------------
        # 4. Filter by context tag
        # -------------------------------------
        if context_tag and initial_candidates:
            filtered_candidates = []
            for meme in initial_candidates:
                meme_tags = meme.get("context_tags", [])
                if context_tag in meme_tags:
                    filtered_candidates.append(meme)

            logger.info(
                f"Filtered {len(initial_candidates)} candidates to {len(filtered_candidates)} matches for '{context_tag}'"
            )

            # -------------------------------------
            # 5. Apply fallback logic if no matches
            # -------------------------------------
            if filtered_candidates:
                final_candidates = filtered_candidates
            elif self.fallback_mode == "strict":
                logger.warning(
                    f"No memes match context '{context_tag}', returning None in strict mode"
                )
                return None if not debug else (None, debug_info)
            elif self.fallback_mode == "hybrid":
                logger.info(
                    f"No exact matches for '{context_tag}', trying broader tag matching"
                )
                broader_matches = []
                all_intent_tags = get_all_intent_tags()

                for tag in all_intent_tags:
                    if tag != context_tag:
                        for meme in initial_candidates:
                            meme_tags = meme.get("context_tags", [])
                            if tag in meme_tags:
                                broader_matches.append(meme)

                if broader_matches:
                    final_candidates = broader_matches[:top_k]
                    logger.info(
                        f"Found {len(broader_matches)} broader tag matches"
                    )
                else:
                    final_candidates = initial_candidates
                    logger.info(
                        "No broader tag matches, falling back to semantic similarity only"
                    )
            else:
                # fallback_mode == "relaxed"
                final_candidates = initial_candidates
                logger.info(
                    f"No matches for '{context_tag}', using semantic similarity only"
                )
        else:
            # If no context_tag or no candidates, just use semantic similarity
            final_candidates = initial_candidates

        # -------------------------------------
        # 6. Debugging: capture final candidate info
        # -------------------------------------
        if debug:
            debug_info["final_candidates_count"] = len(
                final_candidates) if final_candidates else 0
            if final_candidates:
                debug_info["top_candidate"] = {
                    "caption": final_candidates[0].get("caption", ""),
                    "image": final_candidates[0].get("image", ""),
                    "context_tags": final_candidates[0].get("context_tags", [])
                }

        # -------------------------------------
        # 7. Select meme from final candidates
        # -------------------------------------
        if not final_candidates:
            logger.warning("No suitable memes found for query")
            return None if not debug else (None, debug_info)

        pick = self.selector.generate(user_query, final_candidates)
        logger.info(f"Selected meme: {pick}")
        self.log_selection(user_query, intent_tag, pick)

        return pick if not debug else (pick, debug_info)
    
    def record_feedback(self, query, meme_filename, liked=True):
        """
        Record user feedback for a meme selection to improve future matches
        
        Args:
            query (str): The original user query
            meme_filename (str): The filename of the meme shown
            liked (bool): Whether the user liked the meme
        """
        self.feedback_history[meme_filename] = self.feedback_history.get(meme_filename, [])
        self.feedback_history[meme_filename].append({
            "query": query,
            "liked": liked,
            "timestamp": None  # Replace with actual timestamp if needed
        })
        logger.info(f"Recorded feedback for {meme_filename}: {'👍' if liked else '👎'}")

    def log_selection(self, query, intent_tag, meme_filename):
        """
        Save the user query, detected intent, and selected meme to a CSV log.
        """
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query, intent_tag, meme_filename]
        file_path = "log_history.csv"
        try:
            file_exists = False
            try:
                with open(file_path, "r", newline='') as f:
                    file_exists = True
            except FileNotFoundError:
                pass

            with open(file_path, "a", newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(["Timestamp", "User Message", "Intent", "Meme Selected"])
                writer.writerow(row)
        except Exception as e:
            logger.warning(f"Failed to write log to {file_path}: {e}")
        
    def set_fallback_mode(self, mode):
        """
        Set the fallback strategy when no exact context tag matches are found
        
        Args:
            mode (str): One of "strict", "hybrid", or "relaxed"
                - strict: Only return context-matched memes or None
                - hybrid: Try other tags, then fall back to similarity
                - relaxed: Use pure semantic similarity if no tag matches
        """
        valid_modes = ["strict", "hybrid", "relaxed"]
        if mode in valid_modes:
            self.fallback_mode = mode
            logger.info(f"Fallback mode set to '{mode}'")
        else:
            logger.warning(f"Invalid fallback mode '{mode}', using 'hybrid'")
            self.fallback_mode = "hybrid"
            
class MemeSelector:
    """
    Selects the best meme from retrieved candidates.
    Falls back to random meme from index if no candidates.
    Supports negative weighting to avoid repeat selections.
    """
    def __init__(self, strategy="top", retriever=None):
        self.strategy = strategy  # Options: "top", "weighted", "random"
        self.retriever = retriever  # Pass the retriever to allow full fallback
        self.recent_picks = []      # Tracks recently used memes for negative weighting
        self.max_recent = 10        # Max recent picks to track

    def generate(self, query, candidates):
        """Select a meme from the candidates based on strategy, with graceful fallback."""
        # 1️⃣ If we have valid candidates:
        if candidates:
            pick = self._select_from_candidates(query, candidates)
            if pick:
                self._update_recent(pick)
                return pick

        # 2️⃣ If no valid candidates, fallback to random meme from the whole retriever
        logger.warning("No valid candidates — falling back to random meme from full index.")
        return self._select_random_fallback()

    def _select_from_candidates(self, query, candidates):
        """Apply the primary strategy to select from candidates."""
        if self.strategy == "random":
            # Totally random selection
            return random.choice(candidates)['image']

        elif self.strategy == "weighted":
            # Weight by position in list (first = most relevant)
            weights = []
            for i, meme in enumerate(candidates):
                # Negative weighting: if recently picked, reduce chance significantly
                if meme['image'] in self.recent_picks:
                    weight = 0.05 / (i + 1)
                else:
                    weight = 1 / (i + 1)
                weights.append(weight)

            # Normalize weights
            total = sum(weights)
            if total > 0:
                normalized = [w / total for w in weights]
                selected = np.random.choice(len(candidates), p=normalized)
                return candidates[selected]['image']
            else:
                return candidates[0]['image']  # Fallback to top

        else:
            # Default: top candidate
            return candidates[0]['image']

    def _select_random_fallback(self):
        """Pick a random meme from the full index if no candidates exist."""
        if self.retriever and hasattr(self.retriever, 'memes_by_id'):
            memes = list(self.retriever.memes_by_id.values())
            if memes:
                fallback_meme = random.choice(memes)['image']
                self._update_recent(fallback_meme)
                return fallback_meme
        logger.error("No memes found in retriever for fallback!")
        return None

    def _update_recent(self, meme_filename):
        """Track recent picks to apply negative weighting."""
        self.recent_picks.append(meme_filename)
        if len(self.recent_picks) > self.max_recent:
            self.recent_picks.pop(0)

