# Flatland Model Diagram (non) Editor

NEW Status January 13, 2025

I have recently rebuilt the entire application based on a series of modules available on GitHub and PyPI. 
Will be deploying in ernest in the coming days.

Am de-commisioning the old version on GitHub and PyPI named 'flatland-model-diagram-editor'
Now it is just 'flatland' here on GitHub and 'mi-flatland' on PyPI

Ah yes, yet another tool for generating diagrams from text. But this one is different (otherwise I wouldn't have wasted all this time building it!)

I built Flatland because the following benefits are critical for productive model development:

1. Complete separation of the model semantics from the diagram layout
2. Complete separation of model semantics from model notation
3. Consistent layout of model diagrams without forcing the user to accept or hack awkard, non-sensical placements of nodes and connectors (yeah, I'm lookin at YOU PlantUML)
4. Maximum layout power with minimal specification:  No more carpal tunnel pixel pushing!
5. Beautiful, readable diagram output in many output formats (pdf, svg, etc)
6. Support for industrial strength modeling (many hundreds and thousands of model elements)
7. Use your favorite text editor and all the advanced facilities of it and whatever IDE you like without having to learn yet another draw tool that makes you and your team's life difficult.
8. And since we're here on GitHub, wouldn't it be nice if all of your models were under proper configuration management where you and your team can diff and merge to your heart's content? Wouldn't it be nice to update a diagram layout without touching the underlying model (and vice versa)?

Basically, I have wasted way too many hours of my career pushing pixels around and I just couldn't take it anymore!

Flatland is a model diagram non-editor written by me [Leon Starr](mailto:leon_starr@modelint.com) that generates
beautiful PDFs (and other output formats) based on two very
human-readable input text files. The model file specifies model semantics
(state transitions, generalizations, classes etc)
while the layout file specifies (node placement and alignment, connector anchors) and lightly refers to some elements
in the model file. You can think of the layout file as a "style sheet" for your models.
Some benefits:

Follow me on BlueSky and [LinkedIn](https://linkedin.com/in/modelint) for updates.

## Models to Code

In the meantime, if you are curious about the whole MBSE thing that this tool supports, take a look at our [book](https://modelstocode.com).
Also, various resources at the [Model Integration](https://modelint.com/mbse) website.

## Installation

Flatland is a command-line program published on PyPI as **`mi-flatland`**. You install it once into
an isolated Python *virtual environment* and then run it with the `flatland` command. The steps below
assume no prior Python experience — if you're already comfortable with Python, just run the commands in
the code blocks and skip the explanations.

### What you'll need

- **Python 3.11 or 3.12.** (Python 3.13 and newer are not yet supported.)
- macOS, Linux, or Windows.

### 1. Install Python

If you don't already have a supported version, download Python 3.12 from
[python.org](https://www.python.org/downloads/) and run the installer for your platform. Any install
method is fine (the official installer, Homebrew, etc.) as long as the version is 3.11 or 3.12. Having
other Python versions already on your machine is not a problem.

Confirm it's available:

```
python3 --version
```

You should see something like `Python 3.12.7`. (On Windows the command is usually `py --version`.)

### 2. Create a virtual environment

A virtual environment is just a folder that holds a private copy of Python and the packages flatland
needs, kept separate from the rest of your system so nothing conflicts. Python has this built in — no
extra tools required. Create one (here named `flatland-env`, but you can call it anything):

**macOS / Linux**
```
python3 -m venv ~/flatland-env
```

**Windows (PowerShell)**
```
py -m venv $HOME\flatland-env
```

### 3. Activate the environment

Activating tells your terminal to use the environment you just created.

**macOS / Linux**
```
source ~/flatland-env/bin/activate
```

**Windows (PowerShell)**
```
& $HOME\flatland-env\Scripts\Activate.ps1
```

Your prompt now starts with `(flatland-env)`, which means it's active. **You'll need to run this
activate command again each time you open a new terminal** before using flatland.

### 4. Install flatland

```
pip install --upgrade pip
pip install mi-flatland
```

### 5. Check the version

```
flatland -V
```

This prints something like `Flatland version: 3.0.0`, confirming the install worked.

### 6. Generate your first diagram

Flatland ships with example models. Copy them into your current folder:

```
flatland -E
```

This creates an `examples/` directory. Move into the elevator example and generate a class diagram:

```
cd examples/elevator
flatland -m elevator.xcm -l elevator_xUML.mls -d elevator.pdf
```

That command supplies three things:

- `-m elevator.xcm` — the **model** file (`.xcm` = class model, `.xsm` = state-machine model)
- `-l elevator_xUML.mls` — the **layout** file (`.mls`), which positions everything
- `-d elevator.pdf` — the **output** file to generate

**The extension you give to `-d` selects the output format.** Use `.pdf` for PDF or `.svg` for SVG —
so the same model and layout produce an SVG just by changing the name:

```
flatland -m elevator.xcm -l elevator_xUML.mls -d elevator.svg
```

A layout file refers to specific model content, so each `.mls` only works with its matching model. A
single model can have several layouts (e.g. `elevator_xUML.mls` and `elevator_Starr.mls` here), grouped
together so you can tell which files belong with which.

Run `flatland -h` to see every option (grid overlay, rulers, no-color, and more).

### Where your settings live

The first time you run flatland it creates two folders of YAML configuration files under your home
directory at `~/.config`:

- **`flatland`** — layout, title-block, and positional parameters.
- **`mi_tablet`** — graphics and text styles, plus any logos or other media.

You can browse and edit these (each file has explanatory comments), but edit carefully. If anything
breaks, just delete the folder and flatland will recreate the defaults on its next run.

### Coming back later

Whenever you open a new terminal, re-activate the environment (step 3) before running `flatland`.
Prefer not to activate every time? Installing with [pipx](https://pipx.pypa.io)
(`pipx install mi-flatland`) puts the `flatland` command on your PATH globally while keeping it
isolated.