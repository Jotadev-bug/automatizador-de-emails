import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK resources are available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def clean_html(self, raw_html):
        """Strip HTML tags using BeautifulSoup."""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text()
        
    def process(self, text):
        """Standardize and tokenize email text for NLP."""
        if not isinstance(text, str):
            return ""
        
        # 1. Strip HTML
        text = self.clean_html(text)
        
        # 2. Lowercase
        text = text.lower()
        
        # 3. Remove punctuation and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # 4. Tokenization (by whitespace)
        tokens = text.split()
        
        # 5. Stop-word removal and Lemmatization
        cleaned_tokens = [
            self.lemmatizer.lemmatize(word) 
            for word in tokens 
            if word not in self.stop_words
        ]
        
        return " ".join(cleaned_tokens)
