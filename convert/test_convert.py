import unittest
from convert import jboss_command_to_http_request


class TestJBOSSCommandToHTTPGETRequestOperationOnlyTestCase(unittest.TestCase):
    """Test case for JBOSS CLI commands operation only commands using HTTP GET"""

    def test_no_path_one_operations_no_params_http_get(self):
        """See if we only operations without params return correctly using HTTP GET"""

        test_data = ':read-resource'
        desired_operation = {"operation": "resource"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_empty_params_http_get(self):
        """See if only operations with empty params return correctly using HTTP GET"""

        test_data = ':read-resource()'
        desired_operation = {"operation": "resource"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_single_param_http_get(self):
        """ See if only operations with single parameter return correctly using HTTP GET"""

        test_data = ':read-resource(attributes-only=true)'
        desired_operation = {"operation": "resource", "attributes-only": "true"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_multiple_params_http_get(self):
        """See if only operations with multiple params return correctly using HTTP GET"""

        test_data = ':read-attribute(include-defaults=true,name=uuid)'
        desired_operation = {"operation": "attribute", "include-defaults": "true", "name": "uuid"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)


class TestJBOSSCommandToHTTPPOSTRequestOperationOnlyTestCase(unittest.TestCase):
    """Test case for JBOSS CLI commands operation only commands using HTTP POST"""

    def test_no_path_one_operations_no_params_http_post(self):
        """See if we only operations without params return correctly using HTTP POST"""

        test_data = ':read-resource'
        desired_operation = {"operation": "read-resource"}
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_empty_params_http_post(self):
        """See if only operations with empty params return correctly using HTTP POST"""

        test_data = ':read-resource()'
        desired_operation = {"operation": "read-resource"}
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_single_param_http_post(self):
        """See if only operations with single parameter return correctly using HTTP POST"""

        test_data = ':read-attribute(name=server-state)'
        desired_operation = {"operation": "read-attribute", "name": "server-state"}
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_no_path_only_operations_multiple_params_http_post(self):
        """See if only operations with multiple params return correctly using HTTP POST"""

        test_data = ':read-operation-description(name=whoami,access-control=true)'
        desired_operation = {"operation": "read-operation-description", "name": "whoami", "access-control": "true"}
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)


class TTestJBOSSCommandToHTTPGETRequestTestCase(unittest.TestCase):
    """Test case for for convert.jboss_command_to_http_request"""

    def test_single_path_and_operation_no_params_http_get(self):
        """See if command with path and operation returns correctly using HTTP GET"""

        test_data = '/subsystem=undertow:read-resource'
        desired_operation = {"operation": "resource", "address": "/subsystem/undertow"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_single_path_and_operation_single_param_http_get(self):
        """See if command with path, operation, and single param return correctly using HTTP GET"""

        test_data = '/subsystem=undertow:read-attribute(resolve-expressions=true)'
        desired_operation = {
            "operation": "attribute", "resolve-expressions": "true", "address": "/subsystem/undertow"
        }
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_single_path_and_operation_multiple_params_http_get(self):
        """See if command with path, operation, and multiple params return correctlty using HTTP GET"""

        test_data = '/subsystem=undertow:read-attribute(resolve-expressions=true,name=instance-id)'
        desired_operation = {
            "operation": "attribute", "resolve-expressions": "true", "name": "instance-id",
            "address": "/subsystem/undertow"
        }
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_no_params_http_get(self):
        """See if command with path, operation, and single param return correctly using HTTP GET"""

        test_data = '/subsystem=undertow/server=default-server:read-resource'
        desired_operation = {"operation": "resource", "address": "/subsystem/undertow/server/default-server"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_empty_params_http_get(self):
        """See if command with path, operation, and single param return correctly using HTTP GET"""

        test_data = '/subsystem=undertow/server=default-server:read-resource()'
        desired_operation = {"operation": "resource", "address": "/subsystem/undertow/server/default-server"}
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_single_param_http_get(self):
        """See if command with path, operation, and single param return correctly using HTTP GET"""

        test_data = '/subsystem=undertow/server=default-server:read-attribute(name=default-host)'
        desired_operation = {
            "operation": "attribute", "name": "default-host",
            "address": "/subsystem/undertow/server/default-server"
        }
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_multiple_param_http_get(self):
        """See if command with multiple pathresult, operation, and multiple param return correctly using HTTP GET"""

        test_data = '/subsystem=undertow/server=default-server:read-attribute(resolve-expressions=true,include-defaults=true,name=servlet-container)'
        desired_operation = {
            "operation": "attribute", "resolve-expressions": "true", "include-defaults": "true",
            "name": "servlet-container", "address": "/subsystem/undertow/server/default-server"
        }
        result = jboss_command_to_http_request(test_data, "GET")
        self.assertEqual(result, desired_operation)


class TestJBOSSCommandToHTTPPOSTRequestTestCase(unittest.TestCase):
    """Test case for for convert.jboss_command_to_http_request"""

    def test_single_path_and_operation_no_params_http_post(self):
        """See if command with path and operation returns correctly using HTTP POST"""

        test_data = '/core-service=management:whoami'
        desired_operation = {"operation": "whoami", "address": ["core-service", "management"]}
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_single_path_and_operation_single_param_http_post(self):
        """See if command with path, operation, and single param return correctly using HTTP POST"""

        test_data = '/core-service=server-environment:path-info(unit=GIGABYTES)'
        desired_operation = {
            "operation": "path-info", "unit": "GIGABYTES",
            "address": ["core-service", "server-environment"]
        }
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_single_path_and_operation_multiple_params_http_post(self):
        """See if command with path, operation, and multiple params return correctly using HTTP POST"""

        test_data = '/subsystem=undertow:write-attribute(name=statistics-enabled,value=true)'
        desired_operation = {
            "operation": "write-attribute", "name": "statistics-enabled", "value": "true",
            "address": ["subsystem", "undertow"]
        }
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_no_params_http_post(self):
        """See if command with multiple pathresult, operation, and single param return correctly using HTTP POST"""

        test_data = "/subsystem=datasources/data-source=ExampleDS:dump-queued-threads-in-pool()"
        desired_operation = {
            "operation": "dump-queued-threads-in-pool",
            "address": ["subsystem", "datasources", "data-source", "ExampleDS"]
        }
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_single_param_http_post(self):
        """See if command with multiple pathresult, operation, and single param return correctly using HTTP POST"""
        test_data = "/core-service=management/service=configuration-changes:add(max-history=200)"
        desired_operation = {
            "operation": "add", "max-history": "200",
            "address": ["core-service", "management", "service", "configuration-changes"]
        }
        result = jboss_command_to_http_request(test_data, desired_operation)
        self.assertEqual(result, desired_operation)

    def test_multiple_path_and_operation_multiple_param_http_post(self):
        """See if command with multiple pathresult, operation, and multiple params return correctly using HTTP POST"""

        test_data = "/subsystem=datasources/data-source=ExampleDS:write-attribute(name=max-pool-size,value=5000)"
        desired_operation = {
            "operation": "write-attribute", "name": "max-pool-size", "value": "5000",
            "address": ["subsystem", "datasources", "data-source", "ExampleDS"]
        }
        result = jboss_command_to_http_request(test_data, "POST")
        self.assertEqual(result, desired_operation)


if __name__ == '__main__':
    unittest.main()
