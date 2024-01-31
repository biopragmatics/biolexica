# Anatomy, Tissues, and Organ Systems

This directory contains a coherent, merged lexical index for the following resources:

1. uberon
2. mesh
3. bto
4. caro
5. ncit

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

INDEX = "anatomy"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

grounder: gilda.Grounder = biolexica.load_grounder(URL)
scored_matches = grounder.ground("brain")
```

## Running an API

If you've cloned the repository, you can run:

```shell
python web.py
```

If you have `biolexica[web]` installed, you can do:

```python
from biolexica.web import run_app

INDEX = "anatomy"
URL = f"https://github.com/biopragmatics/biolexica/raw/main/lexica/{INDEX}/terms.tsv.gz"

run_app(URL)
```
