# make            rebuild every edition and guide from the house style
# make <slug>     rebuild one
.PHONY: all lint $(notdir $(wildcard editions/* guides/*))
all: ; tools/build.sh
lint: ; tools/lint.sh
$(notdir $(wildcard editions/* guides/*)): ; tools/build.sh $@
