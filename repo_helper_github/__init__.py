#!/usr/bin/env python3
#
#  __init__.py
"""
Manage GitHub repositories with repo-helper.
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
import sys
from contextlib import contextmanager
from functools import partial
from typing import Dict, List

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from consolekit.utils import abort
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList
from dulwich.errors import NotGitRepository  # type: ignore
from github import Github, GithubException
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository
from repo_helper.cli import cli_group
from repo_helper.core import RepoHelper
from southwark.repo import Repo
from typing_extensions import NoReturn, TypedDict

# this package
from repo_helper_github.options import token_option, verbose_option, version_callback, version_option

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"github",
		"new",
		"update",
		]


class _EditKwargs(TypedDict, total=False):
	description: str
	homepage: str
	private: bool
	has_issues: bool
	has_projects: bool
	has_wiki: bool
	has_downloads: bool
	allow_squash_merge: bool
	allow_merge_commit: bool
	allow_rebase_merge: bool


class _ExcData(TypedDict):
	message: str
	errors: List[Dict[str, str]]


@version_option(version_callback)
@cli_group(invoke_without_command=False)
def github():
	"""
	Manage a GitHub repo.
	"""


github_command = partial(github.command, context_settings=CONTEXT_SETTINGS)


@verbose_option()
@token_option()
@github_command()
def new(token: str, verbose: bool = False):
	"""
	Create a new GitHub repository for this project.
	"""

	sys.exit(GithubManager(token).new(verbose))


@verbose_option()
@token_option()
@github_command()
def update(token: str, verbose: bool = False):
	"""
	Update the GitHub repository for this project.
	"""

	sys.exit(GithubManager(token).update(verbose))


@contextmanager
def echo_rate_limit(github: Github, verbose: bool = True):
	rate = github.get_rate_limit()
	remaining_requests = rate.core.remaining

	if not remaining_requests:
		raise abort(f"No requests available! Resets at {rate.core.reset}")

	if verbose:
		click.echo(f"{remaining_requests} requests available.")

	yield github

	if verbose:
		rate = github.get_rate_limit()
		used_requests = remaining_requests - rate.core.remaining
		click.echo(f"Used {used_requests} requests. {rate.core.remaining} remaining. Resets at {rate.core.reset}")


class GithubManager(RepoHelper):
	"""

	:param token: The token to authenticate with the GitHub API.
	"""

	def __init__(self, token: str):
		super().__init__(PathPlus.cwd())
		self.github = Github(token)

	def new(self, verbose: bool = False) -> int:
		"""
		Create a new GitHub repository for this project.

		:param verbose:
		"""

		with echo_rate_limit(self.github, verbose):
			user: AuthenticatedUser = self.github.get_user()
			self.assert_matching_usernames(user)

			try:
				repo = user.create_repo(self.templates.globals["repo_name"], **self.get_repo_kwargs())
			except GithubException as e:
				self.handle_exception(e)

			self.update_topics(repo)
			click.echo(f"Success! View the repository online at {repo.html_url}")

			try:
				# Try to set the upstream url, or fail silently
				config = Repo('.').get_config()
				config.set(("remote", "origin"), "url", repo.ssh_url.encode("UTF-8"))
				config.write_to_path()

			except NotGitRepository:
				pass

		return 0

	def update(self, verbose: bool = False) -> int:
		"""
		Update the GitHub repository for this project.

		:param verbose:
		"""

		with echo_rate_limit(self.github, verbose):
			user: AuthenticatedUser = self.github.get_user()
			self.assert_matching_usernames(user)

			try:
				repo = user.get_repo(self.templates.globals["repo_name"])
			except GithubException as e:
				self.handle_exception(e)

			repo.edit(**self.get_repo_kwargs())
			self.update_topics(repo)
			click.echo("Up to date!")

		return 0

	def assert_matching_usernames(self, user: AuthenticatedUser):
		if user.login != self.templates.globals["username"]:
			raise abort(
					f"The username configured in 'repo_helper.yml' ({self.templates.globals['username']}) "
					f"differs from that of the authenticated user ({user.login})!"
					)

	def update_topics(self, repo: Repository):
		# TODO: other languages detected in repo

		topics = set(repo.get_topics())
		topics.add("python")
		topics.update(self.templates.globals["keywords"])
		repo.replace_topics(sorted(topics))

	def handle_exception(self, exc: GithubException) -> NoReturn:
		data: _ExcData = exc.data  # type: ignore
		errors = DelimitedList(i["message"] for i in data["errors"])
		raise abort(f"{exc.data['message']}\n{errors:\t\n}")

	def get_repo_kwargs(self) -> _EditKwargs:
		edit_kwargs: _EditKwargs = {"description": self.templates.globals["short_desc"]}

		if self.templates.globals["enable_docs"]:
			edit_kwargs["homepage"] = "https://{repo_name}.readthedocs.io".format_map(self.templates.globals)

		return edit_kwargs
