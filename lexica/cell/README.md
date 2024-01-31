# Cell and Cell Line Lexicon

This directory contains a coherent, merged lexical index for the following resources:

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

```shell
python generate.py
```

## Using in Python

Use in Python like in the following:

```python
import biolexica
import gilda

INDEX = "cell"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

grounder: gilda.Grounder = biolexica.load_grounder(URL)
scored_matches = grounder.ground("HeLA")
```

## Running an API

If you've cloned the repository, you can run:

```shell
python web.py
```

If you have `biolexica[web]` installed, you can do:

```python
from biolexica.web import run_app

INDEX = "cell"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

run_app(URL)
```
