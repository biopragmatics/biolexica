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
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
    <a href="https://github.com/biopragmatics/biolexica/blob/main/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg" alt="Contributor Covenant"/></a>
    <!-- uncomment if you archive on zenodo
    <a href="https://zenodo.org/badge/latestdoi/XXXXXX">
        <img src="https://zenodo.org/badge/XXXXXX.svg" alt="DOI"></a>
    -->
</p>

`biolexica` helps generate and apply coherent biomedical lexica. It takes care
of the following:

1. Getting names and synonyms from a diverse set of inputs (ontologies,
   databases, custom) using [`pyobo`](https://github.com/pyobo/pyobo),
   [`bioontologies`](https://github.com/biopragmatics/bioontologies),
   [`biosynonyms`](https://github.com/biopragmatics/biosynonyms), and more.
2. Merging equivalent terms to best take advantage of different synonyms for the
   same term from different sources using
   [`semra`](https://github.com/biopragmatics/semra).
3. Generating lexical index and doing NER using a standard interface from
   [SSSLM](https://github.com/cthoyt/ssslm)

Importantly, we pre-define lexica for several entity types that can be readily
used with any NLP tools wrapped by SSSLM, such as
[Gilda](https://github.com/gyorilab/gilda). They can be found in the
[`lexica/`](lexica/) folder including:

1. [Cells and cell lines](lexica/cell)
2. [Diseases, conditions, and other phenotypes](lexica/phenotype)
3. [Anatomical terms, tissues, organ systems, etc.](lexica/anatomy)

## 💪 Getting Started

Load a pre-defined grounder like this:

```python
import biolexica

grounder = biolexica.load_grounder("phenotype")

>>> grounder.get_best_match("Alzheimer's disease")
Match(reference=Reference(prefix='doid', identifier='10652'), name="Alzheimer's disease", score=0.7778)

>>> grounder.annotate("Clinical trials for reducing Aβ levels in Alzheimer's disease have been controversial.")
[Annotation(text="Alzheimer's disease", start=42, end=61, match=Match(reference=Reference(prefix='doid', identifier='10652'), name="Alzheimer's disease", score=0.7339))]
```

## 🚀 Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/biolexica/) with uv:

```console
$ uv pip install biolexica
```

or with pip:

```console
$ python3 -m pip install biolexica
```

The most recent code and data can be installed directly from GitHub with uv:

```console
$ uv --preview pip install git+https://github.com/biopragmatics/biolexica.git
```

or with pip:

```console
$ UV_PREVIEW=1 python3 -m pip install git+https://github.com/biopragmatics/biolexica.git
```

Note that this requires setting `UV_PREVIEW` mode enabled until the uv build
backend becomes a stable feature.

## 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are
appreciated. See
[CONTRIBUTING.md](https://github.com/biopragmatics/biolexica/blob/master/.github/CONTRIBUTING.md)
for more information on getting involved.

## 👋 Attribution

### ⚖️ License

The code in this package is licensed under the MIT License.

<!--
### 📖 Citation

Citation goes here!
-->

<!--
### 🎁 Support

This project has been supported by the following organizations (in alphabetical order):

- [Biopragmatics Lab](https://biopragmatics.github.io)

-->

<!--
### 💰 Funding

This project has been supported by the following grants:

| Funding Body  | Program                                                      | Grant Number |
|---------------|--------------------------------------------------------------|--------------|
| Funder        | [Grant Name (GRANT-ACRONYM)](https://example.com/grant-link) | ABCXYZ       |
-->

### 🍪 Cookiecutter

This package was created with
[@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using
[@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-snekpack](https://github.com/cthoyt/cookiecutter-snekpack)
template.

## 🛠️ For Developers

<details>
  <summary>See developer instructions</summary>

The final section of the README is for if you want to get involved by making a
code contribution.

### Development Installation

To install in development mode, use the following:

```console
$ git clone git+https://github.com/biopragmatics/biolexica.git
$ cd biolexica
$ uv --preview pip install -e .
```

Alternatively, install using pip:

```console
$ UV_PREVIEW=1 python3 -m pip install -e .
```

Note that this requires setting `UV_PREVIEW` mode enabled until the uv build
backend becomes a stable feature.

### Updating Package Boilerplate

This project uses `cruft` to keep boilerplate (i.e., configuration, contribution
guidelines, documentation configuration) up-to-date with the upstream
cookiecutter package. Install cruft with either `uv tool install cruft` or
`python3 -m pip install cruft` then run:

```console
$ cruft update
```

More info on Cruft's update command is available
[here](https://github.com/cruft/cruft?tab=readme-ov-file#updating-a-project).

### 🥼 Testing

After cloning the repository and installing `tox` with
`uv tool install tox --with tox-uv` or `python3 -m pip install tox tox-uv`, the
unit tests in the `tests/` folder can be run reproducibly with:

```console
$ tox -e py
```

Additionally, these tests are automatically re-run with each commit in a
[GitHub Action](https://github.com/biopragmatics/biolexica/actions?query=workflow%3ATests).

### 📖 Building the Documentation

The documentation can be built locally using the following:

```console
$ git clone git+https://github.com/biopragmatics/biolexica.git
$ cd biolexica
$ tox -e docs
$ open docs/build/html/index.html
```

The documentation automatically installs the package as well as the `docs` extra
specified in the [`pyproject.toml`](pyproject.toml). `sphinx` plugins like
`texext` can be added there. Additionally, they need to be added to the
`extensions` list in [`docs/source/conf.py`](docs/source/conf.py).

The documentation can be deployed to [ReadTheDocs](https://readthedocs.io) using
[this guide](https://docs.readthedocs.io/en/stable/intro/import-guide.html). The
[`.readthedocs.yml`](.readthedocs.yml) YAML file contains all the configuration
you'll need. You can also set up continuous integration on GitHub to check not
only that Sphinx can build the documentation in an isolated environment (i.e.,
with `tox -e docs-test`) but also that
[ReadTheDocs can build it too](https://docs.readthedocs.io/en/stable/pull-requests.html).

#### Configuring ReadTheDocs

1. Log in to ReadTheDocs with your GitHub account to install the integration at
   https://readthedocs.org/accounts/login/?next=/dashboard/
2. Import your project by navigating to https://readthedocs.org/dashboard/import
   then clicking the plus icon next to your repository
3. You can rename the repository on the next screen using a more stylized name
   (i.e., with spaces and capital letters)
4. Click next, and you're good to go!

### 📦 Making a Release

#### Configuring Zenodo

[Zenodo](https://zenodo.org) is a long-term archival system that assigns a DOI
to each release of your package.

1. Log in to Zenodo via GitHub with this link:
   https://zenodo.org/oauth/login/github/?next=%2F. This brings you to a page
   that lists all of your organizations and asks you to approve installing the
   Zenodo app on GitHub. Click "grant" next to any organizations you want to
   enable the integration for, then click the big green "approve" button. This
   step only needs to be done once.
2. Navigate to https://zenodo.org/account/settings/github/, which lists all of
   your GitHub repositories (both in your username and any organizations you
   enabled). Click the on/off toggle for any relevant repositories. When you
   make a new repository, you'll have to come back to this

After these steps, you're ready to go! After you make "release" on GitHub (steps
for this are below), you can navigate to
https://zenodo.org/account/settings/github/repository/biopragmatics/biolexica to
see the DOI for the release and link to the Zenodo record for it.

#### Registering with the Python Package Index (PyPI)

You only have to do the following steps once.

1. Register for an account on the
   [Python Package Index (PyPI)](https://pypi.org/account/register)
2. Navigate to https://pypi.org/manage/account and make sure you have verified
   your email address. A verification email might not have been sent by default,
   so you might have to click the "options" dropdown next to your address to get
   to the "re-send verification email" button
3. 2-Factor authentication is required for PyPI since the end of 2023 (see this
   [blog post from PyPI](https://blog.pypi.org/posts/2023-05-25-securing-pypi-with-2fa/)).
   This means you have to first issue account recovery codes, then set up
   2-factor authentication
4. Issue an API token from https://pypi.org/manage/account/token

#### Configuring your machine's connection to PyPI

You have to do the following steps once per machine.

```console
$ uv tool install keyring
$ keyring set https://upload.pypi.org/legacy/ __token__
$ keyring set https://test.pypi.org/legacy/ __token__
```

Note that this deprecates previous workflows using `.pypirc`.

#### Uploading to PyPI

After installing the package in development mode and installing `tox` with
`uv tool install tox --with tox-uv` or `python3 -m pip install tox tox-uv`, run
the following from the console:

```console
$ tox -e finish
```

This script does the following:

1. Uses [bump-my-version](https://github.com/callowayproject/bump-my-version) to
   switch the version number in the `pyproject.toml`, `CITATION.cff`,
   `src/biolexica/version.py`, and [`docs/source/conf.py`](docs/source/conf.py)
   to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel using
   [`uv build`](https://docs.astral.sh/uv/guides/publish/#building-your-package)
3. Uploads to PyPI using
   [`uv publish`](https://docs.astral.sh/uv/guides/publish/#publishing-your-package).
4. Push to GitHub. You'll need to make a release going with the commit where the
   version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump
   the version by minor, you can use `tox -e bumpversion -- minor` after.

#### Releasing on GitHub

1. Navigate to https://github.com/biopragmatics/biolexica/releases/new to draft
   a new release
2. Click the "Choose a Tag" dropdown and select the tag corresponding to the
   release you just made
3. Click the "Generate Release Notes" button to get a quick outline of recent
   changes. Modify the title and description as you see fit
4. Click the big green "Publish Release" button

This will trigger Zenodo to assign a DOI to your release as well.

</details>
