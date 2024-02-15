# OBO Foundry Lexicon

This contains all the terms from OBO Foundry ontologies
(minus Protein Ontology, which is stubborn and won't download).

```python
import json
import gilda
from urllib.request import urlretrieve

# download the URL until https://github.com/gyorilab/gilda/pull/132
# is accepted, then the URL can be used in gilda.Grounder directly
url = "https://github.com/biopragmatics/biolexica/raw/main/lexica/obo/terms.tsv.gz"
path = "terms.tsv.gz"
urlretrieve(url, path)

grounder = gilda.Grounder(path)

obo_prefix = ...
obo_uri_prefix = f"http://purl.obolibrary.org/obo/{obo_prefix}_"
path_to_obograph_json = ...
with open(path_to_obograph_json) as file:
    data = json.load(file)

safe = []

print("## Lexical matching returned results\n")
for graph in data['graphs']:
    for node in sorted(graph['nodes'], key=lambda n: n['id']):
        if node['type'] == "PROPERTY":
            continue
        uri = node['id']
        if not uri.startswith(obo_uri_prefix):
            continue

        identifier = uri[len(obo_uri_prefix) :]
        name = node['lbl']

        results = []
        results.extend(grounder.ground(name))
        results.extend(
            scored_match
            for synonym in node.get("meta", {}).get("synonyms", [])
            for scored_match in grounder.ground(synonym['val'])
        )

        if not results:
            safe.append((identifier, name)) 
        else:
            print(f'- f`{obo_prefix}:{identifier}`', name)
        for res in results:
            curie = res.term.get_curie()
            print(f'  - [`{curie}`](https://bioregistry.io/{curie}) {res.term.entry_name} ({round(res.score, 3)})')

print("\n## Lexical matching returned no results\n")
for luid, lbl in safe:
    print(f'- `CAROLIO:{luid}`', lbl)
```

Inspired by https://gist.github.com/cthoyt/d26df3ec12f6a15f3157546c6ebee3a2.
