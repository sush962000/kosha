OBJ_DIR=static
BOWER_COMP_DIR=bower_components
POLYMER_ELEM_DIR=elements
HTML_SRCS=index.html

bower_srcs=$(shell find $(BOWER_COMP_DIR) -type f -name '*')
element_srcs=$(shell find $(POLYMER_ELEM_DIR) -type f -name '*')
html_objs=$(addprefix $(OBJ_DIR)/, $(HTML_SRCS))

all: dist

dist: $(html_objs)

$(html_objs): $(OBJ_DIR)/% : % $(bower_srcs) $(element_srcs)
	vulcanize -o $@ $< --inline --strip

setup:
	bower install

serve: dist
	python kosha.py

clean:
	rm -f $(html_objs)

.PHONY: all clean dist serve
