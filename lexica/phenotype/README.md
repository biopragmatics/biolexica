# Disease, Phenotype, and Condition Lexicon

This directory contains a coherent, merged lexical index for the following resources:

1. Human Disease Ontology (DOID)
2. MONDO Disease Ontology (MONDO)
3. Human Phenotype Ontology (HPO)
4. Symptom Ontology (SYMP)
5. Medical Subject Headings (MeSH)
6. Experimental Factor Ontology (EFO)

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

INDEX = "phenotype"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

grounder: gilda.Grounder = biolexica.load_grounder(URL)
scored_matches = grounder.ground("Alzheimer's disease")
```

## Running an API

If you've cloned the repository, you can run:

```shell
python web.py
```

If you have `biolexica[web]` installed, you can do:

```python
from biolexica.web import run_app

INDEX = "phenotype"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

run_app(URL)
```
