# Anatomy, Tissues, and Organ Systems

This directory contains a coherent, merged lexical index for the following resources:

1. uberon
2. mesh
3. bto
4. caro
5. ncit

## Generating the Lexical Index

The index can be regenerated with:

```console
$ uv run --script generate.py
```

The resulting index is in the SSSLM format.

## Using in Python

Use in Python like in the following:

```python
import ssslm

INDEX = "anatomy"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

literal_mappings = ssslm.read_literal_mappings(URL)
grounder = ssslm.make_grounder(literal_mappings)
matches = grounder.get_matches("HeLA")
```

## Running an API

If you've cloned the repository, you can run:

```console
$ uv tool install ssslm[web,gilda-slim]
$ uv tool run ssslm web anatomy.ssslm.tsv.gz
```

If you have `ssslm[web,gilda-slim]` installed, you can do:

```python
from ssslm.web import run_app

INDEX = "anatomy"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/{INDEX}.ssslm.tsv.gz"

run_app(URL)
```
