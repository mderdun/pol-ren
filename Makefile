# make            rebuild every edition and guide from the house style
# make <slug>     rebuild one
# make musicxml   MusicXML of every critical score (editions/<slug>/pdf/<slug>.musicxml)
.PHONY: all lint musicxml $(notdir $(wildcard editions/* guides/*))
all: ; tools/build.sh
lint: ; tools/lint.sh
musicxml: ; python3 tools/export_musicxml.py
$(notdir $(wildcard editions/* guides/*)): ; tools/build.sh $@
