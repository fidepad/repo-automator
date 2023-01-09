import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MakeRequest:
    """This class handles all requests I make with exception handling."""

    def __init__(self, url, data=None, headers=None, json=False):
        if headers is None:
            headers = {}

        self.url = url
        self.data = None
        self.headers = headers
        self.json = json

    def get(self):
        """This makes a get requests."""
        response = {}
        try:
            response = requests.get(self.url, headers=self.headers)
        except [ConnectionError, requests.Timeout] as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response

    def post(self):
        """This handles the post requests."""
        response = {}
        try:
            if self.json:
                response = requests.post(self.url, json=self.data, headers=self.headers)
            else:
                response = requests.post(self.url, data=self.data, headers=self.headers)
        except [ConnectionError, requests.Timeout] as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response

    def put(self):
        """This handles the put requests."""
        response = {}
        try:
            if self.json:
                response = requests.put(self.url, json=self.data, headers=self.headers)
            else:
                response = requests.put(self.url, data=self.data, headers=self.headers)
        except [ConnectionError, requests.Timeout] as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response
