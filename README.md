# FastAPI Tutorial

Step-by-step tutorial for learning FastAPI and building modern web APIs with Python.

## 1. Development Environment Setup - Windows

### Install `pyenv`
`pyenv` helps you manage and switch between multiple Python versions on your system.

1. Install pyenv (Windows) `git clone https://github.com/pyenv-win/pyenv-win.git ~/.pyenv`
2. Tell your Bash shell where to find it.
    ```bash
    echo 'export PYENV="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV/pyenv-win/bin:$PYENV/pyenv-win/shims:$PATH"' >> ~/.bashrc
    ```

    **First Command**

    ```bash
    echo 'export PYENV="$HOME/.pyenv"' >> ~/.bashrc
    ```
    * `echo '...'` simply prints whatever text is inside the quotes.
    * `export PYENV="$HOME/.pyenv"` is the text we are printing.
        - `PYENV` is the name of the environment variable.
        - It's being set to `$HOME/.pyenv`
        - `$HOME` means your home directory e.g., `C:/Users/Daniel`
    * `>> ~/.bashrc`
        - `>>` means *append the output to a file.*
        - `~/.bashrc` is your Bash configuration file (a hidden file in your home directory). 
    * In plain English: *Add a line to my Bash configuration file that defines where pyenv is installed*

    **Second Command**
    ```bash
    echo 'export PATH="$PYENV/pyenv-win/bin:$PYENV/pyenv-win/shims:$PATH"' >> ~/.bashrc
    ```
    * `echo 'export PATH=...'` prints the command `export PATH=...` to be appended to `.bashrc`
    * `$PYENV/pyenv-win/bin` contains the core pyenv command itself.
    * `$PYENV/pyenv-win/shims` contains shim executables, which act as lightweight wrappers for different Python versions.
    * By putting them before `$PATH`, you ensure:
        - When you type `python`, the system finds the `pyenv` shim first (not the Windows Store one).
        - When you type `pyenv`, it finds the real `pyenv-win` command.
    * In plain English: *Tell my shell to look in pyenv's folders first whenever I run commands*.
    * `>> ~/.bashrc` this appends the line to your `.bashrc`, so it runs automatically in every future terminal session. 

3. `exec "$SHELL"`

4. Useful commands:
    * `pyenv install --list` to see the list of python versions you can install.
    * `pyenv versions` to see the list of python versions you have already installed.
    * `pyenv install <VERSION>` to install the python version you want.
    * `pyenv local <VERSION>` sets the Python version for a specific project or directory.
        - When you run `pyenv local 3.10.6` (for example), it creates a file named `.python-version` in your current directory.
        - Whenever you’re inside that directory (or any subdirectory), `pyenv` automatically switches to use that Python version.
        - If you move to another folder without a `.python-version` file, it stops using that version.  
    * `pyenv global <VERSION>` sets the default (system-wide) Python version for your user account.
     
### Create a Python Virtual Environment


### Installing the `HTTPie` Command-Line Utility





## Resources:
* [Building Data Science Applications with FastAPI by Francois Voron - Jul 2023](https://github.com/PacktPublishing/Building-Data-Science-Applications-with-FastAPI-Second-Edition/tree/main)


