# Coding standard

---
## General

  * Use spaces, not tabs.
  * Avoid adding trailing whitespace as it creates noise in the diffs.

---
## Python

  * Comments should not exceed 80 columns, code should not exceed 120 columns.
  * All code must be compatible with Python 2.7 and 3.7.
  * [Pylint][pylintlink] should not give any error or warning (few exceptions apply with external classes like `numpy` and `pygame`, see our `.pylintrc`).
  * Python code follows [PEP8 style guide][pep8link] (use `autopep8` whenever possible).

[pylintlink]: https://www.pylint.org/
[pep8link]: https://www.python.org/dev/peps/pep-0008/