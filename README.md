# jboss_call_api

##Description
Covert JBOSS CLI commands given as command line arguments to JBOSS API calls

##Purpose
JBOSS commands given directly to the JBOSS cli are time consuming, taking on average about 3.5 seconds per simple read operation
Using this tool will skip the CLI directly and make the calls to the JBOSS API which takes on average just over 100ms per read operation.

##Usage
./jboss_api.py 'jboss cli command'
Example1: ./jboss_api.py ':read-operation-description(name=whoami)'

##Future
The original goal of writing this was to use this as a python module for use with an Ansible JBOSS module. Providing true idempotency through Ansible was the goal I was going to strive for when writing the Ansible module. As is, the script works well when used non-interactively as part of a BASH script, or called directly from Ansible for read-write operations relying on returns from queries to check before making uneccesary changes, resulting in a user-configurable idempotency. 
