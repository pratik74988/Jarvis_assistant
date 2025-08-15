import spacy

nlp = spacy.load("en_core_web_sm")

MAX_TURNS = 6
history = []

def add_to_history (role, content):
    history.append({"role": role, "content": content})
    if len(history)>MAX_TURNS*2:
        history.pop(0)
def get_context ():
    return history[-MAX_TURNS*2:]

def extract_important_parts(text, max_words = 20):
    doc = nlp(text)
    keywords = set()

    for ent in doc.ents:
        keywords.add(ent.text)
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN", "VERB"):
            keywords.add(token.text)
    
    short_text = " ".join(list(keywords)[:max_words])
    return short_text.strip()


