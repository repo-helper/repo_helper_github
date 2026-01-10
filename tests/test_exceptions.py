# stdlib
import re
from typing import Type

# 3rd party
import click
import pytest

# this package
from repo_helper_github.exceptions import (
		BadUsername,
		ErrorCreatingRepository,
		GitHubException,
		NoSuchBranch,
		NoSuchRepository,
		OrganizationError,
		TracebackHandler
		)


@pytest.mark.parametrize(
		"exception",
		[
				GitHubException,
				GitHubException(),
				GitHubException("An error occurred"),
				ErrorCreatingRepository("domdfcoding", "domdf_python_tools"),
				ErrorCreatingRepository("domdfcoding", "domdf_python_tools", org=False),
				ErrorCreatingRepository("repo-helper", "whey", org=True),
				NoSuchRepository("domdfcoding", "domdf_python_tools"),
				NoSuchRepository("domdfcoding", "domdf_python_tools", org=False),
				NoSuchRepository("repo-helper", "whey", org=True),
				NoSuchBranch("domdfcoding", "domdf_python_tools", "master"),
				NoSuchBranch("repo-helper", "whey", "main"),
				BadUsername("Invalid username", "domdfcoding"),
				BadUsername("Invalid username", "repo-helper"),
				OrganizationError("Invalid organization", "domdfcoding"),
				OrganizationError("Invalid organization", "repo-helper"),
				],
		)
def test_GitHubException(exception: GitHubException):
	with pytest.raises(GitHubException):
		raise exception

	with pytest.raises(ValueError):  # noqa: PT011
		raise exception


def test_ErrorCreatingRepository():
	exception = ErrorCreatingRepository("domdfcoding", "domdf_python_tools")
	assert isinstance(exception, ErrorCreatingRepository)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	assert exception.repository == "domdf_python_tools"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "domdfcoding/domdf_python_tools"
	assert isinstance(exception.full_name, str)

	assert not exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(
			ErrorCreatingRepository,
			match="Could not create repository 'domdf_python_tools' for user 'domdfcoding'.",
			):
		raise exception

	exception = ErrorCreatingRepository("domdfcoding", "domdf_python_tools", org=False)
	assert isinstance(exception, ErrorCreatingRepository)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	assert exception.repository == "domdf_python_tools"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "domdfcoding/domdf_python_tools"
	assert isinstance(exception.full_name, str)

	assert not exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(
			ErrorCreatingRepository,
			match="Could not create repository 'domdf_python_tools' for user 'domdfcoding'.",
			):
		raise exception

	exception = ErrorCreatingRepository("repo-helper", "whey", org=True)
	assert isinstance(exception, ErrorCreatingRepository)

	assert exception.username == "repo-helper"
	assert isinstance(exception.username, str)

	assert exception.repository == "whey"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "repo-helper/whey"
	assert isinstance(exception.full_name, str)

	assert exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(ErrorCreatingRepository, match="Could not create repository 'whey' for org 'repo-helper'."):
		raise exception


def test_NoSuchRepository():
	exception = NoSuchRepository("domdfcoding", "domdf_python_tools")
	assert isinstance(exception, NoSuchRepository)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	assert exception.repository == "domdf_python_tools"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "domdfcoding/domdf_python_tools"
	assert isinstance(exception.full_name, str)

	assert not exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(NoSuchRepository, match="No such repository 'domdf_python_tools' for user 'domdfcoding'."):
		raise exception

	exception = NoSuchRepository("domdfcoding", "domdf_python_tools", org=False)
	assert isinstance(exception, NoSuchRepository)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	assert exception.repository == "domdf_python_tools"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "domdfcoding/domdf_python_tools"
	assert isinstance(exception.full_name, str)

	assert not exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(NoSuchRepository, match="No such repository 'domdf_python_tools' for user 'domdfcoding'."):
		raise exception

	exception = NoSuchRepository("repo-helper", "whey", org=True)
	assert isinstance(exception, NoSuchRepository)

	assert exception.username == "repo-helper"
	assert isinstance(exception.username, str)

	assert exception.repository == "whey"
	assert isinstance(exception.repository, str)

	assert exception.full_name == "repo-helper/whey"
	assert isinstance(exception.full_name, str)

	assert exception.org
	assert isinstance(exception.org, bool)

	with pytest.raises(NoSuchRepository, match="No such repository 'whey' for org 'repo-helper'."):
		raise exception


