from lxml import html, etree
import re
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', default='data/html/files/S1470160X05000063.pdf-0004.html')
parser.add_argument('--output_words', default='out/words/S1470160X05000063.pdf-0004.html.json')
parser.add_argument('--output_html', default='out/html/S1470160X05000063.pdf-0004.html')
parser.add_argument('--strip_tags', nargs='+', default=['strong', 'em'])
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_WORD = args.output_words
OUTPUT_HTML = args.output_html
STRIP_TAGS = args.strip_tags

BBOX_COORDINATES_PATTERN = re.compile("bbox\s(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+)")
DATA_COORDINATES_PATTERN = re.compile("(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+).")
PAGE_NUMBER_PATTERN = re.compile(".-([0-9]+).html")


def coordinate(title, org_x=0, org_y=0):
    match = BBOX_COORDINATES_PATTERN.search(title)
    page_match = PAGE_NUMBER_PATTERN.search(INPUT_FILE)
    return {
        'xmin': int(match.group(1)) + org_x,
        'ymin': int(match.group(2)) + org_y,
        'xmax': int(match.group(3)) + org_x,
        'ymax': int(match.group(4)) + org_y,
        'page_num': int(page_match.group(1))
    }


def get_data_coordinate_pattern(data_coordinate_str):
    match = DATA_COORDINATES_PATTERN.search(data_coordinate_str)
    return int(match.group(1)), int(match.group(2))


def load_file_to_tree(path):
    with open(path, 'r') as in_f:
        loaded = html.fromstring(in_f.read())
    return loaded


def get_ocr_segments(root):
    for node in root.xpath("//body"):
        yield node


def get_all_words_with_coordinates(root):
    for body in get_ocr_segments(root):
        for child in body:
            meta_node = child.xpath(".//*[@id='hocr']")[0]
            assert len(child.xpath(".//*[@id='hocr']")) == 1
            base_x, base_y = get_data_coordinate_pattern(meta_node.attrib['data-coordinates'])
            for word in child.xpath(".//*[@class='ocrx_word']"):
                if word.text.strip():
                    # print(word.text)
                    yield {
                        'text': word.text,
                        'word_bbox': coordinate(word.attrib['title'], base_x, base_y),
                        'line_bbox': coordinate(word.getparent().attrib['title'], base_x, base_y),
                        'area_bbox': coordinate(word.getparent().getparent().attrib['title'], base_x, base_y),
                    }


def remove_ocr_and_split_paragraph(root):
    for node in get_ocr_segments(root):
        for area in node:
            for child in area.xpath(".//*"):
                if 'id' not in child.attrib or child.attrib['id'] != 'rawtext':
                    child.getparent().remove(child)
                elif child.text:
                    for paragraph in re.split('\n{2,}', child.text):
                        if len(paragraph) > 0:
                            etree.SubElement(child, "p").text = paragraph
                        child.text = ''


if __name__ == '__main__':
    tree = load_file_to_tree(INPUT_FILE)
    etree.strip_tags(tree, *STRIP_TAGS)
    with open(OUTPUT_WORD, 'w') as out_word:
        json.dump([*get_all_words_with_coordinates(tree)], out_word, indent=4)
    remove_ocr_and_split_paragraph(tree)
    with open(OUTPUT_HTML, 'wb') as out_html:
        out_html.write(etree.tostring(tree, pretty_print=True))

