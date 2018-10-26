# Copyright (c) 2012-2013 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from swift.common.swob import HTTPBadRequest
import swift.common.constraints
import swift.common.ring as _ring
from nas_connector.swift.common import ring

MAX_OBJECT_NAME_COMPONENT_LENGTH = 255


def set_object_name_component_length(len=None):
    global MAX_OBJECT_NAME_COMPONENT_LENGTH

    if len:
        MAX_OBJECT_NAME_COMPONENT_LENGTH = len
    elif hasattr(swift.common.constraints, 'constraints_conf_int'):
        MAX_OBJECT_NAME_COMPONENT_LENGTH = \
            swift.common.constraints.constraints_conf_int(
                'max_object_name_component_length', 255)
    else:
        MAX_OBJECT_NAME_COMPONENT_LENGTH = 255
    return

set_object_name_component_length()


def get_object_name_component_length():
    return MAX_OBJECT_NAME_COMPONENT_LENGTH


def validate_obj_name_component(obj):
    if not obj:
        return 'cannot begin, end, or have contiguous %s\'s' % os.path.sep
    if len(obj) > MAX_OBJECT_NAME_COMPONENT_LENGTH:
        return 'too long (%d)' % len(obj)
    if obj == '.' or obj == '..':
        return 'cannot be . or ..'
    return ''


# Save the original check object creation
__check_object_creation = swift.common.constraints.check_object_creation


# Define our new one which invokes the original
def _check_object_creation(req, object_name):
    """
    Check to ensure that everything is alright about an object to be created.
    Monkey patches swift.common.constraints.check_object_creation, invoking
    the original, and then adding an additional check for individual object
    name components.

    :param req: HTTP request object
    :param object_name: name of object to be created
    :raises HTTPRequestEntityTooLarge: the object is too large
    :raises HTTPLengthRequered: missing content-length header and not
                                a chunked request
    :raises HTTPBadRequest: missing or bad content-type header, or
                            bad metadata
    """
    ret = __check_object_creation(req, object_name)

    if ret is None:
        for obj in object_name.split(os.path.sep):
            reason = validate_obj_name_component(obj)
            if reason:
                bdy = 'Invalid object name "%s", component "%s" %s' \
                    % (object_name, obj, reason)
                ret = HTTPBadRequest(body=bdy,
                                     request=req,
                                     content_type='text/plain')

    return ret

# Replace the original checks with ours
swift.common.constraints.check_object_creation = _check_object_creation

# Save the original Ring class
__Ring = _ring.Ring

# Replace the original Ring class
_ring.Ring = ring.Ring

# Monkey patch account_listing_response
import swift.account.utils
from nas_connector.swift.account.utils import account_listing_response \
    as nc_als
swift.account.utils.account_listing_response = nc_als

# Monkey patch StoragePolicy.load_ring as POLICIES are initialized already
from swift.common.storage_policy import StoragePolicy


def load_ring(self, swift_dir):
    if self.object_ring:
        return
    self.object_ring = ring.Ring(swift_dir, ring_name='object')

StoragePolicy.load_ring = load_ring
