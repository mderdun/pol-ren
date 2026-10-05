# make            rebuild every edition and guide from the house style
# make <slug>     rebuild one
# make changed    rebuild only the editions and guides whose sources changed (DRY=1 lists them)
# make musicxml   MusicXML of every critical score (editions/<slug>/pdf/<slug>.musicxml)
.PHONY: all changed lint musicxml $(notdir $(wildcard editions/* guides/*))
all: ; tools/build.sh
changed: ; DRY=$(DRY) tools/build-changed.sh
lint: ; tools/lint.sh
musicxml: ; python3 tools/export_musicxml.py
$(notdir $(wildcard editions/* guides/*)): ; tools/build.sh $@
