import argparse
from lxml import etree
from os import listdir, path
from collections import defaultdict
import re
from itertools import groupby

from preprocess import load_file_to_tree

parser = argparse.ArgumentParser()
parser.add_argument('--rawfolder', default='data/html/files')
parser.add_argument('--outputfolder', default='data/html/merged')
args = parser.parse_args()

PAGENAME_NUMBER_PATTERN = re.compile("(.*)-([0-9]+).html")

if __name__ == '__main__':

    filenames = defaultdict(list)

    def get_filename(filename):
        page_match = PAGENAME_NUMBER_PATTERN.search(filename)
        return page_match.group(1)

    def get_page_number(filename):
        page_match = PAGENAME_NUMBER_PATTERN.search(filename)
        return page_match.group(2)

    for key, group in groupby(sorted(listdir(args.rawfolder)), key=get_filename):

        html = etree.Element('html')
        root = etree.SubElement(html, 'body')

        for file in group:
            page = etree.SubElement(root, 'div', page=get_page_number(file))
            tree = load_file_to_tree(path.join(args.rawfolder, file))

            for element in tree[1]:
                page.append(element)

        with open(path.join(args.outputfolder, key.replace(' ', '_'))+'.html', 'wb') as f:
            f.write(etree.tostring(root, pretty_print=True))
