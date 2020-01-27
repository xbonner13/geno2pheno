# geno2pheno

Application to run sequences through geno2pheno

Set up and dependencies can be found in ./dockerfile

Example from local terminal - no server set up, install selenium and chromedriver locally:

```bash
python selenium_python_geno2pheno.py ./unaligned_input.fasta
```

Example usage from terminal to remote server set up with repo:

```bash
curl -F file=@./unaligned_input.fasta -o g2p.tar.gz -L http://server.url/
```

Extract file received from curl (includes \_log and .fasta)

```bash
tar -xzvf g2p.tar.gz
```
