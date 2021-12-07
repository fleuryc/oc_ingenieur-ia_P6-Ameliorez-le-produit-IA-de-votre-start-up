[![Python application](https://github.com/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/actions/workflows/python-app.yml/badge.svg)](https://github.com/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/actions/workflows/python-app.yml)
[![CodeQL](https://github.com/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/actions/workflows/codeql-analysis.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/79b1cde8627141de8d00df17edd319de)](https://www.codacy.com/gh/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/dashboard)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/79b1cde8627141de8d00df17edd319de)](https://www.codacy.com/gh/fleuryc/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/dashboard)

- [Avis Restau : improve the AI product of your start-up](#avis-restau--improve-the-ai-product-of-your-start-up)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Virtual environment](#virtual-environment)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [Run Notebook](#run-notebook)
    - [Quality Assurance](#quality-assurance)
  - [Troubleshooting](#troubleshooting)

* * *

# Avis Restau : improve the AI product of your start-up

Repository of OpenClassrooms' [AI Engineer path](https://openclassrooms.com/fr/paths/188-ingenieur-ia), project #6

Goal : use Scikit-Learn and Keras conduct NLP, sentiment analysis and topic modeling on textual reviews, and CV for image classification.

You can see the results here :

-   [Presentation](https://fleuryc.github.io/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/index.html)

-   [HTML page with interactive plots](https://fleuryc.github.io/oc_ingenieur-ia_P6-Ameliorez-le-produit-IA-de-votre-start-up/notebook.html)

## Installation

### Prerequisites

-   [Python 3.9](https://www.python.org/downloads/)

### Virtual environment

```bash
# python -m venv env
# > or just :
make venv
source env/bin/activate
```

### Dependencies

```bash
# pip install --upgrade jupyterlab ipykernel ipywidgets widgetsnbextension graphviz python-dotenv requests matplotlib seaborn plotly numpy statsmodels pandas sklearn lightgbm nltk spacy gensim pyldavis Pillow scikit-image opencv-python tensorflow
# > or :
# pip install -r requirements.txt
# > or just :
make install
```

## Usage

### Run Notebook

```bash
jupyter-lab notebooks/main.ipynb
```

### Quality Assurance

```bash
# make isort
# make format
# make lint
# make bandit
# make mypy
# make test
# > or just :
make qa
```

## Troubleshooting

-   Fix Plotly issues with JupyterLab

cf. [Plotly troubleshooting](https://plotly.com/python/troubleshooting/#jupyterlab-problems)

```bash
jupyter labextension install jupyterlab-plotly
```

-   If using Jupyter Notebook instead of JupyterLab, uncomment the following lines in the notebook

```python
import plotly.io as pio
pio.renderers.default='notebook'
```
