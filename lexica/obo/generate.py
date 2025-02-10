# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "biolexica",
#     "pyobo",
#     "semra",
#     "ssslm[gilda-slim]",
#     "bioontologies",
# ]
#
# [tool.uv.sources]
# semra = { path = "../../../semra", editable = true  }
# biolexica = { path = "../..", editable = true  }
# pyobo = { path = "../../../pyobo", editable = true }
# ssslm = { path = "../../../ssslm", editable = true }
# bioontologies = { path = "../../../bioontologies", editable = true }
#
# ///

from pathlib import Path

import bioregistry
import click
import ssslm
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from biolexica import get_literal_mappings_by_prefix

HERE = Path(__file__).parent.resolve()
LITERAL_MAPPINGS_PATH = HERE.joinpath("obo.ssslm.tsv.gz")
GILDA_PATH = HERE.joinpath("terms.tsv.gz")
CACHE = HERE.joinpath("cache")
CACHE.mkdir(exist_ok=True, parents=True)


@click.command()
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

    literal_mappings: list[ssslm.LiteralMapping] = []
    for prefix in tqdm(prefixes):
        path = CACHE.joinpath(prefix).with_suffix(".ssslm.tsv.gz")
        if path.is_file():
            literal_mappings.extend(ssslm.read_literal_mappings(path))
        else:
            local_literal_mappings = list(
                get_literal_mappings_by_prefix(prefix, processor="bioontologies")
            )
            with logging_redirect_tqdm():
                ssslm.write_literal_mappings(path=path, literal_mappings=local_literal_mappings)
            literal_mappings.extend(local_literal_mappings)

    ssslm.write_literal_mappings(path=LITERAL_MAPPINGS_PATH, literal_mappings=literal_mappings)

    try:
        from gilda import dump_terms
    except ImportError:
        click.secho("could not import gilda", fg="red")
    else:
        dump_terms([t.to_gilda() for t in literal_mappings], GILDA_PATH)


if __name__ == "__main__":
    main()
