import bioregistry
from pathlib import Path
from biolexica import iter_terms_by_prefix
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from gilda import dump_terms
from gilda.grounder import load_entries_from_terms_file

HERE = Path(__file__).parent.resolve()
TERMS_OUTPUT_PATH = HERE.joinpath("terms.tsv.gz")
CACHE = HERE.joinpath("cache")
CACHE.mkdir(exist_ok=True, parents=True)


def main():
    skip = {"pr"}
    prefixes = sorted(
        resource.prefix
        for resource in bioregistry.resources()
        if resource.get_obo_preferred_prefix()
        and not resource.is_deprecated()
        and not resource.no_own_terms
        and resource.prefix not in skip
    )

    all_terms = []
    for prefix in tqdm(prefixes):
        path = CACHE.joinpath(prefix).with_suffix(".tsv.gz")
        if path.is_file():
            all_terms.extend(load_entries_from_terms_file(path))
        else:
            local_terms = list(iter_terms_by_prefix(prefix, processor="bioontologies"))
            with logging_redirect_tqdm():
                dump_terms(local_terms, path)
            all_terms.extend(local_terms)

    dump_terms(all_terms, TERMS_OUTPUT_PATH)


if __name__ == "__main__":
    main()
