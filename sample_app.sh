#!/usr/bin/env bash

python3 ./sample_app.py firstpositional positionallist \
                        --malformed somethingmalformed \
                        -o somethingoptional \
                        --user_configs resources/user_config/user.conf resources/user_config/user_secret.conf
