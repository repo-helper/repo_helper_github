#!/usr/bin/env python3
#
#  __init__.py
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
import tempfile
from getpass import getpass
from typing import Iterator, Optional, Union

# 3rd party
import click
from consolekit.input import confirm
from consolekit.terminal_colours import ColourTrilean, Fore, resolve_color_default
from consolekit.utils import abort
from deprecation_alias import deprecated
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from dulwich.errors import NotGitRepository
from dulwich.porcelain import fetch
from github3 import GitHub, orgs, repos, users
from github3.exceptions import NotFoundError
from github3.repos import contents
from github3.repos.branch import Branch
from github3_utils import echo_rate_limit as _utils_echo_rate_limit
from github3_utils import get_user, protect_branch, secrets
from github3_utils.check_labels import check_status_labels
from repo_helper.core import RepoHelper
from repo_helper.files.ci_cd import ActionsManager, platform_ci_names
from repo_helper.utils import set_gh_actions_versions
from southwark.repo import Repo

# this package
from repo_helper_github._github import Github
from repo_helper_github._types import _EditKwargs
from repo_helper_github.cli import github_command

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.5.1"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"github_command",
		"echo_rate_limit",
		"GitHubManager",
		"IsolatedGitHubManager",
		"encrypt_secret",
		"compile_required_checks",
		]

echo_rate_limit = deprecated(
		deprecated_in="0.5.1",
		removed_in="1.0.0",
		current_version=__version__,
		details="Use the new 'github3-utils' package instead."
		)(
				_utils_echo_rate_limit
				)


def _lower(string: str) -> str:
	return string.lower().replace('_', '-')


