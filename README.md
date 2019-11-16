# jboss_call_api

## Description
Converts JBOSS CLI command line arguments to JBOSS API calls

## Purpose
JBOSS commands given directly to the JBOSS CLI are time consuming, taking on average about 3.5 seconds per simple read operation
The CLI is essentially a wrapper for API calls to the JBOSS API. Using this tool will skip the CLI directly and make
the calls to the JBOSS API which takes on average just over 100ms per read operation.

## Usage
./jboss_api.py 'jboss cli command'
Example1: ./jboss_api.py ':read-operation-description(name=whoami)'

## Future
The original goal of writing this was to use this as a python module for use with an Ansible JBOSS module. Providing
idempotency through Ansible was the goal I was going to strive for when writing the Ansible module. As is, the script
works well when used non-interactively as part of a BASH script, or called directly from Ansible shell module for
read-write operations. Used in conjunction with Ansible conditionals can be used to execute queries before making
uneccesary changes, or simply called outright. 
