import re
import sys
import logging

RECOVERABLE_ERROR = 1

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO)


class Error(Exception):
    """Base class for exception"""
    pass


class NoOperationFound(Error):
    """Raised when an operation not found in CLI command"""

    def __init__(self, expression):
        self.expression = expression
        print(f'Error: Unable to find operation in command: ({expression}) - '
              'Operations should be prepended with a single colon. Eg. (:reload)')
        sys.exit(RECOVERABLE_ERROR)


class TooManyOperations(Error):
    """Too many operations found in command"""

    def __init__(self, expression):
        self.expression = expression
        logging.error(f'Too many operations found in ({expression}) - '
                      'Only a single operation should be defined. E.g (:read-resource)')
        sys.exit(RECOVERABLE_ERROR)


def jboss_command_to_http_request(cli_call, request_type):
    """Returns a mostly structured format suitable for JBOSS API calls

    Parses the CLI command and the HTTP request method we are using and formats them into a variable more suitable
    for JBOSS API requests with the formatting used for the HTTP request type

    Parameters
    ----------
    cli_call : str
        The JBOSS CLI command to be executed
    request_type : str
        The HTTP request type: [GET, POST]

    Returns
    -------
    list:
        A list with 1 or 2 elements.
        If the request HTTP method is GET, it will be 2 elements
        [0] A dictionary of the operation, [1] A string for the resource path
        If the request HTTP methos is POST, it will be a single element
        [0] A single element of type dict with the full operation and resource path
    """

    logging.debug(f'Full CLI call: {cli_call}')
    logging.debug(f'Using HTTP Request: {request_type}')

    operation_no_args, path, args = None, None, None

    if cli_call.count(':') < 1:
        raise NoOperationFound(cli_call)

    elif cli_call.count(':') > 1:
        raise TooManyOperations(cli_call)

    elif cli_call.startswith(':'):
        # We received an operation command without a resource path, parse the operation and arguments
        logging.debug(f'Executing standalone operation')

        # Remove the precedeing : from the command. E.g :read-attribute becomes read-attribute
        cli_call = cli_call.split(':', 1)[1]
        operation_no_args, args = get_operation_and_args(cli_call, request_type)

    elif cli_call.startswith('/') and cli_call.count(':') == 1:
        # We received a CLI command that has both a resource path and operation
        logging.debug(f'We have a path and an operation defined')

        # The path should always precede the operation in JBOSS CLI if both are defined
        isolated_operation = cli_call.split(':')[1]
        isolated_path = cli_call.split(':')[0]

        operation_no_args, args = get_operation_and_args(isolated_operation, request_type)
        path = get_path_to_resource(isolated_path, request_type)

    else:
        sys.exit('Unknown command {cli_call}')

    if request_type == "GET":
        # Split off the first portion of the CLI operation as the URL path does not contain it
        # E.g: read-resource -> resource, list-snapshots -> snapshots
        operation_no_args = operation_no_args.split('-', 1)[1]

    logging.debug(f'Path: {path}')
    logging.debug(f'Operation: {operation_no_args}')
    logging.debug(f'Arguments: {args}')

    # Start to create the full API call we will be using
    api_call = {"operation": operation_no_args}

    # Append our arguments to our api call
    if args is not None:
        api_call = {**api_call, **args}

    # Append our path to our API call
    # The path will be a list of seperated elements when using HTTP POST and a string containing the partial
    # URI that we will append to the URL for HTTP GET methods. We extract the value if necessary when making
    # final URL during the HTTP request
    if path is not None:
        api_call = {**api_call, "address": path}

    logging.debug(f'API call being returned: {api_call}')

    return api_call


def get_operation_and_args(isolated_operation, request_type):
    """Returns the seperated operation and arguments from the JBOSS CLI command

    Take the JBOSS CLI command operation portion of the JBOSS CLI command and seperates the operation from
    the arguments passed inside the parenthesis. Returns both as seperate variables

    Parameters
    ----------
    isolated_operation: str
        The original CLI operation command split off from the resource path
    request_type: str
        HTTP method being used: [GET, POST]

    Returns
    -------
    operation_no_args: str
        The operation portion of the command without the arguments or parenthesis
    args: str
        The argument portion of the command without the parenthesis

    """

    # Regex for empty parameters inside operation parenthesis (designated as empty parameters)
    re_empty_args = re.compile(r'\(\)')
    # Regex for finding everything before the parenthesis (designated as operation with parameters)
    re_no_args = re.compile(r'^[^\(]+')
    # Regex to get only what is inside the parenthesis
    re_args = re.compile(r'\(([^)]+)\)')
    args = None

    if '(' not in isolated_operation:
        # There are no parameters being passed to the operation
        operation_no_args = isolated_operation

    elif re_empty_args.search(isolated_operation):
        # Found operation with empty parameters. E.g read-resource()
        # Grab the operation before the paraenthesis. E.g read-resource() becomes read-resource
        operation_no_args = re_no_args.search(isolated_operation)
        operation_no_args = operation_no_args.group(0)

    else:
        # We have parenthesis and arguments to the operation. E.g read-resource(name=default)
        operation_no_args = re_no_args.search(isolated_operation)
        operation_no_args = operation_no_args.group(0)
        # Grab everything inside the parenthesis
        arguments = re_args.search(isolated_operation)
        arguments = arguments.group(1)

        # Convert arguments string into key value pairs into dictionary
        # This only works if they are properly defined in the arguments
        # E.g name=system,value=default which becomes { name:system, value:default}
        args = dict(item.split("=") for item in arguments.split(','))

    logging.debug(f'Found operation: {operation_no_args}')
    logging.debug(f'Found arguments: {args}')

    return operation_no_args, args


def get_path_to_resource(isolated_path, request_type):
    """Returns a modified CLI path to resource suitable for API requests

    Returns a list if HTTP POST is being used
    Returns a str if HTTP GET is being used

    Parameters
    ----------
    isolated_path : str
        Path seperated from the operation component of the original CLI command
    request_type: str
        Specifies what type of HTTP operation we are doing: [GET, POST]

    Returns
    -------
    str: if we are doing HTTP GET
        Formatted string for use in URL
    list: if we are doing HTTP POST
        List of the path broken into individual elements

    """

    # Take a resource path such as /subsystem=undertow/server=default-server
    # and turn it into path = [http://url] /subsystem/undertow/server/default-server suitable URL for HTTP GET
    if request_type == "GET":
        path = isolated_path.replace('=', '/')

    else:
        # Split the path into a list of its independent segments suitable for HTTP POST request
        # Ex: /subsystem=undertow/server=default-server becomes ["subsystem","undertow","server","default-server"]
        path = re.split(r'/|=', isolated_path)

        # Remove the empty string from beginning of path because splitting the fist / gives an empty string
        path = list(filter(None, path))

    logging.debug(f'Original full path: {isolated_path}')
    logging.debug(f'Modified return path: {path}')

    return path
