# Cell and Cell Line Lexicon

This directory contains a coherent, merged lexical index for the following
resources:

1. Medical Subject Headings (MeSH) (children of `mesh:D002477`)
2. Experimental Factor Ontology (EFO) (children of `efo:0000324`)
3. Cellosaurus
4. Cancer Cell Line Encyclopedia (CCLE)
5. DepMap
6. BRENDA Tissue Ontology (BTO)
7. Cell Ontology (CL)
8. Cell Line Ontology (CLO)

## Generating the Lexical Index

The index can be regenerated with:

```console
$ uv run --script generate.py
```

## Using in Python

Use in Python like in the following:

```python
import ssslm

INDEX = "cell"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

literal_mappings = ssslm.read_literal_mappings(URL)
grounder = ssslm.make_grounder(literal_mappings)
matches = grounder.get_matches("HeLA")
```

## Running an API

If you've cloned the repository, you can run:

```console
$ uv tool install ssslm[web,gilda-slim]
$ uv tool run ssslm web cell.ssslm.tsv.gz
```

If you have `ssslm[web,gilda-slim]` installed, you can do:

```python
from ssslm.web import run_app

INDEX = "cell"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

run_app(URL)
```
