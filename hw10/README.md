# Homework 10: C Extensions

## Protobuf (de)serializer

Complete C Extension `pb.c`:

- Implement `deviceapps_xwrite_pb` which should
    - Accept iterable object with dictionaries and output file path as arguments
    - Write serialized into protobuf gzipped messages to a file
    - Prepend each protobuf message with a header (`pbheader_t`)
    - Return number of written bytes
- Implement `deviceapps_xread_pb` which should
    - Accept input file path as argument
    - Read messages from `deviceapps_xwrite_pb` and convert them back to dictionaries
    - Return generator object with dictionaries
- Write more tests

**Useful links:**

- [Python/C API Reference Manual](https://docs.python.org/3.7/c-api/index.html)
- [Porting guide for Python C Extensions](https://py3c.readthedocs.io/en/latest/reference.html)
- [Implementing a generator/yield in a Python C extension](https://eli.thegreenplace.net/2012/04/05/implementing-a-generatoryield-in-a-python-c-extension)



### Requirements

- Python 3.x



### Install dependencies

Install Python dependencies:

```bash
pip3 install -r requirements.txt
```

Install `protobuf`:

```bash
# macOS
brew install protobuf
# Ubuntu
curl -OL https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
unzip protoc-3.2.0-linux-x86_64.zip -d protoc3
sudo mv protoc3/bin/* /usr/local/bin/
sudo mv protoc3/include/* /usr/local/include/
```

Install `protobuf-c`:

```bash
# Prepare package
git clone https://github.com/protobuf-c/protobuf-c
cd protobuf-c
chmod +x ./autogen.sh

# macOS
brew install autoconf automake libtool pkg-config
# Ubuntu
sudo apt-get update
sudo apt-get install autoconf, automake, libtool

# Fix namespace issue
# https://github.com/protobuf-c/protobuf-c/issues/356#issuecomment-460079949

# Build and install package
./autogen.sh && ./configure && make && make install
```

Generate `deviceapps.pb-c.c` and `deviceapps.pb-c.h` (if you want to create project from scratch):

```bash
cd deviceapps
protoc --c_out=. deviceapps.proto
```



### How to run

```bash
# Install `pb` module
python3 setup.py install
# Run Python shell
python3
```

Run in Docker:

```bash
docker build -t pb .
docker run -it --rm pb
```

Usage:

```python
import pb

file_name = 'test.pb.gz'
deviceapps = [
    {"device": {"type": "idfa", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7c"},
     "lat": 67.7835424444, "lon": -22.8044005471, "apps": [1, 2, 3, 4]},
]

# Write
total_bytes = pb.deviceapps_xwrite_pb(deviceapps, file_name)
print(total_bytes)  # 76
# Read
result = list(pb.deviceapps_xread_pb(file_name))
print(result == deviceapps)  # True
```



### Testing

```bash
python3 -m unittest
```