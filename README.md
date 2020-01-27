# geno2pheno

Application to run sequences through geno2pheno

Set up and dependencies can be found in the dockerfile

Example usage from terminal for local processing:

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
