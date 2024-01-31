# Lexical Indices

This directory contains pre-built lexical indices that can be directly
used with [Gilda](https://github.com/gyorilab/gilda):

1. [`cell`](cell) contains cells and cell lines
2. [`phenotype`](cell) contains diseases, phenotypes, and other conditions

Each has declarative configuration and a reproducible rebuild script such
that the resources can be updated periodically, either as the underlying
terminologies curate new terms or as new mappings become available.
Importantly, these lexical indices are **coherent**, meaning that equivalent
entities are merged together.
