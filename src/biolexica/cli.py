"""Command line interface for :mod:`biolexica`."""

import logging
from pathlib import Path

import click

__all__ = [
    "main",
]

logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option("--configuration", type=Path)
@click.option("--output", required=True, type=Path)
def main(configuration: Path, output: Path):
    """Assemble a lexicon based on a configuration file."""
    import json

    import biolexica

    configuration = biolexica.Configuration.model_validate(json.loads(configuration.read_text()))
    biolexica.assemble_terms(configuration, processed_path=output)


if __name__ == "__main__":
    main()
