"""Multivariate underlay analyser for the Polish Early Music editions.

Reads an edition's MusicXML (make musicxml), analyses the music on music21
(metre, sonorities, dissonance, cadences, phrases, imitation, texture) and the
text (lexicons), and judges the underlay against the series rules
(docs/editorial-principles.md §10) as an alignment problem with weighted
constraints. Severity is regret against the best legal alternative nearby.
It advises and never rewrites (principles 10.6). See docs/analyser.md.
"""
