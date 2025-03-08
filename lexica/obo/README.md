# OBO Foundry Lexicon

This contains all the terms from OBO Foundry ontologies.

It can be regenerated with:

```console
$ uv run --script generate.py
```

The following script can be adapted to check new ontologies against existing
terms:

```python
import json
import ssslm

url = "https://github.com/biopragmatics/biolexica/raw/main/lexica/obo/terms.tsv.gz"
grounder = ssslm.make_grounder(url)

obo_prefix = ...
obo_uri_prefix = f"http://purl.obolibrary.org/obo/{obo_prefix}_"
path_to_obograph_json = ...
with open(path_to_obograph_json) as file:
    data = json.load(file)

safe = []

print("## Lexical matching returned results\n")
for graph in data['graphs']:
    for node in sorted(graph['nodes'], key=lambda n: n['id']):
        uri = node['id']
        if not uri.startswith(obo_uri_prefix):
            continue

        # Skip nodes without a label
        name = node.get('lbl')
        if not name:
            continue

        identifier = uri[len(obo_uri_prefix) :]

        results = []
        results.extend(grounder.get_matches(name))
        results.extend(
            scored_match
            for synonym in node.get("meta", {}).get("synonyms", [])
            for scored_match in grounder.get_matches(synonym['val'])
        )

        if not results:
            safe.append((identifier, name))
        else:
            print(f'- f`{obo_prefix}:{identifier}`', name)
        for res in results:
            curie = res.term.get_curie()
            print(f'  - [`{curie}`](https://bioregistry.io/{curie}) {res.term.entry_name} ({round(res.score, 3)})')

print("\n## Lexical matching returned no results\n")
for identifier, name in safe:
    print(f'- `{obo_prefix}:{identifier}`', name)
```

Inspired by https://gist.github.com/cthoyt/d26df3ec12f6a15f3157546c6ebee3a2.
