#!/bin/sh

/bin/sh /app/key_exchange.sh
python3 init_table.py
python3 app.py