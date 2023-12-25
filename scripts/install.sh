#!/usr/bin/env bash

if [[ ! $@ ]]; then
    python3 -m install.sh -h
else
    python3 -m install.sh $@
fi

