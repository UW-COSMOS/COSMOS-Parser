from fonduer import Meta
from fonduer.parser.models import Document, Sentence

if __name__ == '__main__':
    ATTRIBUTE = "cosmos"
    conn_string = 'postgres://postgres:password@localhost:5432/' + ATTRIBUTE
    session = Meta.init(conn_string).Session()
    docs = session.query(Document.id).order_by(Document.id)
    count = 0
    for doc in docs[2:3]:
        sentences = session.query(Sentence).filter(Sentence.document_id == doc.id).order_by(Sentence.id)
        for sent in sentences:
            for word in sent.text.split():
                print(word)
                count += 1
    print(count)