def test_NoSuchBranch():
	exception = NoSuchBranch("domdfcoding", "domdf_python_tools", "master")
	assert isinstance(exception, NoSuchBranch)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	assert exception.repository == "domdf_python_tools"
	assert isinstance(exception.repository, str)

	assert exception.branch == "master"
	assert isinstance(exception.branch, str)

	with pytest.raises(
			NoSuchBranch,
			match="No such branch 'master' for repository 'domdfcoding/domdf_python_tools'.",
			):
		raise exception

	exception = NoSuchBranch("repo-helper", "whey", "main")
	assert isinstance(exception, NoSuchBranch)

	assert exception.username == "repo-helper"
	assert isinstance(exception.username, str)

	assert exception.repository == "whey"
	assert isinstance(exception.repository, str)

	assert exception.branch == "main"
	assert isinstance(exception.branch, str)

	with pytest.raises(NoSuchBranch, match="No such branch 'main' for repository 'repo-helper/whey'."):
		raise exception


def test_BadUsername():
	exception = BadUsername("Invalid username", "domdfcoding")
	assert isinstance(exception, BadUsername)

	assert exception.username == "domdfcoding"
	assert isinstance(exception.username, str)

	with pytest.raises(BadUsername, match="Invalid username"):
		raise exception

	exception = BadUsername("Invalid username", "repo-helper")
	assert isinstance(exception, BadUsername)

	assert exception.username == "repo-helper"
	assert isinstance(exception.username, str)

	with pytest.raises(BadUsername, match="Invalid username"):
		raise exception


def test_OrganizationError():
	exception = OrganizationError("Invalid organization", "domdfcoding")
	assert isinstance(exception, OrganizationError)

	assert exception.organization == "domdfcoding"
	assert isinstance(exception.organization, str)

	with pytest.raises(OrganizationError, match="Invalid organization"):
		raise exception

	exception = OrganizationError("Invalid organization", "repo-helper")
	assert isinstance(exception, OrganizationError)

	assert exception.organization == "repo-helper"
	assert isinstance(exception.organization, str)

	with pytest.raises(OrganizationError, match="Invalid organization"):
		raise exception


@pytest.mark.parametrize(
		"exception, match",
		[
				(ErrorCreatingRepository("domdfcoding", "domdf_python_tools"), "Error Creating Repository: "),
				(
						ErrorCreatingRepository("domdfcoding", "domdf_python_tools", org=False),
						"Error Creating Repository: ",
						),
				(ErrorCreatingRepository("repo-helper", "whey", org=True), "Error Creating Repository: "),
				(NoSuchRepository("domdfcoding", "domdf_python_tools"), "No Such Repository: "),
				(NoSuchRepository("domdfcoding", "domdf_python_tools", org=False), "No Such Repository: "),
				(NoSuchRepository("repo-helper", "whey", org=True), "No Such Repository: "),
				(NoSuchBranch("domdfcoding", "domdf_python_tools", "master"), "No Such Branch: "),
				(NoSuchBranch("repo-helper", "whey", "main"), "No Such Branch: "),
				(BadUsername("Invalid username", "domdfcoding"), "Bad Username: Invalid username"),
				(BadUsername("Invalid username", "repo-helper"), "Bad Username: Invalid username"),
				(
						OrganizationError("Invalid organization", "domdfcoding"),
						"Organization Error: Invalid organization",
						),
				(
						OrganizationError("Invalid organization", "repo-helper"),
						"Organization Error: Invalid organization",
						),
				],
		)
def test_TracebackHandler(exception: Type[Exception], match: str, capsys):
	with pytest.raises(click.Abort), TracebackHandler()():
		raise exception

	assert re.match(match, capsys.readouterr().err)
