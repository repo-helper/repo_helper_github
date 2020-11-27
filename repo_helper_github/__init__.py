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
from base64 import b64encode
from contextlib import contextmanager
from getpass import getpass
from typing import Optional

# 3rd party
import click
from apeye import RequestsURL
from consolekit.input import confirm
from consolekit.terminal_colours import Fore, resolve_color_default
from consolekit.utils import abort
from domdf_python_tools.stringlist import DelimitedList
from domdf_python_tools.typing import PathLike
from dulwich.errors import NotGitRepository
from dulwich.porcelain import fetch
from github import Github, GithubException
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository
from nacl import encoding, public  # type: ignore
from repo_helper.core import RepoHelper
from southwark.repo import Repo
from typing_extensions import NoReturn

# this package
from repo_helper_github._types import _EditKwargs, _ExcData
from repo_helper_github.cli import github_command
from repo_helper_github.options import token_option, version_callback

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.2"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"github_command",
		"echo_rate_limit",
		"GithubManager",
		"encrypt_secret",
		]


@contextmanager
def echo_rate_limit(github: Github, verbose: bool = True):
	"""
	Contextmanager to echo the GitHub API rate limit before and after making a series of requests.

	:param github:
	:param verbose: If :py:obj:`False` no output will be printed.
	"""

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


def _lower(string: str) -> str:
	return string.lower()


