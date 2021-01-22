#!/usr/bin/env python3
#
#  cli.py
"""
Manage GitHub repositories with ``repo-helper``.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import sys
from functools import partial
from typing import Callable

# 3rd party
import click
from click import Command
from consolekit import CONTEXT_SETTINGS
from consolekit.options import colour_option, verbose_option, version_option
from consolekit.terminal_colours import ColourTrilean
from github3_utils.click import token_option
from repo_helper.cli import cli_group

# this package
from repo_helper_github.options import org_option, version_callback

__all__ = [
		"github",
		"new",
		"update",
		"github_command",
		"protect_branch",
		"labels",
		]


@version_option(version_callback)
@cli_group(invoke_without_command=False)
def github():
	"""
	Manage a GitHub repo.
	"""


github_command = partial(github.command, context_settings=CONTEXT_SETTINGS)


def options(command: Command) -> Command:
	deco: Callable[[Command], Command]
	for deco in [
			colour_option(),
			verbose_option(help_text="Show information on the GitHub API rate limit."),
			token_option(),
			org_option(),
			]:
		command = deco(command)

	return command


@options
@github_command()
def new(token: str, verbose: bool = False, colour: ColourTrilean = None, org: bool = False):
	"""
	Create a new GitHub repository for this project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_github import GitHubManager

	sys.exit(GitHubManager(token, PathPlus.cwd(), verbose=verbose, colour=colour).new(org=org))


@options
@github_command()
def update(token: str, verbose: bool = False, colour: ColourTrilean = None, org: bool = False):
	"""
	Update the GitHub repository for this project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_github import GitHubManager

	sys.exit(GitHubManager(token, PathPlus.cwd(), verbose=verbose, colour=colour).update(org=org))


@options
@github_command()
def secrets(token: str, verbose: bool = False, colour: ColourTrilean = None, org: bool = False):
	"""
	Set or update the secrets of the GitHub repository for this project.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_github import GitHubManager

	sys.exit(GitHubManager(token, PathPlus.cwd(), verbose=verbose, colour=colour).secrets(org=org))


@click.argument("branch", type=click.STRING)
@options
@github_command()
def protect_branch(
		branch: str,
		token: str,
		verbose: bool = False,
		colour: ColourTrilean = None,
		org: bool = False,
		):
	"""
	Set or update the branch protection for the given branch on GitHub.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_github import GitHubManager

	sys.exit(GitHubManager(token, PathPlus.cwd(), verbose=verbose, colour=colour).protect_branch(branch, org=org))


@options
@github_command()
def labels(token: str, verbose: bool = False, colour: ColourTrilean = None, org: bool = False):
	"""
	Create labels for this repository.
	"""

	# 3rd party
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_github import GitHubManager

	sys.exit(GitHubManager(token, PathPlus.cwd(), verbose=verbose, colour=colour).create_labels(org=org))
