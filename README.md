# Machine Translation-based Fine-grained Comments Generation for Solidity Smart Contracts

## Data
The *contract* folder contains the 3,000 smart contracts collected from Etherscan. The names of .sol files are contract addresses.
## Execution Instructions
### AST Generation

`AST_gen.py` generates the AST file of Solidity source code (.sol) in JSON format. Source code with Solidity version <= 0.4 is not supported.

`python AST_gen.py <sourcecode-filename>.sol <AST-filename>.json`

### Code Translation

`AST_parse` parses the AST file and generates surface texts based on customized CFG rules.

`python AST_parse.py <AST-filename>.json`
