#!/bin/bash

# goes through every model
python3 mamba_magenta_api.py -a music_transformer -g random
python3 mamba_magenta_api.py -a music_vae -g random
python3 mamba_magenta_api.py -a melody_rnn -g random
python3 mamba_magenta_api.py -a performance_rnn -g random
python3 mamba_magenta_api.py -a pianoroll_rnn_nade -g random
python3 mamba_magenta_api.py -a improv_rnn -g random

sleep 1

