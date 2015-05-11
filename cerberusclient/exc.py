#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import json


class HTTPException(BaseException):
    """Base exception for all HTTP-derived exceptions."""
    code = 'N/A'

    def __init__(self, details=None):
        self.details = details

    def __str__(self):
        try:
            data = json.loads(self.details)
            message = data.get("error_message", {}).get("faultstring")
            if message:
                return "%s (HTTP %s) ERROR %s" % (
                    self.__class__.__name__, self.code, message)
        except (ValueError, TypeError, AttributeError):
            pass
        return "%s (HTTP %s)" % (self.__class__.__name__, self.code)


class HTTPNotFound(HTTPException):
    code = 404
