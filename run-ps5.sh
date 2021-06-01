#!/usr/bin/bash
rm -f ./logs/*
rm geckodriver.log
rm nohup.out
nohup python3 ps5.py &
