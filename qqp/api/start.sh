#!/bin/bash
gunicorn -b 0.0.0.0:8000 --workers 3 app:application --reload