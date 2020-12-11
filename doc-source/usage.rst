=======
Usage
=======

repo-helper github
--------------------

.. click:: repo_helper_github.cli:github
	:prog: repo-helper github
	:nested: none

Commands
^^^^^^^^^^^^^^^^^^^^^^^^^

new
*****

.. click:: repo_helper_github.cli:new
	:prog: repo-helper github new
	:nested: none

update
*******

.. click:: repo_helper_github.cli:update
	:prog: repo-helper github update
	:nested: none

secrets
********

.. click:: repo_helper_github.cli:secrets
	:prog: repo-helper github secrets
	:nested: none

Tokens
^^^^^^^^^


The token passed to the ``-t / --token`` argument, or set as the ``GITHUB_TOKEN`` environment variable,
must have the following OAuth scopes:

* ``public_repo`` -- Access public repositories
* ``workflow`` -- Update github action workflows
* ``read:org`` -- Read org and team membership, read org projects


For information on creating a personal access token please see the
`GitHub Documentation <https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token>`_.
