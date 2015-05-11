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

import copy
import logging
import socket

from oslo.serialization import jsonutils
from oslo.utils import encodeutils
import requests
import six

from cerberusclient.common import exceptions as exc

LOG = logging.getLogger(__name__)
USER_AGENT = 'python-cerberusclient'


class HTTPClient(object):

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.auth_url = kwargs.get('auth_url')
        self.auth_token = kwargs.get('token')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.region_name = kwargs.get('region_name')
        self.include_pass = kwargs.get('include_pass')
        self.endpoint_url = endpoint

        self.cert_file = kwargs.get('cert_file')
        self.key_file = kwargs.get('key_file')
        self.timeout = kwargs.get('timeout')

        self.ssl_connection_params = {
            'ca_file': kwargs.get('ca_file'),
            'cert_file': kwargs.get('cert_file'),
            'key_file': kwargs.get('key_file'),
            'insecure': kwargs.get('insecure'),
        }

        self.verify_cert = None

    def log_curl_request(self, method, url, kwargs):
        curl = ['curl -i -X %s' % method]

        for (key, value) in kwargs['headers'].items():
            header = '-H \'%s: %s\'' % (encodeutils.safe_decode(key),
                                        encodeutils.safe_decode(value))
            curl.append(header)

        conn_params_fmt = [
            ('key_file', '--key %s'),
            ('cert_file', '--cert %s'),
            ('ca_file', '--cacert %s'),
        ]
        for (key, fmt) in conn_params_fmt:
            value = self.ssl_connection_params.get(key)
            if value:
                curl.append(fmt % value)

        if self.ssl_connection_params.get('insecure'):
            curl.append('-k')

        if 'data' in kwargs:
            curl.append('-d \'%s\'' % kwargs['data'])

        curl.append('%s%s' % (self.endpoint, url))
        LOG.debug(' '.join(curl))

    @staticmethod
    def log_http_response(resp):
        status = (resp.raw.version / 10.0, resp.status_code, resp.reason)
        dump = ['\nHTTP/%.1f %s %s' % status]
        dump.extend(['%s: %s' % (k, v) for k, v in resp.headers.items()])
        dump.append('')
        if resp.content:
            content = resp.content
            if isinstance(content, six.binary_type):
                try:
                    content = encodeutils.safe_decode(resp.content)
                except UnicodeDecodeError:
                    pass
                else:
                    dump.extend([content, ''])
        LOG.debug('\n'.join(dump))

    def _http_request(self, url, method, **kwargs):
        """Send an http request with the specified characteristics.

        Wrapper around requests.request to handle tasks such
        as setting headers and error handling.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', USER_AGENT)
        if self.auth_token:
            kwargs['headers'].setdefault('X-Auth-Token', self.auth_token)
        else:
            kwargs['headers'].update(self.credentials_headers())
        if self.auth_url:
            kwargs['headers'].setdefault('X-Auth-Url', self.auth_url)
        if self.region_name:
            kwargs['headers'].setdefault('X-Region-Name', self.region_name)

        self.log_curl_request(method, url, kwargs)

        if self.cert_file and self.key_file:
            kwargs['cert'] = (self.cert_file, self.key_file)

        if self.verify_cert is not None:
            kwargs['verify'] = self.verify_cert

        if self.timeout is not None:
            kwargs['timeout'] = float(self.timeout)

        # Allow the option not to follow redirects
        follow_redirects = kwargs.pop('follow_redirects', True)

        # Since requests does not follow the RFC when doing redirection to sent
        # back the same method on a redirect we are simply bypassing it.  For
        # example if we do a DELETE/POST/PUT on a URL and we get a 302 RFC says
        # that we should follow that URL with the same method as before,
        # requests doesn't follow that and send a GET instead for the method.
        # Hopefully this could be fixed as they say in a comment in a future
        # point version i.e.: 3.x
        # See issue: https://github.com/kennethreitz/requests/issues/1704
        allow_redirects = False

        try:
            resp = requests.request(
                method,
                self.endpoint_url + url,
                allow_redirects=allow_redirects,
                **kwargs)
        except socket.gaierror as e:
            message = ("Error finding address for %(url)s: %(e)s" %
                       {'url': self.endpoint_url + url, 'e': e})
            raise exc.InvalidEndpoint(message=message)
        except (socket.error,
                socket.timeout,
                requests.exceptions.ConnectionError) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s" %
                       {'endpoint': endpoint, 'e': e})
            raise exc.CommunicationError(message=message)

        self.log_http_response(resp)

        if 'X-Auth-Key' not in kwargs['headers'] and \
                (resp.status_code == 401 or
                 (resp.status_code == 500 and "(HTTP 401)" in resp.content)):
            raise exc.HTTPUnauthorized("Authentication failed. Please try"
                                       " again.\n%s"
                                       % resp.content)
        elif 400 <= resp.status_code < 600:
            raise exc.from_response(resp)
        elif resp.status_code in (301, 302, 305):
            # Redirected. Reissue the request to the new location,
            # unless caller specified follow_redirects=False
            if follow_redirects:
                location = resp.headers.get('location')
                path = self.strip_endpoint(location)
                resp = self._http_request(path, method, **kwargs)
        elif resp.status_code == 300:
            raise exc.from_response(resp)

        return resp

    def strip_endpoint(self, location):
        if location is None:
            message = "Location not returned with 302"
            raise exc.InvalidEndpoint(message=message)
        elif location.startswith(self.endpoint):
            return location[len(self.endpoint):]
        else:
            message = "Prohibited endpoint redirect %s" % location
            raise exc.InvalidEndpoint(message=message)

    def credentials_headers(self):
        creds = {}
        if self.username:
            creds['X-Auth-User'] = self.username
        if self.password:
            creds['X-Auth-Key'] = self.password
        return creds

    def json_request(self, method, url, content_type='application/json',
                     **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', content_type)
        # Don't set Accept because we aren't always dealing in JSON

        if 'body' in kwargs:
            if 'data' in kwargs:
                raise ValueError("Can't provide both 'data' and "
                                 "'body' to a request")
            LOG.warning("Use of 'body' is deprecated; use 'data' instead")
            kwargs['data'] = kwargs.pop('body')
        if 'data' in kwargs:
            kwargs['data'] = jsonutils.dumps(kwargs['data'])

        resp = self._http_request(url, method, **kwargs)
        body = resp.content

        if 'application/json' in resp.headers.get('content-type', []):
            try:
                body = resp.json()
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body

    def json_patch_request(self, url, method='PATCH', **kwargs):
        content_type = 'application/murano-packages-json-patch'
        return self.json_request(
            method, url, content_type=content_type, **kwargs)

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        if 'body' in kwargs:
            if 'data' in kwargs:
                raise ValueError("Can't provide both 'data' and "
                                 "'body' to a request")
            LOG.warning("Use of 'body' is deprecated; use 'data' instead")
            kwargs['data'] = kwargs.pop('body')
        # Chunking happens automatically if 'body' is a
        # file-like object
        return self._http_request(url, method, **kwargs)

    def client_request(self, method, url, **kwargs):
        resp, body = self.json_request(method, url, **kwargs)
        return resp

    def head(self, url, **kwargs):
        return self.client_request("HEAD", url, **kwargs)

    def get(self, url, **kwargs):
        return self.client_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.client_request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.client_request("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.raw_request("DELETE", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.client_request("PATCH", url, **kwargs)
