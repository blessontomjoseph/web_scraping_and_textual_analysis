import re
import os
import requests
from collections import Counter

import spacy
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.autonotebook import tqdm


def clean(texts):
    """ input: texts returned from the website using requests
        removes stop words
        returns text as a string"""

    text = list(texts.split(" "))

    # removing sto words
    stop_words = "../StopWords"
    items = os.listdir(stop_words)

    for file in items:
        name = os.path.join(stop_words, file)
        try:
            with open(name) as f:
                words = set(map(str.lower, f.read().split('\n')))
        except:
            with open(name, 'r', encoding='latin-1') as f:
                words = set(map(lambda x: x.split('|')[
                            0].lower(), f.read().split("\n")))

            text = [word for word in text if word.lower() not in words]
    text = " ".join(text)
    return text


def derived_variables(doc):
    """input:doc object which is a container of tokenized text
        output:positive_scorem,negertive_score,polarity_score,subjectivity_score"""

    with open("../MasterDictionary/positive-words.txt", "rb") as f:
        pos_dict = list(map(str.lower, str(f.read()).split("\\n")))

    with open("../MasterDictionary/negative-words.txt", "rb") as f:
        neg_dict = list(map(str.lower, str(f.read()).split("\\n")))

    positive_score = len([token for token in doc if token.text in pos_dict])
    negetive_score = len([token for token in doc if token.text in neg_dict])
    polarity_score = (positive_score-negetive_score)/((positive_score+negetive_score)+1e-6)
    subjectivity_score = (positive_score+negetive_score)/(len(doc)+1e-6)
    return positive_score, negetive_score, polarity_score, subjectivity_score


def personal_pronouns(doc):
    """input:tokenized_texts as doc
        output: count of personal_pronouns in the doc"""

    personal_pronouns = ["i", "we", "my", "ours", "us"]
    count = 0
    for token in doc.ents:
        if token.label != 'GPE' and token.text.lower() in personal_pronouns:
            count += 1
    return count


def alphanumfilter(text):
    """input: single word as text
       output:word after removing non alpha numerica charectors
       this is a helper function for filtering out words that should not be considerd for calculations(expressions with only special chars)
    """
    out = []
    for i in text:
        if i.isalnum():
            out.append(i)
    return ''.join(out)


def readability(text):
    """
    input: cleaned raw text

    outputs:
    1.Average Number of Words Per Sentence or Average Sentence Length 
    2.Complex Word Count
    3.complex word percent
    4.Fog Index
    5.Word Count
    6.syllable count per word
    7.average word length
    """
    sents = re.split(r'[.!?]', text)
    total_words = 0
    complex_word_count = 0
    total_word_length = 0
    syllable_count = 0

    for sent in sents:
        for word in sent.split(' '):
            if word.isalnum():
                total_words += 1
                total_word_length += len(word)
                syllables = sum([Counter(word.lower())[i] for i in [
                                'a', 'e', 'i', 'o', 'u'] if word.lower()[-2:] not in ['es', 'ed']])
                syllable_count += syllables
                if syllables > 2:
                    complex_word_count += 1

            else:
                if len(alphanumfilter(word)) > 0:
                    total_words += 1
                    total_word_length += len(word)
                    syllables = sum([Counter(word.lower())[i] for i in [
                                    'a', 'e', 'i', 'o', 'u'] if word.lower()[-2:] not in ['es', 'ed']])
                    syllable_count += syllables
                    if syllables > 2:
                        complex_word_count += 1

    average_sentence_length = (total_words/len(sents))
    percent_complex = complex_word_count/total_words
    fog_index = 0.4*(average_sentence_length+percent_complex)
    average_word_length = total_word_length/total_words
    syllable_counts_per_word = syllable_count/total_words
    return average_sentence_length, percent_complex, fog_index, average_sentence_length, complex_word_count, total_words, syllable_counts_per_word, average_word_length


def execute(data):
    """input:data(Output Data Structure.xlsx- which contains only urls all other columns empty)
        this iterates thriugh the url takes the web content and calculates the parameters specified, adds it in to the apropriate column and complety fills the input data file
        output: data, with fields completed"""

    nlp = spacy.load("en_core_web_sm")

    for url in tqdm(data['URL']):
        response = requests.get(url)

        if response.status_code == 200:
            extracted = ""
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string
            extracted += title+"\n"
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                extracted += p.text+"\n"
        else:
            print("Failed to load webpage")
            continue

        text = clean(extracted)
        doc = nlp(text)
        positive_score, negetive_score, polarity_score, subjectivity_score = derived_variables(
            doc)
        average_sentence_length, percent_complex, fog_index, average_sentence_length, complex_word_count, total_words, syllable_counts_per_word, average_word_length = readability(
            text)
        pronouns = personal_pronouns(doc)
        values = [positive_score, negetive_score, polarity_score, subjectivity_score, average_sentence_length, percent_complex,
                  fog_index, average_sentence_length, complex_word_count, total_words, syllable_counts_per_word, pronouns, average_word_length]

        for idx, column in enumerate(data.columns[2:]):
            data.loc[data['URL'] == url, column] = values[idx]

    data.to_csv('completed_output_data.csv', header=True, index=False)


if __name__ == "__main__":
    data = pd.read_excel("output_data_structure.xlsx")
    data = data.loc[:, :'AVG WORD LENGTH']
    execute(data)