class GithubManager(RepoHelper):
	"""
	Subclass of :class:`repo_helper.core.RepoHelper`
	with additional functions to update the repository metadata on GitHub.

	:param token: The token to authenticate with the GitHub API.
	:param target_repo: The path to the root of the repository to manage files for.
	:param managed_message: Message placed at the top of files to indicate that they are managed by ``repo_helper``.
	:param verbose: Whether to show information on the GitHub API rate limit.
	:param colour: Whether to use coloured output.

	.. versionchanged:: 0.2.2

		Added the ``verbose`` and ``colour`` options.
	"""

	#:
	github: Github

	verbose: bool
	"""
	Whether to show information on the GitHub API rate limit.

	.. versionadded: 0.2.2
	"""

	colour: Optional[bool]
	"""
	Whether to use coloured output.

	.. versionadded: 0.2.2
	"""

	def __init__(
			self,
			token: str,
			target_repo: PathLike,
			managed_message="This file is managed by 'repo_helper'. Don't edit it directly.",
			*,
			verbose: bool = False,
			colour: Optional[bool] = True,
			):
		super().__init__(target_repo, managed_message)

		self.github = Github(token)
		self.verbose = verbose
		self.colour = resolve_color_default(colour)

	def echo_rate_limit(self):
		return echo_rate_limit(self.github, self.verbose)

	def new(self) -> int:
		"""
		Create a new GitHub repository for this project.

		.. versionchanged:: 0.2.2

			Removed the ``verbose`` option. Provide it to the class constructor instead.
		"""

		with self.echo_rate_limit():
			user: AuthenticatedUser = self.github.get_user()
			self.assert_matching_usernames(user)

			try:
				repo = user.create_repo(self.templates.globals["repo_name"], **self.get_repo_kwargs())
			except GithubException as e:
				self.handle_exception(e)

			self.update_topics(repo)
			click.echo(f"Success! View the repository online at {repo.html_url}")

			try:
				dulwich_repo = Repo('.')
			except NotGitRepository:
				return 0

			config = dulwich_repo.get_config()
			config.set(("remote", "origin"), "url", repo.ssh_url.encode("UTF-8"))
			config.set(("remote", "origin"), "fetch", b"+refs/heads/*:refs/remotes/origin/*")
			config.write_to_path()

			fetch(dulwich_repo, remote_location="origin")

		return 0

	def update(self) -> int:
		"""
		Update the GitHub repository for this project.

		.. versionchanged:: 0.2.2

			Removed the ``verbose`` option. Provide it to the class constructor instead.
		"""

		with self.echo_rate_limit():
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

	def secrets(self) -> int:
		"""
		Set or update the secrets of the GitHub repository for this project.

		.. versionadded: 0.2.2
		"""

		with self.echo_rate_limit():
			user: AuthenticatedUser = self.github.get_user()
			self.assert_matching_usernames(user)

			try:
				repo: Repository = user.get_repo(self.templates.globals["repo_name"])
			except GithubException as e:
				self.handle_exception(e)

			repos_url = RequestsURL("https://api.github.com/repos")
			secrets_url = repos_url / repo.owner.login / repo.name / "actions/secrets"
			secrets_url.session.headers = {
					"Authorization": repo._requester._Requester__authorizationHeader,  # type: ignore
					"user-agent": "repo_helper_github",
					}

			# List of existing secrets.
			existing_secrets = [secret["name"] for secret in secrets_url.get().json()["secrets"]]

			# Public key to encrypt secrets with.
			public_key = (secrets_url / "public-key").get().json()

			ret = 0
			target_secrets = {"PYPI_TOKEN"}

			if self.templates.globals["enable_conda"]:
				target_secrets.add("ANACONDA_TOKEN")

			for secret_name in sorted(target_secrets):
				if secret_name in existing_secrets:
					click.echo(f"A value for the secret {secret_name!r} already exists. ")
					update = confirm("Do you want to update the secret?")
				else:
					update = True

				if update:
					operation = "create" if secret_name in existing_secrets else "update"

					response = (secrets_url / secret_name).put(
							json={
									"encrypted_value":
											encrypt_secret(public_key["key"], getpass(f"{secret_name}: ")),
									"key_id":
											public_key["key_id"],
									},
							)

					if response.status_code not in {200, 201, 204}:
						message = f"Could not {operation} the secret {secret_name!r}: Status {response.status_code}"
						click.echo(Fore.YELLOW(message), color=self.colour)
						ret |= 1
					else:
						message = f"Successfully {operation}d the secret {secret_name!r}."
						click.echo(Fore.GREEN(message), color=self.colour)

		return ret

	def assert_matching_usernames(self, user: AuthenticatedUser):
		"""
		Assert that the username configured in ``repo_helper.yml`` matches that of the authenticated user.

		:param user:
		"""

		if user.login != self.templates.globals["username"]:
			raise abort(
					f"The username configured in 'repo_helper.yml' ({self.templates.globals['username']}) "
					f"differs from that of the authenticated user ({user.login})!"
					)

	def update_topics(self, repo: Repository):
		"""
		Update the repository's topics.

		:param repo:
		"""
		# TODO: other languages detected in repo

		topics = set(repo.get_topics())
		topics.add("python")
		topics.update(self.templates.globals["keywords"])
		repo.replace_topics(sorted(map(_lower, topics)))

	@staticmethod
	def handle_exception(exc: GithubException) -> NoReturn:
		"""
		Handle an exception raised by the GitHub REST API.

		:param exc:

		:raises: :class:`click.Abort`
		"""

		data: _ExcData = exc.data  # type: ignore
		errors = DelimitedList(i["message"] for i in data["errors"])
		raise abort(f"{exc.data['message']}\n{errors:\t\n}")

	def get_repo_kwargs(self) -> _EditKwargs:
		"""
		Returns the keyword arguments used when creating and updating repositories.
		"""

		edit_kwargs: _EditKwargs = {"description": self.templates.globals["short_desc"]}

		if self.templates.globals["enable_docs"]:
			edit_kwargs["homepage"] = "https://{repo_name}.readthedocs.io".format_map(self.templates.globals)

		return edit_kwargs


def encrypt_secret(public_key: str, secret_value: str) -> str:
	"""
	Encrypt a GitHub Actions secret.

	:param public_key:
	:param secret_value:

	.. versionadded: 0.2.2
	"""

	public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
	sealed_box = public.SealedBox(public_key)
	encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
	return b64encode(encrypted).decode("utf-8")
