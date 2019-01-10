from fonduer import Meta
from fonduer.parser.models import Document, Sentence
import json
from itertools import chain


def get_word_bag(html_source):
    with open('out/words/'+html_source+'.html.json') as words:
        return json.load(words)


def same(w1, w2):
    return w1.replace('-', '—') == w2.replace('-', '—')


if __name__ == '__main__':
    ATTRIBUTE = "cosmos"
    conn_string = 'postgres://postgres:password@localhost:5432/' + ATTRIBUTE
    session = Meta.init(conn_string).Session()
    docs = session.query(Document).order_by(Document.id)
    for doc in docs[5:]:

        word_bag = get_word_bag(doc.name)
        sentences = session.query(Sentence).filter(Sentence.document_id == doc.id).order_by(Sentence.id)
        db_count = 0
        word_bag_count = 0
        all_words_from_db = list(chain(*[sent.text.split() for sent in sentences[1:]]))
        count = 0
        # for word in all_words_from_db:
        #     # print(word, word_bag[count]['text'])
        #     # count += 1
        #     print(word)
        for sent in sentences[1:]:
            tokenized_words = sent.text.split()
            for word in tokenized_words:
                if same(word, word_bag[word_bag_count]['text']):
                    # print(word, word_bag[word_bag_count]['text'])
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

    # session.commit()
    # print(count)


