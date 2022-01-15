# GNU MO Files

Read and write GNU MO files.

Created using [The Format of GNU MO Files](https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html) article.

To the contrary of what's written there, **the file revision** is totally ignored.
The reason is that the difference between the revisions is not clear.

**The hash table** does not get written and ignored while reading, for Python dictionary uses its own hashing anyway.

Requires `Python >= 3.6` and no additional packages.
The code can be easily ported to older Python version, but I have no intention to.
