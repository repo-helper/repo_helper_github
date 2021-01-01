# 3rd party
from apeye import URL
from github3.repos import Repository  # type: ignore


def test_secrets(github_manager, example_config, module_cassette):
	# vcr.config.match_options = ["method", "uri", "headers"]

	repo: Repository = github_manager.github.repository("domdfcoding", "repo_helper_demo")

	# List of existing secrets.
	secrets_url = URL(repo._build_url("actions/secrets", base_url=repo._api))
	raw_secrets = repo._json(repo._get(str(secrets_url), headers=repo.PREVIEW_HEADERS), 200)
	existing_secrets = [secret["name"] for secret in raw_secrets["secrets"]]

	assert "PYPI_TOKEN" not in existing_secrets
	assert "ANACONDA_TOKEN" not in existing_secrets

	github_manager.secrets(PYPI_TOKEN="abcdefg", ANACONDA_TOKEN="hijklmnop", overwrite=False)

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
# 			result: Result = runner.invoke(secrets, catch_exceptions=False, input="abcdefg\nhijklmnop\n")
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
