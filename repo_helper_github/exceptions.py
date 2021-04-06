#!/usr/bin/env python3
#
#  exceptions.py
"""
Custom exception types.

.. versionadded:: 0.7.0
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

__all__ = [
		"GitHubException",
		"ErrorCreatingRepository",
		"NoSuchRepository",
		"NoSuchBranch",
		"BadUsername",
		"OrganizationError",
		"TracebackHandler",
		]

# 3rd party
from consolekit import tracebacks
from consolekit.utils import abort


class GitHubException(ValueError):
	"""
	Base class for exceptions raised by ``repo-helper-github``.
	"""


class ErrorCreatingRepository(GitHubException):
	"""
	Exception raised when a repository cannot be created.

	:param username: The username of the account the repository should belong to.
	:param repository: The name of the repository which doesn't exist.
	:param org: Whether the username is a GitHub organization.
	"""

	#: The username of the account the repository was being created in.
	username: str

	#: The name of the repository being created.
	repository: str

	#: Whether the username is a GitHub organization.
	org: bool

	def __init__(self, username: str, repository: str, org: bool = False):
		self.username = str(username)
		self.repository = str(repository)
		self.org = bool(org)

		super().__init__(
				f"Could not create repository {self.repository!r} "
				f"for {'org' if self.org else 'user'} {self.username!r}."
				)

	@property
	def full_name(self) -> str:
		"""
		The full name (``user/name``) of the repository being created.
		"""

		return f"{self.username}/{self.repository}"


class NoSuchRepository(GitHubException):
	"""
	Exception raised when a repository does not exist.

	:param username: The username of the account the repository should belong to.
	:param repository: The name of the repository which doesn't exist.
	:param org: Whether the username is a GitHub organization.
	"""

	#: The username of the account the repository should belong to.
	username: str

	#: The name of the repository which doesn't exist.
	repository: str

	#: Whether the username is a GitHub organization.
	org: bool

	def __init__(self, username: str, repository: str, org: bool = False):
		self.username = str(username)
		self.repository = str(repository)
		self.org = bool(org)

		super().__init__(
				f"No such repository {self.repository!r} "
				f"for {'org' if self.org else 'user'} {self.username!r}."
				)

	@property
	def full_name(self) -> str:
		"""
		The full name (``user/name``) of the repository which doesn't exist.,
		"""

		return f"{self.username}/{self.repository}"


class NoSuchBranch(GitHubException):
	"""
	Exception raised when a branch does not exist.

	:param username: The username of the account the repository belongs to.
	:param repository: The name of the repository.
	:param branch: The name of the branch.
	"""

	#: The username of the account the repository belongs to.
	username: str

	#: The name of the repository.
	repository: str

	#: The name of the branch.
	branch: str

	def __init__(self, username: str, repository: str, branch: str):
		self.username = str(username)
		self.repository = str(repository)
		self.branch = str(branch)

		fullname = f"{self.username}/{self.repository}"
		super().__init__(f"No such branch {self.branch!r} for repository {fullname!r}.")


class BadUsername(GitHubException):
	"""
	Raised when there is a problem with the username configured in ``repo_helper.yml``.

	:param username:
	"""

	#: The problem username
	username: str

	def __init__(self, msg: str, username: str):
		self.username = str(username)
		super().__init__(msg)


class OrganizationError(GitHubException):
	"""
	Raised when there is a problem with the organization configured in ``repo_helper.yml``.

	:param organization:
	"""

	#: The problem organization
	organization: str

	def __init__(self, msg: str, organization: str):
		self.organization = str(organization)
		super().__init__(msg)


class TracebackHandler(tracebacks.TracebackHandler):
	"""
	:class:`consolekit.tracebacks.TracebackHandler` which handles subclasses of :exc:`~.GitHubException`.
	"""

	def handle_ErrorCreatingRepository(self, e: ErrorCreatingRepository) -> bool:  # noqa: D102
		raise abort(f"Error Creating Repository: {e}", colour=False)

	def handle_NoSuchRepository(self, e: NoSuchRepository) -> bool:  # noqa: D102
		raise abort(f"No Such Repository: {e}", colour=False)

	def handle_NoSuchBranch(self, e: NoSuchBranch) -> bool:  # noqa: D102
		raise abort(f"No Such Branch: {e}", colour=False)

	def handle_BadUsername(self, e: BadUsername) -> bool:  # noqa: D102
		raise abort(f"Bad Username: {e}", colour=False)

	def handle_OrganizationError(self, e: OrganizationError) -> bool:  # noqa: D102
		raise abort(f"Organization Error: {e}", colour=False)
