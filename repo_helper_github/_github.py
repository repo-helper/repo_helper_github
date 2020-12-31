#!/usr/bin/env python3
#
#  _github.py
"""
Helper shims for github3.py
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import List, Optional

# 3rd party
from apeye import URL
from github3 import GitHub, users  # type: ignore
from github3.repos.branch import Branch  # type: ignore

__all__ = ["Github", "get_user", "protect"]


class Github(GitHub):
	pass


def get_user(gh: GitHub) -> users.User:
	"""
	Retrieve a :class:`github3.users.User` object for the authenticated user.
	"""

	url = gh._build_url("user")
	json = gh._json(gh._get(url), 200)
	return gh._instance_or_null(users.User, json)


def protect(branch: Branch, status_checks: Optional[List[str]] = None) -> bool:
	"""
	Enable force push protection and configure status check enforcement.

	:param status_checks: A list of strings naming status checks which must pass before merging.
		Use :py:obj:`None` or omit to use the already associated value.
	:returns: :py:obj:`True` if successful, :py:obj:`False` otherwise
	"""

	previous_values = None
	previous_protection = getattr(branch, "original_protection", {})

	if previous_protection:
		previous_values = previous_protection.get("required_status_checks", {})

	if status_checks is None and previous_values:
		status_checks = previous_values["contexts"]

	edit = {
			"required_status_checks": {"strict": False, "contexts": status_checks},
			"enforce_admins": None,
			"required_pull_request_reviews": {
					"dismiss_stale_reviews": False,
					"required_approving_review_count": 1,
					},
			"restrictions": None,
			}

	PREVIEW_HEADERS = {"Accept": "application/vnd.github.luke-cage-preview+json"}
	resp = branch._put(str(URL(branch._api) / "protection"), json=edit, headers=PREVIEW_HEADERS)

	branch._json(resp, 200)
	return branch._boolean(resp, 200, 404)
