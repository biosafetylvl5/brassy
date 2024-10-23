# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= python3 -m sphinx
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

examples:
	@echo "Building examples"
	@cd ./source/examples/basic-usage; \
	 brassy -o new-release-note release-note.yaml; \
	 brassy -o new-release-note-v1 release-note.yaml -r 1.0.0; \
	 brassy -o new-release-note-date release-note.yaml -d 3000-30-30; \
	 brassy -o new-release-note-header-footer release-note.yaml -p header.txt -s footer.txt

pages:
	@echo "Building github pages docs"
	@make clean
	@make html
	@rm -rf ./../docs
	@mv ./build/html ./../docs
	@rm -rf ./build
	@touch ./../docs/.nojekyll # This is to prevent github from rendering the docs strangely

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
