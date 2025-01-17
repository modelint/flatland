"""
Flatland Diagram Editor

"""
# System
import logging
import logging.config
import sys
import atexit
import argparse
from pathlib import Path

# Flatland
from flatland.xuml.xuml_classdiagram import XumlClassDiagram
from flatland.xuml.xuml_statemachine_diagram import XumlStateMachineDiagram
from flatland.database.flatland_db import FlatlandDB
from flatland import version

_logpath = Path("flatland.log")

def clean_up():
    """Normal and exception exit activities"""
    _logpath.unlink(missing_ok=True)

def get_logger():
    """Initiate the logger"""
    log_conf_path = Path(__file__).parent / 'log.conf'  # Logging configuration is in this file
    logging.config.fileConfig(fname=log_conf_path, disable_existing_loggers=False)
    return logging.getLogger(__name__)  # Create a logger for this module

# Configure the expected parameters and actions for the argparse module
def parse(cl_input):
    parser = argparse.ArgumentParser(description='Flatland model diagram generator')
    parser.add_argument('-m', '--model', action='store',
                        help='xuml model file name defining model connectivity without any layout information')
    parser.add_argument('-l', '--layout', action='store',
                        help='Flatland layout file defining all layout information with light\
                         references to model file.')
    parser.add_argument('-d', '--diagram', action='store', default='diagram.pdf',
                        help='Name of file to generate, .pdf extension automatically added')
    parser.add_argument('-CF', '--configuration', action='store_true',
                        help="Create a new configuration directory in user's flatland home")
    parser.add_argument('-E', '--examples', action='store_true',
                        help='Create a directory of examples in the current directory')
    parser.add_argument('-L', '--log', action='store_true',
                        help='Generate a diagnostic flatland.log file')
    parser.add_argument('-N', '--nodes_only', action='store_true',
                        help='Do not draw any connectors. Helpful to diagnose connector failures due\
                         to bad node cplace.')
    parser.add_argument('-NC', '--no_color', action='store_true',
                        help='Use white instead of the specified sheet color. Useful when creating printer output.'),
    parser.add_argument('-V', '--version', action='store_true',
                        help='Print the current version of flatland')
    parser.add_argument('-G', '--grid', action='store_true',
                        help='Print the grid so you can diagnose output with row and column boundaries visible')
    parser.add_argument('-RT', '--show_ref_types', action='store_true',
                        help='Display referential attribute types on class diagrams')
    parser.add_argument('-RUL', '--rulers', action='store_true',
                        help='Print the ruler grid so you check canvas positions')
    parser.add_argument('-R', '--rebuild', action='store_true',
                        help='Rebuild the flatland database. Necessary only if corrupted.')
    parser.add_argument('-X', '--debug', action='store_true',
                        help='Debug mode -- outputs db and diagnostics to stdout')
    return parser.parse_args(cl_input)


def main():
    # Start logging
    logger = get_logger()
    logger.info(f'Flatland version: {version}')

    # Keep track of whether or not Config has been run by some command line option so we don't re-run it
    already_configured = False

    # Parse the command line args
    args = parse(sys.argv[1:])

    if not args.log:
        # If no log file is requested, remove the log file before termination
        atexit.register(clean_up)

    if args.version:
        # Just print the version and quit
        print(f'Flatland version: {version}')

    if args.examples:
        # Copy the entire example directory into the users local dir if it does not already exist
        import shutil
        ex_path = Path(__file__).parent / 'examples'
        local_ex_path = Path.cwd() / 'examples'
        if local_ex_path.exists():
            logger.warning("Examples already exist in the current directory. Delete or move it if you want the latest.")
        else:
            logger.info("Copying example directory into user's local directory")
            shutil.copytree(ex_path, local_ex_path)  # Copy the example directory

    if args.examples or args.version:
        # Don't require diagram generation args if user is requesting information
        # Just quit here
        sys.exit(0)

    # User is not requesting information, so they must be trying to generate a diagram
    # Ensure the necessary args are supplied
    if args.model and not args.layout:
        logger.error("A layout file must be specified for your model.")
        sys.exit(1)

    if args.layout and not args.model:
        logger.error("A model file must be specified to layout.")
        sys.exit(1)

    # At this point we either have both model and layout or neither
    # If neither, the only thing we might do at this point is rebuild the database if requested

    # Do any configuration tasks necessary before starting up the app
    # The database will be rebuilt if requested
    if not already_configured:
        FlatlandDB.create_db(debug=args.debug, rebuild=args.rebuild)

    # if args.model and args.layout:  # Just making sure we have them both
        model_path = Path(args.model)
        layout_path = Path(args.layout)
        diagram_path = Path(args.diagram)

        # Generate the xuml class diagram (we don't do anything with the returned variable yet)
        mtype = model_path.suffix
        if mtype == '.xcm':
            XumlClassDiagram(
                xuml_model_path=model_path,
                flatland_layout_path=layout_path,
                diagram_file_path=diagram_path,
                show_grid=args.grid,
                nodes_only=args.nodes_only,
                no_color=args.no_color,
                show_rulers=args.rulers,
                show_ref_types=args.show_ref_types
            )
        elif mtype == '.xsm':
            statemodel_diagram = XumlStateMachineDiagram(
                xuml_model_path=model_path,
                flatland_layout_path=layout_path,
                diagram_file_path=diagram_path,
                show_grid=args.grid,
                nodes_only=args.nodes_only,
                show_rulers=args.rulers,
                no_color=args.no_color,
            )

    logger.info("No problemo")  # We didn't die on an exception, basically
    if args.debug:
        print("No problemo")


if __name__ == "__main__":
    main()
