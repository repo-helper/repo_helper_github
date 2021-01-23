#!/usr/bin/env python3
#
#  secret_validation.py
"""
Ensure secrets have the required format before setting them on GitHub.

.. versionadded:: 0.6.0
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import json
from typing import List, Tuple

# 3rd party
from pymacaroons import Caveat, Macaroon  # type: ignore

__all__ = ["no_op_validator", "validate_pypi_token"]


def validate_pypi_token(token: str) -> Tuple[bool, str]:
	"""
	Returns whether the PyPI token *appears* to be valid.

	:param token:
	"""

	if not token.startswith("pypi-"):
		return False, "The token should start with 'pypi-'."

	b64string = token[5:]
	try:
		macaroon = Macaroon.deserialize(b64string)
	except Exception:
		return False, "Could not decode token."

	if macaroon.location != "pypi.org":
		return False, "The token is not for PyPI."

	caveats: List[Caveat] = macaroon.caveats

	if not macaroon.caveats:
		return False, "The decoded output does not have the expected format."

	try:
		permissions_dict = json.loads(caveats[0].caveat_id)
	except Exception:
		return False, "The decoded output does not have the expected format."

	# TODO: check the token has the required permissions.

	return True, ''


def no_op_validator(secret: str) -> Tuple[bool, str]:
	"""
	Used to "validate" secrets which have not had a validator implemented yet.

	:param secret:
	"""

	return True, ''
