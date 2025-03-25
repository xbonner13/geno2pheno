# geno2pheno

Application to automate running sequences through geno2pheno core receptor

## Setup

This version of Python and Selenium automagically install drivers and dependencies. Does not work on Apple Silicone.

```bash
docker-compose build && docker-compose up
```

## Running

```bash
python3 selenium_python_geno2pheno.py ./input named_output
```

The first argument can be a fasta file or directory of fasta files.
