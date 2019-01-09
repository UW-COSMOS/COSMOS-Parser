from fonduer import Meta
from fonduer.parser.preprocessors import HTMLDocPreprocessor
from fonduer.parser import Parser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-html_location', default='out/html/')
parser.add_argument('-database', default='postgres://postgres:password@localhost:5432/cosmos')
args = parser.parse_args()

CONN_STRING = args.database
DOCS_PATH = args.html_location

if __name__ == '__main__':
    session = Meta.init(CONN_STRING).Session()
    doc_preprocessor = HTMLDocPreprocessor(DOCS_PATH)
    corpus_parser = Parser(session, structural=True, lingual=True)
    corpus_parser.apply(doc_preprocessor)
