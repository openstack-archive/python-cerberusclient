#
#   Copyright (c) 2015 EUROGICIEL
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

from cerberusclient.common import http
from cerberusclient.v1 import plugins
from cerberusclient.v1 import security_alarms
from cerberusclient.v1 import security_reports
from cerberusclient.v1 import tasks


class Client(http.HTTPClient):
    """Client for the Cerberus v1 API.

    :param string endpoint: A user-supplied endpoint URL for the service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Cerberus v1 API."""
        super(Client, self).__init__(*args, **kwargs)
        self.plugins = plugins.PluginManager(self)
        self.tasks = tasks.TaskManager(self)
        self.security_reports = security_reports.SecurityReportManager(self)
        self.security_alarms = security_alarms.SecurityAlarmManager(self)
