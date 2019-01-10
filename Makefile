input_folder = data/html/files/
output_html = out/html/
output_words = out/words/
all_inputs = $(shell ls $(input_folder))
db_connect_str = postgres://postgres:password@localhost:5432/cosmos

.SECONDARY: preprocess.stamp parse.stamp parse.stamp

link.stamp: parse.stamp link.py
	python link.py --words_location $(output_words) --database $(db_connect_str) --ignored_files S1470160X05000063.pdf-0004.html
	@touch link.stamp

parse.stamp: preprocess.stamp parse.py
	python parse.py --html_location $(output_html) --database $(db_connect_str)
	@touch parse.stamp

preprocess.stamp: preprocess.py
	$(foreach file,$(all_inputs),\
	python preprocess.py --input $(input_folder)$(file) --output_words $(output_words)$(file).json --output_html $(output_html)$(file);)
	@touch preprocess.stamp

preprocess_clean:
	rm -f preprocess.stamp
	rm -f parse.stamp
	rm -f link.stamp
	rm -r -f $(output_html)/*
	rm -r -f $(output_words)/*


