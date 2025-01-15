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

If you are already a pythonista, you can skim these instructions quickly. But I am writing for
those of you who might not be.

And for today (25-1-14) I have only tested this on my MacBook Pro / M2 Max / Sequoia
A minor adjustment or two may be required for success on Linux and Windows, and I am happy to help you out with that
if you contact me. If you are adept with your platform, I could use the help testing installation.

### Summary

1. Install Python 3.12 on your machine (you might be okay with an earlier version, but all bets are off)
2. Set up a virtual environment so your path variables, python version, etc are all correct for this installation
3. Activate that environment so the settings take effect
4. Install flatland
5. Check version
6. Generate a diagram from an example file
7. For future usage, be sure your environment is activated, or update your shell path environment as necessary

### Details

#### [1] Install Python
Go to https://www.python.org and follow instructions to download Python 3.12 for your machine. It's okay if you already have other versions of Python on your machine. If you have some other way of installing Python on your machine like homebrew that's fine, just get the version right.

#### [2] Set up a virtual environment (venv)
Select or create a directory somewhere as the destination of the virutal environment you are about to create. Here's what I did on my machine:
```
[841] /starr/SDEV/Environments
[842] cd User
[843] ls
[844] python -V
Python 3.12.7
[845] python -m pip install --user --upgrade pip
[notice] A new release of pip is available: 24.2 -> 24.3.1
[notice] To update, run: pip3 install --upgrade pip
[846] pip3 install --upgrade pip
```
Your interaction will be different than above, but I verified that I had the right
Python and ensured that the package installer pip, was up to date and ready for action.
On to the virtual environment setup...
```
[847] python -m pip install --user virtualenv
```
You'll get a lot of diagnstic stuff, but the final line should be something like:
```
Successfully installed distlib-0.3.9 filelock-3.16.1 platformdirs-4.3.6 virtualenv-20.28.1
```
#### [3] Activate the venv
Now I have the venv module available which I can use to create my virtual environment (venv)
```
[848] pwd
/Users/starr/SDEV/Environments/User
[849] python -m venv flatland
```
Above, the name `flatland` is not actually flatland, but the name of the environment that I am creating for it. You could name it anything like `F1` or `flatland_env` if you like.

Now I activate the environment:
```
[850] source flatland/bin/activate
(flatland) [851]
```
Remember that command above, you'll need it whenever you open a terminal window and want to set your environment up to use flatland. You know you've succeeded because it prefixes your shell prompt with the name of the venv while active.

#### [4] Install flatland

Finally! We can install flatland into our environment.
```
(flatland) [851] pip install mi-flatland
```
Okay, now you can go to any directory you want, say your home directory and try it out.
I created an empty directory `Ftest` in my home directory earlier, so I go there and
check to see if flatland will show me it's version.

#### [5] Check version
```
(flatland) [852] cd ~/Ftest
(flatland) [853] flatland -V
(flatland) [914] flatland -V
Flatland version: 2.0.2
(flatland) [915] 
```

#### [6] Generate a diagram
Note: I will write instructions later about how you can get the sample files I am using, but I'll just show you what happens for now.

Initially we see one executable class model (xcm) file and two 
model layout sheet (mls) files.
```
(flatland) [915] ls
elevator.xcm      elevator_xUML.mls    elevator_Starr.mls
```
Now we choose the xUML layout and generate a class diagram.
```
(flatland) [915] flatland -m elevator.xcm -l elevator_xUML.mls -d elevator_cd.pdf
(flatland) [917] ls
elevator.xcm      elevator_xUML.mls     elevator_Starr.mls   elevator_cd.pdf
```
What we did there was supply a model file *.xcm with the -m arg, a layout file *.mls with the -l arg, and the name of the diagram file we wanted to generate, elevator_cd.pdf with the -d arg.

#### [6a]
To get those example files, you can request them like so:
```
(flatland) [918] flatland -E
(flatland) [919] ls
examples
```
This copies the flatland examples directory into your current working directory. In there
you will find a variety of example models and layouts. Note that a given layout file
references model content, so you can only use it with a specific model file.

But you CAN define multiple layouts for the same model. They will be grouped together in subfolders in the examples directory so that you can easily tell which models and layouts can be used together.

By the way, if you are on Mac OS, you will see two directories of YAML configuration files in your $HOME/.config folder named 'flatland' and 'mi_tablet'. Graphics and text style options along with any organization specific logos and other media resources are in the mi_tablet directory and 
a variety of positional, layout, titleblock and other parameters are in the flatland directory.  You might want to browse through those, but careful if you edit them.  If you mess up, don't worry, just delete the directories and the next time you run flatland it will refresh them. Detailed instructions will be available on the wiki eventually, but you can read the comments in each YAML file for now for guidance.

And there you have it.  See the project wiki for all the various command args you can supply and how to edit layout files and the various types of supported model files.