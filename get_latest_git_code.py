#!/usr/bin/python

import sys
import os

"""This Python script gets the latest source code from a specified list of Git
repositories and runs tests against them. If any of the repositories
have unstaged or staged but uncommitted changes, the latest source code
will not be retrieved from that repository. 

The script assumes that all repository directories reside in the same parent
directory on the local machine, and that all repositories have a test suite
that is run by executing a single script with the same name in each directory.
This script should be run from the parent directory of the Git repositories.
"""

def has_unstaged_changes():
    return_code = os.system("git diff --exit-code")
    return return_code != 0

def has_staged_but_uncommitted_changes():
    return_code = os.system("git diff --cached --exit-code")
    return return_code != 0

def repo_has_test_script(test_script_name):
    return os.path.exists(test_script_name)

def readable_list_format(items_list):
    if len(items_list) < 2:
        return ", ".join(items_list)
    else:
        return ", ".join(items_list[:-1]) + " and " + items_list[-1]

if len(sys.argv) < 3:
    sys.exit("Usage python get_latest_git_code.py <test_script_name> " \
        "[repository names]")

test_script_name = sys.argv[1]
repositories = sys.argv[2:]
unstaged_changes = []
staged_but_uncommitted_changes = []
successful_code_fetches = []
failed_test_suites = []

repos_parent_dir = os.path.dirname(os.path.realpath(__file__))

for repository in repositories:
    os.chdir(os.path.join(repos_parent_dir, repository))

    if has_unstaged_changes():
        unstaged_changes.append(repository)
    elif has_staged_but_uncommitted_changes():
        staged_but_uncommitted_changes.append(repository)
    else:
        os.system("git pull --rebase")
        if repo_has_test_script(test_script_name):
            return_code = os.system("./%s" % test_script_name)
            if return_code != 0:
                failed_test_suites.append(repository)
        successful_code_fetches.append(repository)

    os.chdir("..")

if any(unstaged_changes):
    print "\n\nThe %s repositories have unstaged changes, so the latest " \
        "source was not retrieved from them" % \
        readable_list_format(unstaged_changes)

if any(staged_but_uncommitted_changes):
    print "\n\nThe %s repositories have staged but uncommitted changes, so " \
        "the latest source was not retrieved from them" \
        % readable_list_format(staged_but_uncommitted_changes)

if any(successful_code_fetches): 
    print "\n\nThe latest code was successfully retrieved from the %s " \
        "repositories" % readable_list_format(successful_code_fetches)
else:
    print "\n\nNo code was retrieved."

if any(failed_test_suites):
    print "\n\nThe test suite failed for the %s repositories" \
        % readable_list_format(failed_test_suites)
