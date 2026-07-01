# Flatland Model Diagram Generator

### June 29, 2026 -- 3.0 Released with SVG and PDF Diagram Output

Flatland generates beautiful, readable model diagrams from plain text — laid out exactly the way you
want, without pushing a single pixel.

You write two text files for each diagram:

- a **model file** that captures only the semantics — classes, states, transitions, generalizations, and so on, and
- a **layout file** that describes how to arrange those elements on the page.

Flatland combines them to produce **SVG or PDF**. Want to change the layout? Edit the layout file. Want
to change the model? Edit the model, and adjust the layout only if you need to. Because the two are
separate, a version-control diff tells you immediately whether a change touched the model itself or
merely its presentation.

Layout is specified with a single, simple row-and-column markup — a kind of spreadsheet for your
diagram — that works across every model type. No pixel coordinates, no fragile alignment or stacking
rules. You get precise control with a minimum of specification.

I built Flatland after years of frustration with the two usual options: wrestling the wonky GUI of a
monolithic modeling tool (good luck maintaining and version-controlling a large model set), or
accepting the minimal layout control of text-based tools like PlantUML. Flatland gives you the
text-first workflow *and* the layout you actually want.

### Benefits

- **Model and layout stay fully separate.** Edit one without disturbing the other, and diff your models
  with the layout excluded to see whether the meaning changed or just the picture.
- **Precise layout, minimal specification.** A spreadsheet-style row/column markup places nodes,
  connectors, and text exactly where you want them — no pixel pushing, no carpal tunnel.
- **One layout language for every model type.** If your model can be expressed as nodes and labeled
  connectors — most can — the same markup applies.
- **Built for industrial-scale models.** Stays consistent and readable across hundreds or thousands of
  model elements.
- **Text-first and toolchain-friendly.** Use your favorite editor and IDE, and put your models under
  proper configuration management — diff, branch, and merge like any other source.
- **AI-ready.** Feed a model alone for lean, low-token prompting and code generation, or hand the AI an
  SVG to refine the layout by updating the markup. (UML / SysML v2 standards support is easily added.)
- **Beautiful output in multiple formats.** SVG and PDF today, with more to come.

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