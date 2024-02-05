<!--
<p align="center">
  <img src="https://github.com/biopragmatics/biolexica/raw/main/docs/source/logo.png" height="150">
</p>
-->

<h1 align="center">
  Biolexica
</h1>

<p align="center">
    <a href="https://github.com/biopragmatics/biolexica/actions/workflows/tests.yml">
        <img alt="Tests" src="https://github.com/biopragmatics/biolexica/actions/workflows/tests.yml/badge.svg" /></a>
    <a href="https://pypi.org/project/biolexica">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/biolexica" /></a>
    <a href="https://pypi.org/project/biolexica">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/biolexica" /></a>
    <a href="https://github.com/biopragmatics/biolexica/blob/main/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/biolexica" /></a>
    <a href='https://biolexica.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/biolexica/badge/?version=latest' alt='Documentation Status' /></a>
    <a href="https://codecov.io/gh/biopragmatics/biolexica/branch/main">
        <img src="https://codecov.io/gh/biopragmatics/biolexica/branch/main/graph/badge.svg" alt="Codecov status" /></a>  
    <a href="https://github.com/cthoyt/cookiecutter-python-package">
        <img alt="Cookiecutter template from @cthoyt" src="https://img.shields.io/badge/Cookiecutter-snekpack-blue" /></a>
    <a href='https://github.com/psf/black'>
        <img src='https://img.shields.io/badge/code%20style-black-000000.svg' alt='Code style: black' /></a>
    <a href="https://github.com/biopragmatics/biolexica/blob/main/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg" alt="Contributor Covenant"/></a>
</p>

`biolexica` helps generate and apply coherent biomedical lexica. It takes care of the following:

1. Getting names and synonyms from a diverse set of inputs (ontologies, databases, custom)
   using [`pyobo`](https://github.com/pyobo/pyobo), [`bioontologies`](https://github.com/biopragmatics/bioontologies), 
   [`biosynonyms`](https://github.com/biopragmatics/biosynonyms), and more.
2. Merging equivalent terms to best take advantage of different synonyms for the same term from different sources
   using [`semra`](https://github.com/biopragmatics/semra).
3. Generating lexical index and doing NER using [Gilda](https://github.com/gyorilab/gilda)

Importantly, we pre-define lexica for several entity types that can be readily used with Gilda in
the [`lexica/`](lexica/) folder including:

1. [Cells and cell lines](lexica/cell)
2. [Diseases, conditions, and other phenotypes](lexica/phenotype)
3. [Anatomical terms, tissues, organ systems, etc.](lexica/anatomy)

## Getting Started

Load a pre-defined grounder like this:

```python
import biolexica

grounder = biolexica.load_grounder("phenotype")

>>> grounder.get_best_match("Alzheimer's disease")
Match(reference=Reference(prefix='doid', identifier='10652'), name="Alzheimer's disease", score=0.7778)

>>> grounder.annotate("Clinical trials for reducing Aβ levels in Alzheimer's disease have been controversial.")
[Annotation(text="Alzheimer's disease", start=42, end=61, match=Match(reference=Reference(prefix='doid', identifier='10652'), name="Alzheimer's disease", score=0.7339))]
```

Note: Biolexica constructs extended version of `gilda.Grounder` that has convenience functions and a more
simple match data model encoded with Pydantic.

Search PubMed for abstracts and annotate them using a given grounder with:

```python
import biolexica
from biolexica.literature import annotate_abstracts_from_search

grounder = biolexica.load_grounder("phenotype")
pubmed_query = "alzheimer's disease"
annotations = annotate_abstracts_from_search(pubmed_query, grounder=grounder, limit=30)
```

## 🚀 Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/biolexica/) with:

```shell
pip install biolexica
```

The most recent code and data can be installed directly from GitHub with:

```shell
pip install git+https://github.com/biopragmatics/biolexica.git
```

## 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.md](https://github.com/biopragmatics/biolexica/blob/master/.github/CONTRIBUTING.md) for more information
on getting involved.

## 👋 Attribution

### ⚖️ License

The code in this package is licensed under the MIT License.

<!--
### 📖 Citation

Citation goes here!
-->

<!--
### 💰 Funding

This project has been supported by the following grants:

| Funding Body                                             | Program                                                                                                                       | Grant           |
|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------|
| DARPA                                                    | [Automating Scientific Knowledge Extraction (ASKE)](https://www.darpa.mil/program/automating-scientific-knowledge-extraction) | HR00111990009   |
-->

### 🍪 Cookiecutter

This package was created with [@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using [@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-snekpack](https://github.com/cthoyt/cookiecutter-snekpack) template.

## 🛠️ For Developers

<details>
  <summary>See developer instructions</summary>

The final section of the README is for if you want to get involved by making a code contribution.

### Development Installation

To install in development mode, use the following:

```bash
git clone git+https://github.com/biopragmatics/biolexica.git
cd biolexica
pip install -e .
```

### 🥼 Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
tox
```

Additionally, these tests are automatically re-run with each commit in a
[GitHub Action](https://github.com/biopragmatics/biolexica/actions?query=workflow%3ATests).

### 📖 Building the Documentation

The documentation can be built locally using the following:

```shell
git clone git+https://github.com/biopragmatics/biolexica.git
cd biolexica
tox -e docs
open docs/build/html/index.html
``` 

The documentation automatically installs the package as well as the `docs`
extra specified in the [`setup.cfg`](setup.cfg). `sphinx` plugins
like `texext` can be added there. Additionally, they need to be added to the
`extensions` list in [`docs/source/conf.py`](docs/source/conf.py).

The documentation can be deployed to [ReadTheDocs](https://readthedocs.io) using
[this guide](https://docs.readthedocs.io/en/stable/intro/import-guide.html).
The [`.readthedocs.yml`](.readthedocs.yml) YAML file contains all the configuration you'll need.
You can also set up continuous integration on GitHub to check not only that
Sphinx can build the documentation in an isolated environment (i.e., with ``tox -e docs-test``)
but also that [ReadTheDocs can build it too](https://docs.readthedocs.io/en/stable/pull-requests.html).

### 📦 Making a Release

After installing the package in development mode and installing
`tox` with `pip install tox`, the commands for making a new release are contained within the `finish` environment
in `tox.ini`. Run the following from the shell:

```shell
tox -e finish
```

This script does the following:

1. Uses [Bump2Version](https://github.com/c4urself/bump2version) to switch the version number in the `setup.cfg`,
   `src/biolexica/version.py`, and [`docs/source/conf.py`](docs/source/conf.py) to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel using [`build`](https://github.com/pypa/build)
3. Uploads to PyPI using [`twine`](https://github.com/pypa/twine). Be sure to have a `.pypirc` file
   configured to avoid the need for manual input at this step
4. Push to GitHub. You'll need to make a release going with the commit where the version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump the version by minor, you can
   use `tox -e bumpversion -- minor` after.

</details>
