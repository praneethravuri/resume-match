import re
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("text_processing module loaded.")

# Download necessary NLTK data
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    """Lemmatize the input text."""
    tokens = text.split()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    lemmatized = ' '.join(lemmatized_tokens)
    logging.info("Lemmatized text: %s", lemmatized)
    return lemmatized

def preprocess_text(text):
    """Lowercase, remove non-alphanumeric characters, and lemmatize."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    preprocessed = lemmatize_text(text)
    logging.info("Preprocessed text: %s", preprocessed)
    return preprocessed

def compute_matching_score(job_description, resume_text):
    """
    Compute the matching score between job description and resume using TF-IDF cosine similarity.
    Returns a score between 0 and 1.
    """
    try:
        texts = [preprocess_text(job_description), preprocess_text(resume_text)]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
        score = similarity_matrix[0][1]
        logging.info("Computed matching score: %f", score)
        return score
    except Exception as e:
        logging.exception("Error computing matching score")
        return 0.0
