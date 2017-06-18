import os
import sys
import locale
import platform
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs/'))

import pyvert
from pyvert import logger, version, versioncheck
from pyvert.config import Config

def parse_arguments():
    """
    Parse comandline arguments
    """
    parser = argparse.ArgumentParser(description='pyvert ♥')
    conflict_group = parser.add_mutually_exclusive_group()
    conflict_group.add_argument('-q', '--quiet', action='store_true',
                                help='Turn of console logging')
    conflict_group.add_argument('-v', '--verbose', action='store_true',
                                help='Increase console logging verbosity')
    parser.add_argument('--config', action='append',
                        help='Specify a config file to use')
    parser.add_argument('--datadir', action='append',
                        help='Specify a directory ' +
                        'where to store your data files')
    args = parser.parse_args()

    # config dir can only be specified once
    try:
        if len(args.config) == 1:
            if os.path.exists(args.config[0]):
                pyvert.CONFIG_DIR = args.config[0]
            else:
                raise ValueError('The config directory {} doesn\'t '.format(
                                 args.config[0]) + 'exist.')
        else:
            raise ValueError('The config dir was specified {} times.'.format(
                             len(args.config)) + ' Please check your command' +
                             ' line parameters.')
    except TypeError:
        # set to program dir if nothing is entered
        pyvert.CONFIG_DIR = pyvert.PROG_DIR
    except ValueError as e:
        # print error message and exit on error
        print(e)
        exit(1)

    # data dir can only be specified once
    try:
        if len(args.datadir) == 1:
            if os.path.exists(args.datadir[0]):
                pyvert.DATA_DIR = args.datadir[0]
            else:
                raise ValueError('The data directory {} doesn\'t '.format(
                                 args.datadir[0]) + 'exist.')
        else:
            raise ValueError('The data dir was specified {} times. '.format(
                             len(args.datadir)) + 'Please check your command' +
                             ' line parameters.')
    except TypeError:
        # set to program dir if nothing is entered
        pyvert.DATA_DIR = pyvert.PROG_DIR
    except ValueError as e:
        print(e)
        exit(1)

    # set log dir into data directory
    log_dir = os.path.join(pyvert.DATA_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    pyvert.LOG_DIR = log_dir

    pyvert.QUIET = args.quiet
    pyvert.VERBOSE = args.verbose


def main():
    """
    Entry point. Try to parse arguments and initialize application.
    """

    # set locales
    try:
        locale.setlocale(locale.LC_ALL, "")
        pyvert.SYS_ENCODING = locale.getpreferredencoding()
    except (locale.Error, IOError):
        pass

    if not pyvert.SYS_ENCODING or pyvert.SYS_ENCODING != 'UTF-8':
        pyvert.SYS_ENCODING = 'UTF-8'

    # fixed paths for pyvert
    if hasattr(sys, 'frozen'):
        pyvert.FULL_PATH = os.path.abspath(sys.executable)
    else:
        pyvert.FULL_PATH = os.path.abspath(__file__)

    pyvert.PROG_DIR = os.path.dirname(pyvert.FULL_PATH)

    parse_arguments()

    # setup logger
    logger.initLogger(console=not pyvert.QUIET, log_dir=pyvert.LOG_DIR,
                      verbose=pyvert.VERBOSE)

    logger.info('Starting pyvert (v{}.{}{})'.format(version.MAJOR,
                version.MINOR, version.MICRO))
    logger.debug('OS: {system} ({release})'.format(
                system=platform.system(), release=platform.release()))
    logger.debug('Python: {v.major}.{v.minor}.{v.micro}'.format(
                v=sys.version_info))
    logger.debug('Pyvert configuration files:')
    logger.debug('  Configuration Directory: {}'.format(
                 pyvert.CONFIG_DIR))
    logger.debug('  Data Directory: {}'.format(pyvert.DATA_DIR))
    logger.debug('  Log File: {0}/{1}'.format(pyvert.LOG_DIR, 'pacvert.log'))
    logger.debug('Arguments: {}'.format(sys.argv[1:]))
    logger.debug('')

    pyvert.CONFIG = Config()
    print(pyvert.CONFIG.get_all_variables())
    pyvert.CONFIG.save_config_file(os.path.join(pyvert.DATA_DIR, 'config.json'))
    pyvert.CONFIG.load_config_file(os.path.join(pyvert.DATA_DIR, 'config.json'))

    pyvert.CURRENT_VERSION = versioncheck.get_local_version()[0]

    versioncheck.get_remote_version()

if __name__ == "__main__":
    main()
