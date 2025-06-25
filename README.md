Code to run the 'Jewel', a remote for the Shared Game Timer. The Jewel features a single big button with 19 programmable LEDs set into the button cap, 12 in an outer ring, 6 in a middle ring and a final LED in the very middle.

What is The Shared Game Timer?  It is a board game timer that runs in the browser. See https://sharedgametimer.com for more info.

It has a Bluetooth API that allow for electronic devices to act as remotes, letting players interact with the timer through physical devices. This is one such device.

## Installation

You need a microcontroller set up to run CircuitPython. See https://circuitpython.org/ for help with that.

Before running the following commands, please safe-copy the files on your microcontroller and remove all old code.

Then run the following git command from the root of your microcontroller (I assume you have git installed) where you would normally have your `code.py` file.

`git clone --separate-git-dir "C:\Path\To\Somewhere\On\Your\Computer\Where\You\Want\The\Git\Dir" --recurse-submodules https://github.com/Parakoos/sgt-cp-device-jewel .`

That will download this repos working tree files directly to you microcontroller. It will also set up a git directory to hold the git files somewhere on your computer. It is a good idea to keep these things separate since your microcontroller may be short on space.
