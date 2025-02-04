"""Test cases based on gNMI Set/Get requests."""

import json

from oc_config_validate import schema, target, testbase


class TestCase(testbase.TestCase):
    """Sends gNMI Set and later Get.

    Args:
        xpath: gNMI path to write and read.
        json_value: JSON-IETF value to check, set and get.
        model: Python binding class to check the JSON reply against.
    """
    xpath = ""
    json_value = None
    model = ""

    def test0000(self):
        """Check testcase arguments."""
        self.assertArgs(["xpath", "json_value", "model"])
        self.assertXpath(self.xpath)
        self.assertIsInstance(self.json_value, dict,
                              "The value is not a valid JSON object")
        self.assertModelXpath(self.model, self.xpath)
        model = schema.ocContainerFromPath(self.model, self.xpath)
        self.assertJsonModel(json.dumps(self.json_value), model,
                             "JSON value to Set does not match the model")


class JsonCheck(TestCase):
    """Sends gNMI Set and later Get, schema-checking the JSON-IETF value.

    1. The intended JSON-IETF configuration is checked for schema validity.
    1. It is sent in a gNMI Set request.
    1. The same path is used for a gNMI Get request.
    1. The returned value is checked for schema validity

    All arguments are read from the Test YAML description.

    Args:
        xpath: gNMI path to write and read.
        json_value: JSON-IETF value to check, set and get.
        model: Python binding class to check the JSON reply against.
    """
    resp_val = None

    def test0100(self):
        """"""
        self.assertTrue(self.gNMISetUpdate(self.xpath, self.json_value),
                        "gNMI Set did not succeed.")

    @testbase.retryAssertionError
    def test0200(self):
        """"""
        resp = self.gNMIGet(self.xpath)
        self.assertIsNotNone(resp, "No gNMI GET response")
        self.resp_val = resp.json_ietf_val
        self.assertIsNotNone(self.resp_val,
                             "The gNMI GET response is not JSON IETF")
        model = schema.ocContainerFromPath(self.model, self.xpath)
        self.assertJsonModel(self.resp_val, model,
                             "Get response JSON does not match the model")


class JsonCheckCompare(JsonCheck):
    """Does what setget.JsonCheck does, but also compares the JSON Get reply.

    1. The intended JSON-IETF configuration is checked for schema validity.
    1. It is sent in a gNMI Set request.
    1. The same path is used for a gNMI Get request.
    1. The returned value is checked for schema validity
    1. The returned value is compared with the sent value

    All arguments are read from the Test YAML description.

    Args:
        xpath: gNMI path to write and read.
        json_value: JSON-IETF value to check set, get and compare.
        model: Python binding class to check the JSON reply against.
    """

    @testbase.retryAssertionError
    def test0300(self):
        """"""
        resp = self.gNMIGet(self.xpath)
        self.assertIsNotNone(resp, "No gNMI GET response")
        self.resp_val = resp.json_ietf_val
        self.assertIsNotNone(self.resp_val,
                             "The gNMI GET response is not JSON IETF")
        got = json.loads(self.resp_val)
        cmp, diff = target.intersectCmp(self.json_value, got)
        self.assertTrue(cmp, diff)
