import os
import platform
import re
import subprocess
import requests
import json

import pyvert
from pyvert import logger


def runGit(args):
    """
    Execute git command with given arguments as passed as string
    """
    git_locations = ['git']

    if platform.system().lower() == 'darwin':
        git_locations.append('/usr/local/bin/git')

    output = err = None

    for cur_git in git_locations:
        cmd = cur_git + ' ' + args

        try:
            logger.debug('Trying to execute: "{0}" with shell in {1}'.format(
                         cmd, pyvert.PROG_DIR))
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True,
                                 cwd=pyvert.PROG_DIR)
            output, err = p.communicate()
            output = output.strip()
            logger.debug('Git output: {}'.format(output.decode('utf-8')))
        except OSError:
            logger.debug('Command failed: {}'.format(cmd))
            continue
        if b'not found' in output or \
           b'not recognized as an internal or external command' in output:
            logger.debug('Command failed: {}'.format(cmd))
            output = None
        elif b'fatal:' in output or err:
            logger.error('Git returned bad info. Are you sure' +
                         'this is a git installation?')
            output = None
        elif output:
            break

    return (output.decode('utf-8'), err.decode('utf-8'))


def get_local_version():
    """
    Returns hash and branch name
    """
    if os.path.isdir(os.path.join(pyvert.PROG_DIR, '.git')):
        # git installation, good
        output, err = runGit('rev-parse HEAD')

        if not output:
            logger.debug('Couldn\'t find latest installed version.')
            cur_commit_hash = None

        cur_commit_hash = output

        if not re.match('^[a-z0-9]+$', cur_commit_hash):
            logger.error('Output doesn\'t look like a hash, not using it!')
            cur_commit_hash = None

        branch_name, err = runGit('rev-parse --abbrev-ref HEAD')

        if not branch_name:
            logger.error('Could not retrieve branch name from git.' +
                         'Falling back to master.')
            branch_name = 'master'

        return cur_commit_hash, branch_name

    else:
        """
        """


def get_remote_version():
    """
    """
    pyvert.COMMITS_BEHIND = 0
    logger.info('Retrieving latest version information from GitHub')
    url = 'https://api.github.com/repos/{0}/{1}/commits/{2}'.format(
          'Sonic-Y3k', 'pyvert', 'master')
    version = requests.get(url)
    if version is None:
        logger.warn('Could not get the latest version from GitHub.' +
                    'Are you running a local development version?')
        return pyvert.CURRENT_VERSION

    version_json = json.loads(version.text)
    pyvert.LATEST_VERSION = version_json['sha']
    logger.debug('Latest remote version is {}'.format(pyvert.LATEST_VERSION))

    if not pyvert.CURRENT_VERSION:
        logger.info('You are running an unknown version of PlexPy.' +
                    ' Run the updater to identify your version')
        return pyvert.LATEST_VERSION

    if pyvert.LATEST_VERSION == pyvert.CURRENT_VERSION:
        logger.info('Pyvert is up to date.')
        return pyvert.LATEST_VERSION

    logger.info('Comparing currently installed version with latest ' +
                'GitHub version.')
    url = 'https://api.github.com/repos/{0}/{1}/compare/{2}...{3}'.format(
          'Sonic-Y3k', 'pyvert', pyvert.LATEST_VERSION, pyvert.CURRENT_VERSION)
    commits = requests.get(url)
    commits_json = json.loads(commits.text)

    print(url)

    if commits is None:
        logger.warn('Could not get commits behind from GitHub.')
        return pyvert.LATEST_VERSION

    try:
        pyvert.COMMITS_BEHIND = int(commits_json['behind_by'])
        logger.debug('In total, {} commits behind'.format(
                     pyvert.COMMITS_BEHIND))
    except KeyError:
        logger.info('Cannot compare version. Are you running a ' +
                    'local development version?')
        pyvert.COMMITS_BEHIND = 0

    if pyvert.COMMITS_BEHIND > 0:
        logger.info('New version is available. ' +
                    'You are {} commits behind'.format(pyvert.COMMITS_BEHIND))
    elif pyvert.COMMITS_BEHIND == 0:
        logger.info('Pyvert is up to date')

    return pyvert.LATEST_VERSION
