#!/bin/bash
# setup_secret.sh

cd ..

if [ ! -f secret_key.txt ]; then
    python3 -c "import secrets; print(secrets.token_hex(32))" > secret_key.txt
    chmod 600 secret_key.txt
    echo "secret_key.txt created"
else
    echo "secret_key.txt already exists"
fi
