# Requires LuaLaTeX, GregorioTeX 6 (gregorio binary) and the Junicode font.
all: bogurodzica-critical.pdf bogurodzica-performance.pdf bogurodzica-edition.pdf

bogurodzica.gtex: bogurodzica.gabc
	gregorio $<
bogurodzica-performance.gtex: bogurodzica-performance.gabc
	gregorio $<

bogurodzica-critical.pdf bogurodzica-edition.pdf: %.pdf: %.tex bogurodzica.gtex
	lualatex -interaction=nonstopmode $< && lualatex -interaction=nonstopmode $<
bogurodzica-performance.pdf: bogurodzica-performance.tex bogurodzica-performance.gtex
	lualatex -interaction=nonstopmode $< && lualatex -interaction=nonstopmode $<

clean:
	rm -f *.aux *.log *.out *.gaux *.gtex
.PHONY: all clean
