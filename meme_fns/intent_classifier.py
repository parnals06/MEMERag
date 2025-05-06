"""
Enhanced Intent Classifier for MemeRAG v2.2 Pro
Maps user messages to appropriate context tags used in meme_examples
"""
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("memerag_intent.log"), logging.StreamHandler()]
)
logger = logging.getLogger("intent_classifier")

# Maps intent categories to relevant keywords that might appear in user messages
INTENT_KEYWORDS = {
    # Emotional reactions
    "angry": ["angry", "mad", "furious", "rage", "pissed", "annoyed", "irritated", "frustrated"],
    "sad": ["sad", "depressed", "down", "disappointed", "upset", "crying", "lonely"],
    "happy": ["happy", "excited", "joyful", "glad", "cheerful", "delighted", "pleased"],
    "shocked": ["shocked", "surprised", "stunned", "amazed", "astonished", "wow", "wtf", "omg"],
    "confused": ["confused", "puzzled", "unsure", "uncertain", "don't understand", "unclear", "what?"],
    
    # Interactions
    "agreement": ["yes", "agree", "correct", "right", "absolutely", "exactly", "👍", "sure", "ok"],
    "rejection": ["no", "disagree", "wrong", "incorrect", "nope", "not true", "nah", "👎"],
    "questioning": ["why", "how", "when", "what if", "really?", "curious", "wonder"],
    "skeptical": ["doubt", "skeptical", "not sure", "questionable", "suspicious", "hmm"],
    "mockery": ["lol", "haha", "noob", "funny", "joke", "ridiculous", "silly", "lmao"],
    
    # Actions & attitudes
    "victory": ["win", "success", "achievement", "accomplished", "nailed it", "victory", "done"],
    "dismissive": ["whatever", "don't care", "meh", "boring", "irrelevant", "stupid"],
    "challenging": ["try me", "prove it", "challenge", "bet", "dare", "come on", "fight me"],
    "revelation": ["realized", "suddenly", "discovery", "found out", "epiphany", "aha moment"],
    "thoughtful": ["thinking", "considering", "reflecting", "pondering", "contemplating"],
    
    # Decision contexts
    "choice": ["choose", "decision", "options", "dilemma", "either", "or", "alternatives"],
    "comparison": ["better", "worse", "versus", "compared to", "difference", "contrast"],
    "contradiction": ["but", "however", "despite", "although", "contrary", "opposite"],
    "sarcastic": ["sure thing", "yeah right", "obviously", "of course", "how nice"],
    "exasperation": ["seriously?", "again?", "enough", "can't take it", "exhausted"],
    
    # Situations
    "awkward": ["awkward", "uncomfortable", "embarrassed", "cringe", "yikes"],
    "coping": ["dealing with", "handling", "coping", "managing", "surviving", "getting by"],
    "reality": ["truth", "fact", "reality", "actually", "in fact", "really"],
    "confident": ["confident", "certain", "sure", "positive", "definitely", "absolutely"],
    "proud": ["proud", "achievement", "accomplished", "did it", "made it", "success"],
    
    # Additional categories
    "clever": ["smart", "clever", "brilliant", "genius", "intelligent", "big brain"],
    "dramatic": ["dramatic", "intense", "serious", "dire", "critical", "extreme"],
    "supportive": ["support", "help", "encourage", "there for you", "backing you"],
    "strategy": ["plan", "strategy", "approach", "organize", "method", "system"],
    "reaction": ["react", "response", "reply", "answer", "comeback"]
}

# Add fallback tags for when no match is found
# These should be common, versatile tags that work well with many situations
FALLBACK_TAGS = [
    "reaction", "thoughtful", "confused", "questioning", "reality", "sarcastic", "mockery"
]

def classify_intent(message, all_possible_tags=None):
    """
    Analyzes a user message and returns the most appropriate context tag.
    
    Args:
        message (str): The user message to analyze
        all_possible_tags (list): Optional list of valid tags to constrain results
    
    Returns:
        str: The most likely intent/context tag
    """
    if not message or not isinstance(message, str):
        logger.warning(f"Invalid message received: {message}")
        return random.choice(FALLBACK_TAGS)
    
    # Normalize message text
    text = message.lower()
    
    # Track matching tags and their match counts
    matches = {}
    
    # Check each tag's keywords against the message
    for tag, keywords in INTENT_KEYWORDS.items():
        # Skip tags not in allowed list (if provided)
        if all_possible_tags and tag not in all_possible_tags:
            continue
            
        # Count how many keywords match
        match_count = sum(1 for kw in keywords if kw in text)
        if match_count > 0:
            matches[tag] = match_count
    
    # If we found matches, return the tag with the most keyword hits
    if matches:
        # Sort by match count (descending) and return the top tag
        best_match = max(matches.items(), key=lambda x: x[1])[0]
        logger.info(f"Message '{message[:30]}...' classified as '{best_match}' with {matches[best_match]} matches")
        return best_match
    
    # No matches found, use a fallback
    fallbacks = [tag for tag in FALLBACK_TAGS if not all_possible_tags or tag in all_possible_tags]
    if not fallbacks and all_possible_tags:
        # If no valid fallbacks remain, pick any from the allowed list
        fallbacks = all_possible_tags
    
    fallback = random.choice(fallbacks) if fallbacks else "questioning"
    logger.info(f"No matches found for message '{message[:30]}...', using fallback: '{fallback}'")
    return fallback

def get_all_intent_tags():
    """Returns a list of all available intent tags"""
    return list(INTENT_KEYWORDS.keys())

# Example usage 
if __name__ == "__main__":
    test_messages = [
        "I'm so angry about this!",
        "This made me laugh so hard",
        "I'm not sure what to do next",
        "That's completely wrong",
        "I totally agree with you",
        "Wait, what just happened?",
        "Let me think about this...",
        "This is the best day ever!",
        "Choose between option A and B",
        "Random message with no clear intent"
    ]
    
    print("Intent classification examples:")
    for msg in test_messages:
        intent = classify_intent(msg)
        print(f"Message: {msg}\nClassified as: {intent}\n")
