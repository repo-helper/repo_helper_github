# stdlib
import json

# 3rd party
import pymacaroons  # type: ignore
import pytest
from apeye import URL
from github3.repos import Repository

# this package
from repo_helper_github import validate_pypi_token


@pytest.mark.usefixtures("module_cassette", "example_config")
def test_secrets(github_manager):
	# vcr.config.match_options = ["method", "uri", "headers"]

	repo: Repository = github_manager.github.repository("domdfcoding", "repo_helper_demo")

	# List of existing secrets.
	secrets_url = URL(repo._build_url("actions/secrets", base_url=repo._api))
	raw_secrets = repo._json(repo._get(str(secrets_url), headers=repo.PREVIEW_HEADERS), 200)
	existing_secrets = [secret["name"] for secret in raw_secrets["secrets"]]

	assert "PYPI_TOKEN" not in existing_secrets
	assert "ANACONDA_TOKEN" not in existing_secrets

	token = (  # nosec: B105
		"pypi-AgEIcHlwaS5vcmcCCzEyMzQ1LTY3ODkwAAI5eyJwZXJtaXNzaW9ucyI6IHsicHJvamVjdHMiO"
		"iBbImRpY3QyY3NzIl19LCAidmVyc2lvbiI6IDF9AAAGIKPx0SjZyXiAHSDI89qzSUwDTx_iWtoPJEztlNS7Q5I6"
		)

	github_manager.secrets(
			PYPI_TOKEN=token,
			ANACONDA_TOKEN="hijklmnop",  # nosec: B105
			overwrite=False,
			)

	# List of existing secrets.
	raw_secrets = repo._json(repo._get(str(secrets_url), headers=repo.PREVIEW_HEADERS), 200)
	existing_secrets = [secret["name"] for secret in raw_secrets["secrets"]]

	assert "PYPI_TOKEN" in existing_secrets
	assert "ANACONDA_TOKEN" in existing_secrets


#
# def test_via_cli(temp_empty_repo, tmp_pathplus, example_config, monkeypatch, file_regression):
# 	monkeypatch.setenv("GITHUB_TOKEN", "FAKE_TOKEN")
#
# 	session = GitHubSession()
#
# 	def __init__(self, username="", password="", token="", *args, **kwargs):
# 		super(Github, self).__init__(username=username, password=password, token=token, session=session)
#
# 	monkeypatch.setattr(Github, "__init__", __init__)
#
# 	(tmp_pathplus / "repo_helper.yml").write_lines([
# 			*example_config.splitlines()[:8],
# 			*example_config.splitlines()[10:],
# 			'',
# 			"keywords:",
# 			"   - repo_helper",
# 			"   - github",
# 			"   - configuration",
# 			])
#
# 	with Betamax(session) as vcr:
# 		vcr.use_cassette("test_secrets", record="once")
#
# 		manager = GitHubManager(
# 				"FAKE_TOKEN",
# 				tmp_pathplus,
# 				verbose=True,
# 				colour=False,
# 				)
#
# 		repo = manager.github.repository("domdfcoding", "repo_helper_demo")
#
# 		# List of existing secrets.
# 		secrets_url = URL(repo._build_url("actions/secrets", base_url=repo._api))
# 		raw_secrets = repo._json(repo._get(str(secrets_url), headers=repo.PREVIEW_HEADERS), 200)
# 		existing_secrets = [secret["name"] for secret in raw_secrets["secrets"]]
#
# 		assert "PYPI_TOKEN" not in existing_secrets
# 		assert "ANACONDA_TOKEN" not in existing_secrets
#
# 		with in_directory(tmp_pathplus):
# 			runner = CliRunner()
# 			result: Result = runner.invoke(secrets, input="abcdefg\nhijklmnop\n")
#
# 		assert result.exit_code == 0
# 		check_file_regression(result.stdout.rstrip(), file_regression, extension=".md")
#
# 		# List of existing secrets.
# 		raw_secrets = repo._json(repo._get(str(secrets_url), headers=repo.PREVIEW_HEADERS), 200)
# 		existing_secrets = [secret["name"] for secret in raw_secrets["secrets"]]
#
# 		assert "PYPI_TOKEN" in existing_secrets
# 		assert "ANACONDA_TOKEN" in existing_secrets


class TestValidatePyPIToken:

	@pytest.mark.parametrize("token", ["HELLO_WORLD", "pypi_", "12345678"])
	def test_wrong_start(self, token: str):
		assert validate_pypi_token(token) == (False, "The token should start with 'pypi-'.")

	@pytest.mark.parametrize("token", ["pypi-HELLO_WORLD", "pypi-12345678"])
	def test_not_b64(self, token: str):
		assert validate_pypi_token(token) == (False, "Could not decode token.")

	def test_wrong_location(self):
		fake_macaroon = pymacaroons.Macaroon(
				identifier=b"12345-67890",
				signature="4eba1dde2d0866f550278e40bb354542",
				location="github.com",
				version=pymacaroons.MACAROON_V2,
				)
		fake_macaroon.add_first_party_caveat(json.dumps({"permissions": {"projects": ["dict2css"]}, "version": 1}))

		assert validate_pypi_token(f"pypi-{fake_macaroon.serialize()}") == (False, "The token is not for PyPI.")

	def test_no_caveats(self):
		fake_macaroon = pymacaroons.Macaroon(
				identifier=b"12345-67890",
				signature="4eba1dde2d0866f550278e40bb354542",
				location="pypi.org",
				version=pymacaroons.MACAROON_V2,
				)

		error_msg = "The decoded output does not have the expected format."
		assert validate_pypi_token(f"pypi-{fake_macaroon.serialize()}") == (False, error_msg)

	def test_caveat_not_json(self):
		fake_macaroon = pymacaroons.Macaroon(
				identifier=b"12345-67890",
				signature="4eba1dde2d0866f550278e40bb354542",
				location="pypi.org",
				version=pymacaroons.MACAROON_V2,
				)
		fake_macaroon.add_first_party_caveat("foo=bar")

		error_msg = "The decoded output does not have the expected format."
		assert validate_pypi_token(f"pypi-{fake_macaroon.serialize()}") == (False, error_msg)

	def test_seemingly_valid(self):
		fake_macaroon = pymacaroons.Macaroon(
				identifier=b"12345-67890",
				signature="4eba1dde2d0866f550278e40bb354542",
				location="pypi.org",
				version=pymacaroons.MACAROON_V2,
				)
		fake_macaroon.add_first_party_caveat(json.dumps({"permissions": {"projects": ["dict2css"]}, "version": 1}))

		assert validate_pypi_token(f"pypi-{fake_macaroon.serialize()}") == (True, '')
