# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

examples:
	@echo "Building examples"
	@cd ./source/examples/basic-usage; \
	 yarn -o new-release-note release-note.yaml; \
	 yarn -o new-release-note-v1 release-note.yaml -v 1.0.0; \
	 yarn -o new-release-note-date release-note.yaml -d 3000-30-30; \
	 yarn -o new-release-note-header-footer release-note.yaml -p header.txt -s footer.txt

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
