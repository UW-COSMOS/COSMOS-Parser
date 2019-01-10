import argparse
from fonduer import Meta
from fonduer.parser.models import Document, Sentence
import json
from itertools import chain
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--words_location', default='out/words/')
parser.add_argument('--database', default='postgres://postgres:password@localhost:5432/cosmos')
parser.add_argument('--ignored_files', nargs='+', default=['S1470160X05000063.pdf-0004.html'])
args = parser.parse_args()

WORDS_LOCATION = args.words_location
DB_CONNECT_STR = args.database
IGNORED_FILES = args.ignored_files

session = Meta.init(DB_CONNECT_STR).Session()


def get_word_bag(html_source):
    with open(WORDS_LOCATION+html_source+'.html.json') as words:
        return json.load(words)


def get_all_documents():
    return session.query(Document).order_by(Document.id)

def get_all_sentence_from_a_doc(doc_id):
    return session.query(Sentence).filter(Sentence.document_id == doc_id).order_by(Sentence.id)

def same(w1, w2):
    return w1.replace('-', '—') == w2.replace('-', '—')


if __name__ == '__main__':

    for doc in get_all_documents()[0:1]:
        if doc.name+'.html' in IGNORED_FILES:
            continue
        word_bag = get_word_bag(doc.name)
        sentences = get_all_sentence_from_a_doc(doc.id)
        db_count = 0
        word_bag_count = 0
        all_words_from_db = list(chain(*[sent.text.split() for sent in sentences[1:]]))

        for sent in sentences[1:]:
            coordinates_record = defaultdict(list)
            tokenized_words = sent.text.split()


            def add_to_coordinate_record_list():
                current_word_from_bag = word_bag[word_bag_count]
                coordinates_record['top'].append(current_word_from_bag['line_bbox']['ymin'])
                coordinates_record['left'].append(current_word_from_bag['word_bbox']['xmin'])
                coordinates_record['bottom'].append(current_word_from_bag['line_bbox']['ymax'])
                coordinates_record['right'].append(current_word_from_bag['word_bbox']['xmax'])
                coordinates_record['page_num'].append(current_word_from_bag['word_bbox']['page_num'])

            for word in tokenized_words:
                add_to_coordinate_record_list()
                if same(word, word_bag[word_bag_count]['text']):
                    db_count += 1
                    word_bag_count += 1
                elif ''.join([word, all_words_from_db[db_count+1]]) == word_bag[word_bag_count]['text']:
                    db_count += 1
                elif ''.join([all_words_from_db[db_count-1], word]) == word_bag[word_bag_count]['text']:
                    db_count += 1
                    word_bag_count += 1
                else:
                    # print(all_words_from_db[db_count-1], word)
                    print(doc.name)
                    assert False

            sent.top = coordinates_record['top']
            sent.left = coordinates_record['left']
            sent.bottom = coordinates_record['bottom']
            sent.right = coordinates_record['right']
            sent.page = coordinates_record['page_num']

            try:
                assert len(sent.text.split()) == len(sent.top) == len(sent.left) == len(sent.right) == len(sent.bottom) == len(sent.page)
            except AssertionError:
                print(len(sent.text.split()), len(sent.top), len(sent.left), len(sent.bottom), len(sent.right), len(sent.page))
    session.commit()
