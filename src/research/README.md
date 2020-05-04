# Research

## Quantitative

This directory deals with the research performed and the data collected.

Note that the `data/` directory is empty; code was copied into that directory and data collection performed, but is not committed to this GitHub repository
to avoid unnecessary headache.

In addition, some code bases are closed-source (from my work as a software engineer) and so were not able to be committed to this repository for proprietary concerns.

All code bases are written in python.

Open source libraries analyzed:

- https://github.com/mvantellingen/python-zeep
- https://github.com/paramiko/paramiko
- https://github.com/django/django
- https://github.com/sqlalchemy/sqlalchemy

Closed source code bases analyzed (general description):

- A configuration management API
- An ETL (extract-transform-load) process
- A aggregation/forwarder process
- A data regeneration service

### Steps

[Radon](https://pypi.org/project/radon/) `raw` metrics were used to compute logical lines of code, or **LLOC**, using (`python-zeep` as an example) `radon raw data/python-zeep/src -s -j --output-file stats/python-zeep.json`.

The custom `analyzer.py` python script was then run on each of the files output by `Radon` and was used to
detect the number of boilerplate lines of code or **BBPLLOC**. This step also calculated _maximal gain ratio_ or **bpgr**, which was computed as:

```
bpgr = (lloc - bplloc) / lloc
```

## Qualitative

A survey was posted here: [Google Forms](https://docs.google.com/forms/d/e/1FAIpQLSdedVeDo_dnrWVJH1PtPw7wiyB3aZHUf7LHREVO6Q7LtZfpLQ/viewform).

I circulated the survey to my friends and work colleagues.
