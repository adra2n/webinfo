# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

import re
import json

from lib.core.settings import QUERY_STRING_REGEX
from lib.utils import safe_xml


class MimeTypeUtils:
    @staticmethod
    def to_text(content):
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="replace")

        return content

    @staticmethod
    def is_json(content):
        try:
            json.loads(content)
            return True
        except json.decoder.JSONDecodeError:
            return False

    @staticmethod
    def is_xml(content):
        try:
            safe_xml.fromstring(content)
            return True
        except (safe_xml.ParseError, safe_xml.UnsafeXML):
            return False

    @staticmethod
    def is_query_string(content):
        content = MimeTypeUtils.to_text(content)
        if re.match(QUERY_STRING_REGEX, content):
            return True

        return False


def guess_mimetype(content) -> str:
    if MimeTypeUtils.is_json(content):
        return "application/json"
    elif MimeTypeUtils.is_xml(content):
        return "application/xml"
    elif MimeTypeUtils.is_query_string(content):
        return "application/x-www-form-urlencoded"
    else:
        return "text/plain"
