#!/usr/bin/env python3
#
#  options.py
"""
Reusable options for click.
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
from typing import Callable

# 3rd party
import click
from domdf_python_tools.stringlist import DelimitedList

__all__ = ["token_option", "version_callback", "org_option"]


def token_option(token_var: str = "GITHUB_TOKEN") -> Callable:  # nosec: B107
	"""
	Creates a ``-t / --token`` option for the GitHub API token.

	:param token_var:
	"""

	return click.option(
			"-t",
			"--token",
			type=click.STRING,
			help=(
					"The token to authenticate with the GitHub API. "
					f"Can also be provided via the '{token_var}' environment variable."
					),
			envvar=token_var,
			required=True,
			)


def org_option() -> Callable:
	"""
	Creates a ``--org`` option to specify that the repository belongs to an organisation.

	.. versionadded: 0.3.0
	"""

	return click.option(
			"--org",
			type=click.STRING,
			help=
			"Indicates the repository belongs to the organisation configured as 'username' in repo_helper.yml.",
			is_flag=True,
			default=False,
			)


def version_callback(ctx, param, value):  # noqa: D103
	# 3rd party
	import repo_helper

	# this package
	from repo_helper_github import __version__

	if not value or ctx.resilient_parsing:
		return

	parts = DelimitedList([f"repo_helper_github version {__version__}"])

	if value > 1:
		parts.append(f"repo_helper {repo_helper.__version__}")

	click.echo(f"{parts:, }", color=ctx.color)
	ctx.exit()
