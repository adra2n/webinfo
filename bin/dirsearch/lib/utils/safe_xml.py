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

from __future__ import annotations

import re
from pathlib import Path

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException


ParseError = ElementTree.ParseError


FORBIDDEN_XML_MARKUP = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)


class UnsafeXML(ValueError):
    pass


def reject_unsafe_xml_markup(content: bytes | str) -> bytes | str:
    payload = content.encode("utf-8", errors="ignore") if isinstance(content, str) else content
    normalized_payload = payload.replace(b"\x00", b"") if b"\x00" in payload else payload
    if FORBIDDEN_XML_MARKUP.search(payload) or FORBIDDEN_XML_MARKUP.search(
        normalized_payload
    ):
        raise UnsafeXML("XML DTDs and entity declarations are not supported")

    return content


def fromstring(content: bytes | str):
    reject_unsafe_xml_markup(content)
    try:
        return ElementTree.fromstring(content)
    except DefusedXmlException as error:
        raise UnsafeXML("Unsafe XML markup is not supported") from error


def parse_file(path: str | Path):
    data = Path(path).read_bytes()
    reject_unsafe_xml_markup(data)
    try:
        return ElementTree.parse(path)
    except DefusedXmlException as error:
        raise UnsafeXML("Unsafe XML markup is not supported") from error
