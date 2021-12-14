#!/bin/bash
for f in ./logs/*BC.json; do
    md5sum $f
done
