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

Notes here are for those familiar with python installation procedures.  I will write a more detailed set of procedures
for those who are not in a later release.

You should also ensure that you have Python 3.12+ installed. A virtual environment is highly recommended.

You can install the Flatland Model Diagram Editor from [PyPI](https://pypi.org/project/flatland-model-diagram-editor/):

    $ pip install mi-flatland

Flatland is supported on Python 3.12 and above

## How to use

At this point I refer you to the [wiki](https://github.com/modelint/flatland/wiki) on this site for all of the user documentation. Enjoy (and feel free to contact me if you have any questions.
