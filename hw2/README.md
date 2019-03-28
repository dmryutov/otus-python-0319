# Homework 02: Internals

## Opcode

Добавление опкода, совмещающего в себе несколько других опкодов, в исходный код Python.

Запуск:

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply new_opcode.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```



## Until

Добавление оператора until в исходный код Python.

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply until.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```



## Increment / Decrement

Добавление операторов инкремента / декремента в исходный код Python.

```bash
git clone https://github.com/python/cpython.git
cd cpython
git checkout 2.7
git apply inc.patch
./configure --with-pydebug --prefix=/tmp/python
make -j2
```