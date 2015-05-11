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


class Task(base.Resource):
    def __repr__(self):
        return "<Task %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class TaskManager(v1_base.BaseManager):
    resource_class = Task

    def __init__(self, api):
        super(TaskManager, self).__init__(api)
        self.url = self.url_prefix + '/tasks'

    def list(self):
        return self._list(self.url, 'tasks')

    def get(self, task_id):
        return self._get(self.url + '/{id}'.format(id=task_id))

    def create(self, plugin_id, method, name='unknown', type='unique',
               period=None, persistent='False'):
        data = {}
        data['method'] = method
        data['name'] = name
        data['type'] = type
        data['period'] = period
        data['plugin_id'] = plugin_id
        data['persistent'] = persistent
        return self._create(self.url,
                            data=data)

    def stop(self, task_id):
        return self._act(self.url + '/{id}'.format(id=task_id)
                         + '/action/stop',
                         {})

    def delete(self, task_id):
        return self._delete(self.url + '/{id}'.format(id=task_id))

    def force_delete(self, task_id):
        return self._act(self.url + '/{id}'.format(id=task_id)
                         + '/action/force_delete',
                         {})

    def restart(self, task_id):
        return self._act(self.url + '/{id}'.format(id=task_id)
                         + '/action/restart',
                         {})
