"""
Translation module for Alien LLM project
Handles offline English-to-Chinese translation
"""

import os
import logging
from transformers import pipeline, MarianTokenizer, MarianMTModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translator = None
        self.model_loaded = False
        self.load_translation_model()
    
    def load_translation_model(self):
        """Load the English-to-Chinese translation model"""
        try:
            # Using Helsinki-NLP's English-to-Chinese model
            model_name = "Helsinki-NLP/opus-mt-en-zh"
            
            logger.info(f"Loading translation model: {model_name}")
            
            # Set cache directory to avoid any network issues
            cache_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'translation')
            os.makedirs(cache_dir, exist_ok=True)
            
            # Initialize tokenizer and model specifically for Marian models
            self.tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=cache_dir, local_files_only=False)
            self.model = MarianMTModel.from_pretrained(model_name, cache_dir=cache_dir, local_files_only=False)
            
            # For Marian models, we'll use the model directly instead of pipeline
            self.model_loaded = True
            logger.info("Translation model loaded successfully")
            
            self.model_loaded = True
            logger.info("Translation model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load translation model: {e}")
            # Try to load from cache only in case of network issues
            try:
                cache_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'translation')
                self.tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=cache_dir, local_files_only=True)
                self.model = MarianMTModel.from_pretrained(model_name, cache_dir=cache_dir, local_files_only=True)
                
                self.translator = pipeline(
                    "translation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if "mps" in os.popen("sysctl machdep.cpu.features").read() else -1
                )
                
                self.model_loaded = True
                logger.info("Translation model loaded from cache successfully")
            except Exception as e2:
                logger.error(f"Failed to load translation model from cache: {e2}")
                self.model_loaded = False
    
    def translate_to_chinese(self, english_text: str) -> str:
        """
        Translates English text to Chinese using the loaded model.
        
        Args:
            english_text: Input English text to translate
            
        Returns:
            Chinese translation of the input text, or original text with error if translation fails
        """
        if not self.model_loaded:
            logger.error("Translation model not loaded, returning original text")
            return f"[Translation not available]\n{english_text}"
        
        try:
            # Handle empty input
            if not english_text or not english_text.strip():
                return ""
            
            # Tokenize the input text
            inputs = self.tokenizer(english_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Generate translation
            translated = self.model.generate(**inputs, max_length=512, num_beams=5, early_stopping=True)
            
            # Decode the translation
            translated_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
            
            return translated_text
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return f"[Translation error: {str(e)}]\n{english_text}"

# Global instance of the translation service
translation_service = TranslationService()

def translate_to_chinese(english_text: str) -> str:
    """
    Public function to translate English text to Chinese.
    This is the main interface that server.py will call.
    
    Args:
        english_text: Input English text to translate
        
    Returns:
        Chinese translation of the input text
    """
    return translation_service.translate_to_chinese(english_text)

# Test function for debugging
if __name__ == "__main__":
    test_text = "The K2-18b civilization perceives the signals as rhythmic pulsations in their liquid environment."
    result = translate_to_chinese(test_text)
    print(f"English: {test_text}")
    print(f"Chinese: {result}")