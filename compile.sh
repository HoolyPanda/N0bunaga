#! /bin/bash
pyinstaller -F main.py
mv dist/main .
./main
