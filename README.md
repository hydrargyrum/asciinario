# asciinario

`asciinario` is a scenario app for recording a session with [`asciinema`](https://asciinema.org/).
While `asciinema` is live recording, `asciinario` adds scripted recording.

## Rationale

`asciinema` is great for recording live terminal sessions and replay them.
Quality videos include:
- no typos (regular typing speed is a bonus)
- explanatory comments
Since there are no (yet?) good tools for editing `asciinema` casts, making a good asciinema cast requires near-perfection, as the slightest typo would require to restart the whole recording, which is tedious.

`asciinario` lets you automate the `asciinema` session.
It takes a carefully crafted scenario file with instructions to type stuff, display comments, pause for some time, etc. and then runs `asciinema` while the actions described in the scenario are played.

## Example

The following scenario
```
set type_wait = 0.1

status show top
-> welcome to asciinario!
wait 2
-> we are going to type some commands
wait 2
status clear
wait .5

$> python
wait 1
$> 1 + 1
-> well, i hope this result doesn't surprise you
wait 2
status clear
wait .5

$> 42 ** 42
-> i'm pretty sure you didn't know that one though :)
wait 2
status clear
wait .5

$> quit()
wait 1
> bye
-> have a nice day!
wait 2
key enter
```

produces the following cast: [![asciicast](https://asciinema.org/a/515937.svg)](https://asciinema.org/a/515937)
