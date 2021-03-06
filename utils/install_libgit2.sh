#!/bin/bash

set -e

export LIBGIT2=$VIRTUAL_ENV
export LDFLAGS="-Wl,-rpath='$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
wget https://github.com/libgit2/libgit2/archive/v0.21.1.tar.gz
tar xzf v0.21.1.tar.gz
cd libgit2-0.21.1/
cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
cmake --build . --target install
cmake --build .
make
make install
pip install cffi
pip install pygit2==0.21.1
cd ..
rm v0.21.1.tar.gz*
