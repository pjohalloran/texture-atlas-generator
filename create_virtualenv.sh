#!/bin/sh

python3 -m venv env
if [ $? -ne 0 ]; then
    echo "Failed to create python VirtualEnv"
    exit 1
fi

. env/bin/activate
if [ $? -ne 0 ]; then
    echo "Error environment not activated"
    exit 1
fi
echo "virtualenv activated"

eval "pip install --upgrade pip"
if [ $? -ne 0 ]; then
    echo "Error Failed to upgrade pip in the virtualenv"
    exit 1
fi

eval "pip install -r requirements.txt"
if [ $? -ne 0 ]; then
    echo "Error Failed to install requirements"
    exit 1
fi
echo "Success"
