# くらくら BETA
A "dizzying"ly fast Python transpiler.    

## Virus Scans
- [Hybrid Analysis: Latest public beta](https://www.hybrid-analysis.com/sample/97f5168a104ddb96db1e035811d924cddba7adaf38447e7d8e96da272c4b304f)
- [Only HTTP requests in the program, for self-extraction](https://github.com/probablyacai/dizzying-public/blob/main/kurakura.py#L144-L191) - [See Uncrustify (bundled), we use it for beautifying output](https://github.com/uncrustify/uncrustify/)
- [The entry code where your specified command is run](https://github.com/probablyacai/dizzying-public/blob/main/kurakura.py#L2176)

## TL;DR
KuraKura allows you to transpile Python, especially code that is PROS/VEXCode-oriented, into a beautiful set of C++ or C++20 code, automatically beautifying code and generating safe and easy-to-maintain code.   
For those unwilling to read a fourteen year old's equivalent of a thesis project document, here are good links to look at to see if KuraKura is right for you.
- [**Jump** to this README's example & Installation tutorial](https://github.com/probablyacai/dizzying-public?tab=readme-ov-file#an-example-kurakura-script)
- [**Jump** to the examples: Hello World/Enum & PROS demo](https://github.com/probablyacai/dizzying-public/tree/main/example)
- [**Learn** how to use the ION package manager](https://github.com/probablyacai/dizzying-public?tab=readme-ov-file#commands-project-management)
- [**Learn** how to make a new project](https://github.com/probablyacai/dizzying-public?tab=readme-ov-file#set-up-a-project-and-compile)
- [**Info** on how stable Kura is](https://github.com/probablyacai/dizzying-public?tab=readme-ov-file#stability-status)

## Safety Status
**Naively Accepting** - The transpiler will accept any code you throw at it. No type safety, nor type guarantees - Be careful, and make sure you're following spec, docs and examples.   
**Current safety status**   
- 😁 Imports - Accepting only valid imports
- 😭 KuraScript - Unstable **Temporarily**
- 😉 Transpiler - Unsafe definitions and code are treated as ```auto```'s, but transpiler is relatively safe.
- 😁 Bug Reporting - Accepting only valid exceptions
- 😁 ION - Accepting only valid commands, all others are inferred as scripts if they end with the .py extension
- 😁 Error Handling - Safe
- 😭 Self Initialization - Unsafe, has the potential to overwrite existing files. **Will remain this way**

## Stability Status
**Relatively Stable** - Most features have been tested and should normally work well under test circumstances. However, sometimes code may break. Please make sure to keep a backup of your existing C++ code in case the code is modified in an unwanted manner by the transpiler.   
**Current feature status**   
- 😁 Imports
    - 😉 Namespace imports (via ```from namespaces.namespace import subnamespace```)
    - 😉 Header imports (via ```import local_header```)
    - 😉 Builtin imports (via ```from builtins import builtin```)
- 😭 KuraScript
    - 😐 **Unstable** please do not use
- 😁 Transpiler
    - 😉 Basic type conversion
    - 😉 Global conversion of None to void or empty
    - 😉 Basic namespace methods (via ```namespaces.namespace.function()```)
    - 😉 C++20 ```auto``` types.
    - 😉 Beautifier. **All tests compile!**
    - 😉 Class definitions **All tests compile!**
    - 😉 Enums (as specified in "Functional enums" [here](https://docs.python.org/3/library/enum.html)) **All tests compile!**
    - 😉 Class initialization (via ```new.Class()```)
- 😁 Misc.
    - 😉 Detailed error messages and bug report IDs
    - 😉 Test usecases compile
- 😁 ION (Package manager)
    - 😉 Initialize new portable project (via ```py kurakura.py new project```)
    - 😉 Package project into distributable zip (via ```py kurakura.py pkg project```)
    - 😉 Clean project (via ```py kurakura.py clean project```)
    - 😉 Delete project (via ```py kurakura.py del project```)
    - 😉 Reinitialize project with a toolchain, beautifier and config (via ```py kurakura.py remake project```)
    - 😉 Package toolchain for distribution (via ```py kurakura.py toolchain```)
- 😁 Error handling
    - 😉 Beautiful errors
    - 😉 Encode error messages when errors occur
    - 😉 Decode error messages (via ```py kurakura.py decode_error error_id```)
- 😁 Self-initialization
    - 😉 Require package install via ```requirements.txt```. That is all.
    - 😉 Download uncrustify, extract the exe into main folder.
    - 😉 Download uncrustify config.

## Usecases
Imagine this scenario:
- You need to quickly distribute your codebase to multiple people without missing a beat
- You need to write fast, high-performance VEX code quickly, but how?
  - You could write (very slow) Python-based code and have it perform relatively fine (other than more advanced computational tasks), but why?
    - Well, it's very easy to learn and quick to make scripts from
    - However, VEX's Python support is terrible, and you may want C++ interop.
    - You also want better documentation
  - But now, you want to make C++ scripts from them while still being able to explain your code and have C++ interop.
    - This is where KuraKura comes in.

## Have your cake and eat it too
- Python can be slow during intense computational tasks
- Python does not have C++ interop that can be performed via VEX.
- Vex's Python library does not have good documentation.
- You want to make type-safe and safety-guaranteed code that will always work, *no matter what*.
- However, you want to use Python, and have little time to write a huge C++ project and deal with errors all the time.

## Plus side?
- Verbose output explains your code and explains how it will be compiled and transformed.
- Very portable and fast.
- Compiles to the C++ language you know and love
- Generate type-safe, distributable code that will always work.
- Keep your own header files and original source code, just drag in ```include``` and ```src``` and compile!
- Improved compile speeds via ```kurakura.min.py```, the minified version

## An example Kurakura script
To begin, please install all needed requirements with ```py -m pip install -r requirements.txt```.   
Keep in mind - All functions MUST return a value, even if it is ```None``` (transpiled to ```void```).
```py
# file main.py

from bundled import bundle # Locally importing the file "bundle.py" from the folder "bundle"
from namespaces import pros # Import the namespace (a la "using namespace name") "pros"
from namespaces.pros import c
from . import autons # Locally importing "autons.py"

motor_test = new.Motor(1, E_MOTOR_GEARSET_18, True, E_MOTOR_ENCODER_DEGREES)

def autonomous() -> None: # Function "autonomous" returns void
    while True:
        motor_test.move(127)
        delay(25)
        pass
    return

def opcontrol() -> None: # Function "opcontrol" returns void
    while True:
        delay(25)
        pass

def initialize() -> None: # Function "initialize" returns void
    lcd.initialize()
    return


def main() -> int: # Function "main" returns int
    initialize()
    return 0
```

## C++20 Support
Some compilers (such as the one used in VEXCode and PROS) may not support C++20's extreme use of ```auto``` for type (un)safety. However, we provide support for C++20 auto, and we allow you to write regular, unmodified Python code: however, all functions still must return a value.
```py
from namespaces import pros
from namespaces.pros import c

def main():
    lcd.initialize()
    return
```

## Set up a project and compile
- Download kurakura.py into a root folder
- Make a new ```my_project``` - ```py kurakura.py new my_project```
- Change your current directory to that folder - ```cd my_project```
- Compile the main file - ```py kurakura.py main.py```

## Commands (project management)
Project paths are allowed to be "." for the current directory except for ```del```.   
- **Clean** a project's package and output folder: ```py kurakura.py clean projectPath```
- **Package** a project's output into a portable, sharable ```zip``` file: ```py kurakura.py pkg projectPath```
- **Delete** a project that is *not* in the current working directory: ```py kurakura.py del projectPath```
- **Bootstrap** a new project and copy the toolchain and utilities: ```py kurakura.py new projectPath```
- **Rehydrate** a project with the toolchain and utilities: ```py kurakura.py remake projectPath```

## Reporting bugs
- Please go to the issues or [DM me](https://discordapp.com/users/1021090674289942600) tab in order to report a bug.
- To fix a bug (most preferred), please create a pull request.

### ~242D
