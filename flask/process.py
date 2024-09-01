import sys
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import re

API_KEY = 'LIVDSRZULELA'

def fetch_filtered_gifs(api_key, query, limit=50, pos=None):
    url = f'https://g.tenor.com/v1/search?key={api_key}&q={query}&limit={limit}'
    if pos:
        url += f'&pos={pos}'
    response = requests.get(url)
    data = response.json()
    gifs = data.get('results', [])
    next_pos = data.get('next', None)
    return gifs, next_pos

def fetch_gifs(api_key, query, limit=200):
    gifs = []
    next_pos = None
    for _ in range(limit // 50):
        fetched_gifs, next_pos = fetch_filtered_gifs(api_key, query, limit=50, pos=next_pos)
        gifs.extend(fetched_gifs)
        if not next_pos:
            break
    return gifs

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    text = ' '.join(word for word in text.split() if word not in stopwords)
    return text

def extract_keywords_from_url(url):
    key_part = url.split('/')[-1].split('.')[0]
    return re.sub(r'\W', ' ', key_part).replace('-', ' ')

stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

def process(query):
    gifs = fetch_gifs(API_KEY, query)
    descriptions = [preprocess_text(gif['content_description']) for gif in gifs]
    urls = [gif['media'][0]['gif']['url'] for gif in gifs]
    content_descriptions = [gif['content_description'] for gif in gifs]
    keywords = [extract_keywords_from_url(url) for url in urls]
    combined_texts = [desc + ' ' + keyword for desc, keyword in zip(descriptions, keywords)]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(combined_texts)

    def get_most_similar_gifs(query, top_n=5):
        query_text = preprocess_text(query)
        query_keywords = extract_keywords_from_url(query)
        combined_query = query_text + ' ' + query_keywords
        query_vec = vectorizer.transform([combined_query])
        similarities = cosine_similarity(query_vec, X).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        return [(urls[i], content_descriptions[i], similarities[i]) for i in top_indices]

    similar_gifs = get_most_similar_gifs(query, top_n=5)
    return similar_gifs

if __name__ == "__main__":
    input_data = sys.stdin.read()
    query = json.loads(input_data).get('query', '')
    result = process(query)
    print(json.dumps(result))
