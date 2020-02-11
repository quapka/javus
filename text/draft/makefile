TARGET = draft

all: $(TARGET)

$(TARGET):
	pdflatex $@.tex
	# bibtex $@
	# pdflatex $@.tex
	# pdflatex $@.tex

.PHONY: clean
clean:
	-rm $(TARGET).aux $(TARGET).bbl $(TARGET).blg $(TARGET).log $(TARGET).out $(TARGET).pdf

build: clean $(TARGET)
