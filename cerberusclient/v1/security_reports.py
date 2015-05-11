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

from cerberusclient.common import base
from cerberusclient.v1 import base as v1_base


class SecurityReport(base.Resource):
    def __repr__(self):
        return "<SecurityReport %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class SecurityReportManager(v1_base.BaseManager):
    resource_class = SecurityReport

    def __init__(self, api):
        super(SecurityReportManager, self).__init__(api)
        self.url = self.url_prefix + '/security_reports'

    def list(self):
        return self._list(self.url, 'security_reports')

    def get(self, report_id):

        return self._get(self.url + '/{id}'.format(id=report_id))

    def put(self, report_id, ticket_id):
        return self._update(self.url + '/{id}'.format(id=report_id) +
                            '/tickets/' + '{ticket_id}'.format(
            ticket_id=ticket_id))