class GitHubManager(RepoHelper):
	"""
	Subclass of :class:`repo_helper.core.RepoHelper`
	with additional functions to update the repository metadata on GitHub.

	:param token: The token to authenticate with the GitHub API.
	:param target_repo: The path to the root of the repository to manage files for.
	:param managed_message: Message placed at the top of files to indicate that they are managed by ``repo_helper``.
	:param verbose: Whether to show information on the GitHub API rate limit.
	:param colour: Whether to use coloured output.

	.. versionchanged:: 0.5.1  Added the ``verbose`` and ``colour`` options.
	"""  # noqa: D400

	#:
	github: GitHub

	verbose: bool
	"""
	Whether to show information on the GitHub API rate limit.

	.. versionadded: 0.5.1
	"""

	colour: ColourTrilean
	"""
	Whether to use coloured output.

	.. versionadded: 0.5.1
	"""

	def __init__(
			self,
			token: str,
			target_repo: PathLike,
			managed_message="This file is managed by 'repo_helper'. Don't edit it directly.",
			*,
			verbose: bool = False,
			colour: ColourTrilean = True,
			):
		super().__init__(target_repo, managed_message)

		self.github = Github(token=token)
		self.verbose = verbose
		self.colour = resolve_color_default(colour)

	def echo_rate_limit(self):
		"""
		Contextmanager to echo the GitHub API rate limit before and after making a series of requests.
		"""

		return echo_rate_limit(self.github, self.verbose)

	def new(self, org: bool = False) -> int:
		"""
		Create a new GitHub repository for this project.

		:param org: Whether the repository should be created for the organisation set as ``username``,
			or for the authenticated user (default).

		.. versionchanged:: 0.5.1

			Removed the ``verbose`` option. Provide it to the class constructor instead.

		.. versionchanged:: 0.5.1  Added the ``org`` argument.
		"""

		with self.echo_rate_limit():
			user = self.get_org_or_user(org)
			repo_name = self.templates.globals["repo_name"]

			repo: Optional[repos.Repository]

			if org:
				repo = user.create_repository(repo_name, **self.get_repo_kwargs())
			else:
				repo = self.github.create_repository(repo_name, **self.get_repo_kwargs())

			if repo is None:
				raise abort(f"No such repository {repo_name} for {'org' if org else 'user'} {user.login}.")

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

	def update(self, org: bool = False) -> int:
		"""
		Update the GitHub repository for this project.

		:param org: Whether the repository should be created for the organisation set as ``username``,
			or for the authenticated user (default).

		.. versionchanged:: 0.5.1

			Removed the ``verbose`` option. Provide it to the class constructor instead.

		.. versionchanged:: 0.5.1  Added the ``org`` argument.
		"""

		with self.echo_rate_limit():
			user = self.get_org_or_user(org)
			repo_name = self.templates.globals["repo_name"]
			repo: Optional[repos.Repository] = self.github.repository(user.login, repo_name)

			if repo is None:
				raise abort(f"No such repository {repo_name} for {'org' if org else 'user'} {user.login}.")

			# TODO: add config option for allow_merge_commit

			repo.edit(
					name=repo.name,
					**self.get_repo_kwargs(),
					allow_merge_commit=False,
					)

			self.update_topics(repo)
			click.echo("Up to date!")

		return 0

	def get_org_or_user(self, org: bool = False) -> Union[orgs.Organization, users.User]:
		"""
		If ``org`` is :py:obj:`True`, returns the :class:`~.Organization` object representing the
		GitHub org that owns the repository.

		If ``org`` is :py:obj:`False`, returns the :class:`~.AuthenticatedUser` object representing the
		GitHub user that owns the repository.

		:param org:

		.. versionadded:: 0.5.1
		"""  # noqa: D400

		user = get_user(self.github)

		if org:
			self.assert_org_member(user)
			return self.github.organization(self.templates.globals["username"])
		else:
			self.assert_matching_usernames(user)
			return user

	def secrets(
			self,
			org: bool = False,
			overwrite: Optional[bool] = None,
			PYPI_TOKEN: Optional[str] = None,
			ANACONDA_TOKEN: Optional[str] = None
			) -> int:
		"""
		Set or update the secrets of the GitHub repository for this project.

		:param org: Whether the repository should be created for the organisation set as ``username``,
			or for the authenticated user (default).
		:param overwrite: Overwrite existing values.
		:default overwrite: ask first.

		``PYPI_TOKEN`` and ``ANACONDA_TOKEN`` can either be passed as keyword arguments to this function or provided at the interactive prompt.

		.. versionadded:: 0.5.1
		.. versionchanged:: 0.5.1  Add ``overwrite``, ``PYPI_TOKEN``, ``ANACONDA_TOKEN`` options.
		"""

		with self.echo_rate_limit():
			user = self.get_org_or_user(org)
			repo_name = self.templates.globals["repo_name"]

			repo: Optional[repos.Repository] = self.github.repository(user.login, repo_name)

			if repo is None:
				raise abort(f"No such repository {repo_name} for {'org' if org else 'user'} {user.login}.")

			# List of existing secrets.
			existing_secrets = secrets.get_secrets(repo)

			# Public key to encrypt secrets with.
			public_key = secrets.get_public_key(repo)

			ret = 0
			target_secrets = {"PYPI_TOKEN"}

			if self.templates.globals["enable_conda"]:
				target_secrets.add("ANACONDA_TOKEN")

			for secret_name in sorted(target_secrets):
				if overwrite is not None:
					update = True
				elif secret_name in existing_secrets:
					click.echo(f"A value for the secret {secret_name!r} already exists. ")
					update = confirm("Do you want to update the secret?")
				else:
					update = True

				if update:
					operation = "update" if secret_name in existing_secrets else "create"

					response = secrets.set_secret(
							repo,
							secret_name=secret_name,
							value=locals().get(secret_name, None) or getpass(f"{secret_name}: "),
							public_key=public_key,
							)

					if response.status_code not in {200, 201, 204}:
						message = f"Could not {operation} the secret {secret_name!r}: Status {response.status_code}"
						click.echo(Fore.YELLOW(message), color=self.colour)
						ret |= 1
					else:
						message = f"Successfully {operation}d the secret {secret_name!r}."
						click.echo(Fore.GREEN(message), color=self.colour)

		return ret

	def protect_branch(self, branch: str, org: bool = False) -> int:
		"""
		Update branch protection for the given branch.

		This requires that the Linux and Windows tests pass, together with the mypy check.

		:param branch: The branch to update protection for.
		:param org: Whether the repository should be created for the organisation set as ``username``,
			or for the authenticated user (default).

		.. versionadded:: 0.5.1
		"""

		with self.echo_rate_limit():
			user = self.get_org_or_user(org)
			repo_name = self.templates.globals["repo_name"]

			repo: Optional[repos.Repository] = self.github.repository(user.login, repo_name)

			if repo is None:
				raise abort(f"No such repository {repo_name} for {'org' if org else 'user'} {user.login}.")

			gh_branch: Optional[Branch] = repo.branch(branch)

			if not gh_branch:
				raise click.UsageError(f"No such branch {branch}")

			required_checks = list(compile_required_checks(self))

			protect_branch(gh_branch, status_checks=required_checks)

		click.echo("Up to date!")
		return 0

	def assert_matching_usernames(self, user: users.User):
		"""
		Assert that the username configured in ``repo_helper.yml`` matches that of the authenticated user.

		:param user:
		"""

		if user.login != self.templates.globals["username"]:
			raise abort(
					f"The username configured in 'repo_helper.yml' ({self.templates.globals['username']}) "
					f"differs from that of the authenticated user ({user.login})!\n"
					f"If {self.templates.globals['username']} is an organisation you should use the --org flag."
					)

	def assert_org_member(self, user: users.User):
		"""
		Assert that the organisation configured in ``repo_helper.yml`` exists, and the authenticated user is a member.

		:param user:
		"""

		def error():
			raise abort(
					f"Either the organisation configured in 'repo_helper.yml' ({self.templates.globals['username']}) "
					f"does not exist or the authenticated user ({user.login}) is not a member!"
					)

		try:
			org = self.github.organization(self.templates.globals["username"])
		except NotFoundError:
			raise error()

		if not org.is_member(user.login):
			raise error()

	def update_topics(self, repo: repos.Repository):
		"""
		Update the repository's topics.

		:param repo:
		"""
		# TODO: other languages detected in repo

		raw_topics = repo.topics()
		if raw_topics is None:
			topics = set()
		else:
			topics = set(raw_topics.names)

		topics.add("python")
		topics.update(self.templates.globals["keywords"])
		repo.replace_topics(sorted(map(_lower, topics)))

	def get_repo_kwargs(self) -> _EditKwargs:
		"""
		Returns the keyword arguments used when creating and updating repositories.
		"""

		edit_kwargs: _EditKwargs = {"description": self.templates.globals["short_desc"]}

		if self.templates.globals["enable_docs"]:
			edit_kwargs["homepage"] = self.templates.globals["docs_url"]

		return edit_kwargs

	def create_labels(self, org: bool = False) -> int:
		"""
		Create labels for this repository.

		:param org: Whether the repository should be created for the organisation set as ``username``,
			or for the authenticated user (default).

		.. versionadded:: 0.5.1
		"""

		with self.echo_rate_limit():
			user = self.get_org_or_user(org)
			repo_name = self.templates.globals["repo_name"]
			repo: Optional[repos.Repository] = self.github.repository(user.login, repo_name)

			if repo is None:
				raise abort(f"No such repository {repo_name} for {'org' if org else 'user'} {user.login}.")

			current_labels = {label.name: label for label in repo.labels()}

			for label in check_status_labels.values():
				if label.name in current_labels:
					current_labels[label.name].update(**label.to_dict())
				else:
					label.create(repo)
					click.echo(f"Created label {label.name}")

		click.echo("Up to date!")

		return 0


