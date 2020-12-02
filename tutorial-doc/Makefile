.PHONY: all build preview print ebook cleanall clean

# Vars
SRC     := ${PWD}
OUT     := ${PWD}/build

# Commands
LATEXMK := latexmk
LATEXMK_FLAGS := -pdf
#LATEXMK_FLAGS += -silent
LATEXMK_FLAGS += -view=none
LATEXMK_FLAGS += -auxdir=${OUT}
LATEXMK_FLAGS += -outdir=${OUT}
LATEXMK_FLAGS += -pdflatex="pdflatex -file-line-error --shell-escape %O %S"
LATEXMK_FLAGS += -e '$$makeindex=qq/sh -c "cd "`dirname "%D"`" ; makeindex %O -o "`basename "%D"`" "`basename "%S"`""/;'

all: build

build:
	cd ${OUT} ; ${LATEXMK} ${LATEXMK_FLAGS} -cd ${SRC}/main.tex

preview: build
	(${LATEXMK} ${LATEXMK_FLAGS} -pvc -cd & ${LATEXMK} ${LATEXMK_FLAGS} -pvc -cd ${SRC}/main.tex)

print: build
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile=${OUT}/thesis-print.pdf ${OUT}/main.pdf ${OUT}/thesis-print.pdf

ebook: build
	gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=${OUT}/thesis-ebook.pdf ${OUT}/main.pdf

clean:
	@find ${OUT} -type f ! -name '*.pdf' ! -name '.*' -exec rm "{}" \;

cleanall:
	@find ${OUT} -type f ! -name '.*' -exec rm "{}" \;
