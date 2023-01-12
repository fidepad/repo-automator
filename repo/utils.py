import logging

import requests
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MakeRequest:
    """This class handles all requests I make with exception handling."""

    def __init__(self, url, headers=None):
        if headers is None:
            headers = {}

        self.url = url
        self.headers = headers

    def get(self, url=None):
        """This makes a get requests."""
        response = {}
        if not url:
            url = self.url
        try:
            response = requests.get(url, headers=self.headers, timeout=300)
        except (RequestException, requests.Timeout) as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response

    def post(self, data, json=False, url=None):
        """This handles the post requests."""
        response = {}
        if not url:
            url = self.url
        try:
            if json:
                response = requests.post(
                    url, json=data, headers=self.headers, timeout=300
                )
            else:
                response = requests.post(
                    url, data=data, headers=self.headers, timeout=300
                )
        except (RequestException, requests.Timeout) as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response

    def put(self, data, json=False, url=None):
        """This handles the put requests."""
        response = {}
        if not url:
            url = self.url
        try:
            if json:
                response = requests.put(
                    url, json=data, headers=self.headers, timeout=300
                )
            else:
                response = requests.put(
                    url, data=data, headers=self.headers, timeout=300
                )
        except (RequestException, requests.Timeout) as err:
            logger.exception(err)
            response["data"] = {"error": str(err)}
        finally:
            return response
