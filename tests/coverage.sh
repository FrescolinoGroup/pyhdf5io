#!/bin/bash
py.test -p no:cov-exclude --cov=fsc.hdf5_io --cov-report=html
