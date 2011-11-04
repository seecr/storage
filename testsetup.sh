set -e

rm -rf tmp build

python setup.py install --root tmp

export PYTHONPATH=$(find `pwd` -name '*-packages' -print)
cp -r test tmp/test

(
cd tmp/test
./alltests.sh
)

rm -rf tmp build
