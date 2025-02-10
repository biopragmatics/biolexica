# Disease, Phenotype, and Condition Lexicon

This directory contains a coherent, merged lexical index for the following
resources:

1. Human Disease Ontology (DOID)
2. MONDO Disease Ontology (MONDO)
3. Human Phenotype Ontology (HPO)
4. Symptom Ontology (SYMP)
5. Medical Subject Headings (MeSH)
6. Experimental Factor Ontology (EFO)

## Generating the Lexical Index

The index can be regenerated with:

```console
$ uv run --script generate.py
```

## Using in Python

Use in Python like in the following:

```python
import ssslm

INDEX = "phenotype"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

literal_mappings = ssslm.read_literal_mappings(URL)
grounder = ssslm.make_grounder(literal_mappings)
matches = grounder.get_matches("HeLA")
```

## Running an API

If you've cloned the repository, you can run:

```console
$ uv tool install ssslm[web,gilda-slim]
$ uv tool run ssslm web phenotype.ssslm.tsv.gz
```

If you have `ssslm[web,gilda-slim]` installed, you can do:

```python
from ssslm.web import run_app

INDEX = "phenotype"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

run_app(URL)
```
