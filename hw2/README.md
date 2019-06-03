# Homework 02: Internals

## Opcode

Add new opcode (combine `LOAD_FAST` and `LOAD_CONST`) to the Python interpreter.

**Useful links:**

- [https://blog.quarkslab.com/building-an-obfuscated-python-interpreter-we-need-more-opcodes.html](https://blog.quarkslab.com/building-an-obfuscated-python-interpreter-we-need-more-opcodes.html)
- [https://gist.github.com/serge-sans-paille/71a4b1e656d70ae94bb4](https://gist.github.com/serge-sans-paille/71a4b1e656d70ae94bb4)

### Steps

1) Modify `Include/opcode.h`
2) Modify `Lib/opcode.py`
3) `make regen-opcode-targets`
4) Modify `Python/ceval.c`
5) Modify `Python/peephole.c`

### How to run

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply new_opcode.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```

Run in Docker:

```bash
# On host machine
docker build -t python-modified .
docker run -it --rm -v ./:/patch python-modified /bin/bash/
# In container
git apply /patch/new_opcode.patch
make -j2
```



## Until

Add new `until` statement to the Python interpreter.

**Useful links:**

- [https://eli.thegreenplace.net/2010/06/30/python-internals-adding-a-new-statement-to-python/](https://eli.thegreenplace.net/2010/06/30/python-internals-adding-a-new-statement-to-python/)
- [https://devguide.python.org/grammar/](https://devguide.python.org/grammar/)

### Steps

1) Modify `Grammar/Grammar`
2) `make regen-grammar`
3) Modify `Parser/Python.asdl`
4) `make regen-ast`
5) Modify `Python/ast.c`
6) Modify `Python/compile.c`
7) Modify `Python/symtable.c`

### How to run

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply until.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```

Run in Docker:

```bash
# On host machine
docker build -t python-modified .
docker run -it --rm -v ./:/patch python-modified /bin/bash/
# In container
git apply /patch/until.patch
make -j2
```



## Increment / Decrement

Add new `++` and `--` operators to the Python interpreter.

**Useful links:**

- [https://hackernoon.com/modifying-the-python-language-in-7-minutes-b94b0a99ce14](https://hackernoon.com/modifying-the-python-language-in-7-minutes-b94b0a99ce14)

### Steps

1) Modify `Grammar/Grammar`
2) `make regen-grammar`
3) Modify `Parser/tokenizer.c`
4) Modify `Include/token.h`
5) Modify `Python/ast.c`

### How to run

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply inc.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```

Run in Docker:

```bash
# On host machine
docker build -t python-modified .
docker run -it --rm -v ./:/patch python-modified /bin/bash/
# In container
git apply /patch/inc.patch
make -j2
```



## Git patch

```bash
git diff --binary > patch_name.patch
```