# LG

## Setup

If you are on a Mac, you can install the required packages using the following commands:

```bash
brew install graphviz
export C_INCLUDE_PATH="$(brew --prefix graphviz)/include/"
export LIBRARY_PATH="$(brew --prefix graphviz)/lib/"
pip install --use-pep517 --config-setting="--global-option=build_ext" pygraphviz
```
