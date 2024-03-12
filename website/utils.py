import spacy
import re
from pypdf import PdfReader
from keras.models import load_model
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(BASE_DIR, 'CNN_LSTM.h5')
# vectorizer_path = os.path.join(BASE_DIR, 'Vectorizer.h5')


# model = load_model(model_path)
# vectorizer = load_model(vectorizer_path)

nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text().lower() + "\n"
    return text 


def extract_contact_details(resume_text):
    doc = nlp(resume_text.lower())

    contact_details = {}

    # Extract email addresses using regex pattern
    email_pattern = r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b'
    email_matches = re.findall(email_pattern, resume_text)
    contact_details['email'] = email_matches

    # Extract phone numbers using regex pattern
    phone_pattern = r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b'
    phone_matches = re.findall(phone_pattern, resume_text)
    contact_details['phone'] = ["".join(match) for match in phone_matches]
    contact_details['phone'] = ["+" + phone_number for phone_number in contact_details['phone']]

    return contact_details


# calculates the score, and returns it
# def extract_skill_with_score(resume_text, job_description):

#     # Preprocess 
#     preprocessed_resume = preprocess(resume_text) 
#     preprocessed_job_description = preprocess(job_description)  
    
    
#     v1 =  vectorizer.transform([preprocessed_resume]).toarray()
#     v2 =  vectorizer.transform([preprocessed_job_description]).toarray()

#     # Feeding and getting score back
#     score = model.predict([v1, v2])   
#     print(score)
#     return round(score, 3)


# Preprocess
def preprocess(text):
    # Tokenize the text into individual words
    tokens = word_tokenize(text)
    
    # Convert all tokens to lowercase
    lowercase_tokens = []
    for token in tokens:
        lowercase_token = token.lower()
        lowercase_tokens.append(lowercase_token)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = []
    for token in lowercase_tokens:
        if token not in stop_words:
            filtered_tokens.append(token)
    
    # Perform lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    for token in filtered_tokens:
        lemmatized_token = lemmatizer.lemmatize(token)
        lemmatized_tokens.append(lemmatized_token)
    
    preprocessed_text = ' '.join(lemmatized_tokens)
    
    return preprocessed_text










# THE END


























































































































































# def extract_skills(job_description):
#     doc = nlp(job_description.lower())

#     noun_chunks = [chunk.text for chunk in doc.noun_chunks]
#     named_entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'SKILL', 'LANGUAGE']]

#     skills = list(set(noun_chunks + named_entities))
    
#     return skills

def extract_skills_with_score(resume_text, job_description):
    # Preprocessing
    resume_text = resume_text.lower()
    job_description = job_description.lower()

    # Extract skills from job description
    job_skills_list = re.findall(r'\b\w+\b', job_description)  
    resume_skill_list = set(re.findall(r'\b\w+\b', resume_text))
    
    total_score = 0
    for skill in resume_skill_list:
        if skill in job_skills_list:
            total_score += 1 
            
    if len(job_skills_list) > 0:
        total_score = total_score/len(job_skills_list) * 100 
    print(total_score)
    return round(total_score,3)