encrypt_secret = deprecated(
		deprecated_in="0.5.1",
		removed_in="1.0.0",
		current_version=__version__,
		details="Use the new 'github3-utils' package instead."
		)(
				secrets.encrypt_secret
				)


def compile_required_checks(repo: RepoHelper) -> Iterator[str]:
	"""
	Returns an iterator over the names of required checks for the given repository.

	:param repo:

	.. versionadded:: 0.5.1
	"""

	actions_manager = ActionsManager(repo.target_repo, repo.templates)

	for platform in repo.templates.globals["platforms"]:
		if platform not in platform_ci_names:
			continue

		if platform == "Windows":
			ci_platform = platform_ci_names[platform]
			py_versions = actions_manager.get_windows_ci_versions()
		elif platform == "Linux":
			ci_platform = platform_ci_names[platform]
			py_versions = actions_manager.get_linux_ci_versions()
		# elif platform == "macOS":
		# 	ci_platform = platform_ci_names[platform]
		# 	py_versions = actions_manager.get_macos_ci_versions()
		else:
			continue

		for version in set_gh_actions_versions(py_versions):
			if "alpha" in version or "beta" in version or "-dev" in version:
				continue

			yield f"{ci_platform} / Python {version}"

	yield from [f"mypy / {platform_ci_names['Linux']}", "Flake8"]

	if repo.templates.globals["enable_docs"]:
		yield "docs"


GithubManager = GitHubManager


class IsolatedGitHubManager(GitHubManager):
	"""
	Subclass of :class:`~.GitHubManager` which can be used isolated from the repository
	and its ``repo_helper.yml`` config file.

	:param token: The token to authenticate with the GitHub API.

	:param username: The username of the GitHub account hosting the repository.
	:param repo_name: The name of GitHub repository.
	:param managed_message: Message placed at the top of files to indicate that they are managed by ``repo_helper``.
	:param verbose: Whether to show information on the GitHub API rate limit.
	:param colour: Whether to use coloured output.

	.. versionadded:: 0.5.1
	"""  # noqa: D400

	def __init__(
			self,
			token: str,
			username: str,
			repo_name: str,
			*,
			managed_message="This file is managed by 'repo_helper'. Don't edit it directly.",
			verbose: bool = False,
			colour: ColourTrilean = True,
			):

		self._tmpdir = tempfile.TemporaryDirectory()

		self.github = Github(token=token)
		self.verbose = verbose
		self.colour = resolve_color_default(colour)

		target_repo = PathPlus(self._tmpdir.name)
		config_file_name = "repo_helper.yml"

		github_repo: repos.Repository = self.github.repository(username, repo_name)
		contents_from_github: contents.Contents = github_repo.file_contents(config_file_name)
		(target_repo / config_file_name).write_bytes(contents_from_github.decoded)

		RepoHelper.__init__(self, target_repo, managed_message)

	def __del__(self):
		self._tmpdir.cleanup()
