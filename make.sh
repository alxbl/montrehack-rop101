#!/bin/bash
### Poor man's Makefile.

# Challenge 1
 gcc -no-pie -fno-stack-protector --static 1.c -o motd_v0.1

 # Challenge 2
 gcc -no-pie -fno-stack-protector 2.c -o motd_v0.2

 # Challenge 3
 gcc -no-pie -fno-stack-protector 3.c -o motd_v0.3

