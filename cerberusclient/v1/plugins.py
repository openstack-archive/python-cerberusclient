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

import base as v1_base
from cerberusclient.common import base


class Plugin(base.Resource):
    def __repr__(self):
        return "<Plugin %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class PluginManager(v1_base.BaseManager):
    resource_class = Plugin

    def __init__(self, api):
        super(PluginManager, self).__init__(api)
        self.url = self.url_prefix + '/plugins'

    def list(self):
        return self._list(self.url, 'plugins')

    def get(self, plugin_id):
        return self._get(self.url + '/{uuid}'.format(uuid=plugin_id))
