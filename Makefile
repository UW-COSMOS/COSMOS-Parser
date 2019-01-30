input_folder = data/html/files/ #contains only the html source files
output_html = out/html/ #intermediate folder location (will be auto-generated)
output_words = out/words/ #intermediate folder location (will be auto-generated)
all_inputs = $(shell ls $(input_folder))
db_connect_str = postgres://postgres:xxxx@localhost:5432/cosmos

.SECONDARY: preprocess.stamp parse.stamp link.stamp

# 3. run the link file to insert coordinate information into fonduer based on the information from the json output folder (aka. hocr)
link.stamp: parse.stamp link.py
	python link.py --words_location $(output_words) --database $(db_connect_str) --ignored_files S1470160X05000063.pdf-0004.html
	@touch link.stamp

# 2. run the fonduer parser on the generated html file. This will fill in the postgres dabase with everything
# fonduer can understand except the coordinate information.
parse.stamp: preprocess.stamp parse.py
	python parse.py --html_location $(output_html) --database $(db_connect_str)
	@touch parse.stamp

# 1. preprocess the input html and store intermediate json and html in the output folder declared above.
preprocess.stamp: preprocess.py
	mkdir -p $(output_html)
	mkdir -p $(output_words)
	$(foreach file,$(all_inputs),\
	python preprocess.py --input $(input_folder)$(file) --output_words $(output_words)$(file).json --output_html $(output_html)$(file);)
	@touch preprocess.stamp

preprocess_clean:
	rm -f preprocess.stamp
	rm -f parse.stamp
	rm -f link.stamp
	rm -r -f $(output_html)
	rm -r -f $(output_words)


