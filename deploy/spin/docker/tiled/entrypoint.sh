#!/usr/bin/env bash

/app/docker/check_config.py && exec gunicorn --config /deploy/gunicorn_config.py
