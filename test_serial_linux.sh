#!/usr/bin/env bash

socat -d -d pty,raw,echo=0,b9600,link=port1 pty,raw,echo=0,b9600,link=port2
