#!/usr/bin/env python3

"""
jboss_api.py
author: Mike Watkins

Convert JBOSS commands as command line arguments to JBOSS API calls and executes them against provided host/port
Proper configuration of config variables is required before executing
JBOSS_URL: URL to JBOSS server
JBOSS_PORT: Port JBOSS server is listening on
API_AUTH_USER: JBOSS user with appropraite permissions to make API calls
API_AUTH_PWD: Password for JBOSS API_AUTH_USER
USE_PRETTY_JSON: Results returned in pretty JSON
"""

import convert.convert as convert
import logging
import sys

RECOVERABLE_ERROR = 1

# User configurable variables
JBOSS_URL = 'http://localhost'
JBOSS_PORT = '9990'
API_AUTH_USER = ''
API_AUTH_PWD = ''
USE_PRETTY_JSON = False

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO)

try:
    import requests
    from requests.auth import HTTPDigestAuth
    from requests.exceptions import HTTPError

except ModuleNotFoundError:
    logging.error("Python [requests] module is required.")
    sys.exit(RECOVERABLE_ERROR)


def call_jboss_api(cli_command):
    """Makes a REST API call to the JBOSS maangement console

    Parameters
    ----------
    cli_command: str
        The JBOSS CLI command that we want to run

    """

    header = {'content-type': 'application/json'}

    # Determine if we are using HTTP GET or POST method
    request_type = get_request_type(cli_command)

    # Convert the JBOSS cli command to the appropriate API call
    api_call = convert.jboss_command_to_http_request(cli_command, request_type)

    # BUG: Use pretty JSON only works on POST methods, because of the way I have to reformat the JSON
    # when using GET method requests. This will not matter if I end up using this as an Ansible module
    # since I will just be returning the json data to the module
    if USE_PRETTY_JSON is True:
        api_call = {**api_call, "json.pretty": 1}

    response = None

    try:
        if request_type == "GET":
            # HACK: JBOSS REST API returns different data structure when using HTTP GET
            # It completely removes the { outcome: [outcome], results: [return] } and instead just returns [return]
            # This makes the output inconsistent and possibly breaking for scripting when used in combination
            # with HTTP POST requests. Therefore I am adding the return into the same data structure that POST
            # or a GET (500) failure returns

            # data structure returned from convert module sets the address for an HTTP GET method to a string
            # with the correct path to be added to the URL.
            api_path = ""
            if api_call.get("address"):
                api_path = api_call.pop("address")

            logging.debug(f'address after pop: {api_path}')
            logging.debug(f'path in pop: {api_path}')

            response = requests.get(
                url(JBOSS_URL, api_path),
                auth=HTTPDigestAuth(API_AUTH_USER, API_AUTH_PWD),
                params=api_call,
                headers=header
            )

            if response.status_code == 200:
                # HTTP GET response code 200 indicates returns json structure inconsistent with HTTP GET 500,
                # as well as HTTP POST 200,500. Normalizing the data structure in that event
                results = {"outcome": "success", "result": response.json()}

            # Response code 500 will output the correct data structure, only 200 returns inconsistently
            elif response.status_code == 500:
                results = response.json

        elif request_type == "POST":

            response = requests.post(
                url(JBOSS_URL),
                auth=HTTPDigestAuth(API_AUTH_USER, API_AUTH_PWD),
                json=api_call,
                headers=header
            )

            results = response.json()

        response.raise_for_status()

        logging.debug(response.status_code)
        print(results)

    except HTTPError as err:
        if err.response.status_code == 401:
            logging.error("Unauthorized Connection. Possible incorrect username/password")
            sys.exit(RECOVERABLE_ERROR)
        else:
            logging.error(f'HTTP Error occured: {err.response.text}')
    except Exception as err:
        logging.error(f'Other error occured: {err}')


def get_request_type(cli_command):
    """Determines the type of HTTP method to use based off of CLI command

    Wildfly 10+/JBOSS 7.x (and possibly earlier) supports these command operations as HTTP GET requests:
        read-attribute as attribute,
        read-resource as resource,
        read-resource-description as resource-description,
        list-snapshots as snapshots,
        # BUG: read-operation-description does not become -> operation-description,
        read-operation-names as operation-names

    Parameters
    ----------
    cli_command: str
        The JBOSS CLI command we are calling

    Returns
    -------
    request_type: str
        The HTTP request method we are going to use [GET, POST]

    """

    # Default to HTTP POST because we all JBOSS operations support a POST request
    request_type = "POST"

    # Suported operations for HTTP GET method requests
    supported_get_ops = [
        "read-attribute",  # as attribute
        "read-resource",  # as resource
        "read-resource-description",  # as resource-description
        "list-snapshots",  # as snapshots
        # "read-operation-description",  # as operation=operation-description
        "read-operation-names"  # as operation-names
    ]

    # If our CLI command is using one of the read-only HTTP GET operations supported by JBoss/Wildfly, use HTTP GET
    for operation in supported_get_ops:
        if operation in cli_command:
            request_type = "GET"

    return request_type


def url(url, api_path=""):
    """Return a structured URL for API calls"""

    return url + ":" + JBOSS_PORT + "/management" + api_path


if __name__ == '__main__':
    call_jboss_api(sys.argv[1])
