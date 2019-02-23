# Montrehack - ROP101

This repository contains the source code, binaries and solutions to the
Montrehack workshop held on February 20th, 2019.

The workshop was live streamed and you can find my [presentation of the
slides][1] as well my [walk through of solutions 1 and 2][2] on Twitch.

[1]: https://www.twitch.tv/videos/384854978
[2]: https://www.twitch.tv/videos/384854977

## Running

For the challenges: have docker installed, run `./dist.sh`. The challenges will
be exposed on localhsot, port 3001 to 3003.

For the solutions: With pwntools installed, edit `sols/N.py` to point to your
local process or to the remote address, and run the script.  To follow along in
GDB, you can use `gdb.debug()` and run the script while running in tmux or
screen.


## Cleanup

```
docker stop rop-final
docker rm rop-final
docker rmi rop-final
```

## Compiling

If you build the challenges yourself, remember that offsets may change and the
solutiosn will no longer work. Using the challenges in `bin/` will give the
better experience. The code is provided to help understand why/how the
challenges work.
