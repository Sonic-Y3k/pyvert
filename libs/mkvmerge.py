import os.path
import os
import re
import signal
from urllib3.util import parse_url
from subprocess import Popen, PIPE
import logging
import locale
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring

logger = logging.getLogger(__name__)

console_encoding = locale.getdefaultlocale()[1] or 'UTF-8'

class MKVMergeError(Exception):
    def __init__(self, message, cmd, output, details=None, pid=0):
        """
        @param    message: Error message.
        @type     message: C{str}

        @param    cmd: Full command string used to spawn mkvmerge.
        @type     cmd: C{str}

        @param    output: Full stdout output from the mkvmerge command.
        @type     output: C{str}

        @param    details: Optional error details.
        @type     details: C{str}
        """
        super(MKVMergeError, self).__init__(message)

        self.cmd = cmd
        self.output = output
        self.details = details
        self.pid = pid

    def __repr__(self):
        error = self.details if self.details else self.message
        return ('<MKVMergeError error="%s", pid=%s, cmd="%s">' %
                (error, self.pid, self.cmd))

    def __str__(self):
        return self.__repr__()

class MKVMerge(object):
    """
    MKVMerge wrapper object, takes care of calling the mkvmerge binary,
    passing options and parsing the output.

    >>> f = MKVMerge()
    """
    def __init__(self, mkvmerge_path=None):
        """
        Initialize a new MKVMerge wrapper object. Optional parameters specify
        the paths to mkvmerge.
        """

        self.current_process = None

        def which(name):
            path = os.environ.get('PATH', os.defpath)
            for d in path.split(':'):
                fpath = os.path.join(d, name)
                if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                    return fpath
            return None

        if mkvmerge_path is None:
            mkvmerge_path = 'mkvmerge'
            
        if '/' not in mkvmerge_path:
            mkvmerge_path = which(mkvmerge_path) or mkvmerge_path
            
        self.mkvmerge_path = mkvmerge_path
        
        if not os.path.exists(self.mkvmerge_path):
            raise MKVMergeError("mkvmerge binary not found: " + self.mkvmerge_path)
    
    @staticmethod
    def _spawn(cmds, stdin=PIPE):
        logger.debug('Spawning mkvmerge with command: ' + ' '.join(cmds))
        return Popen(cmds, shell=False, stdin=stdin, stdout=PIPE, stderr=PIPE,
                     close_fds=True)

    def stop(self):
        if self.current_process:
            try:
                self.current_process.terminate()
            except (OSError, AttributeError):
                raise MKVMergeError("Can't stop MKVMerge")
    
    def is_url(self, url):
        #: Accept objects that have string representations.
        try:
            url = unicode(url)
        except NameError:
            # We're on Python 3.
            url = str(url)
        except UnicodeDecodeError:
            pass

        # Support for unicode domain names and paths.
        scheme, auth, host, port, path, query, fragment = parse_url(url)

        if not scheme or not host:
            return False

        # Only want to apply IDNA to the hostname
        try:
            host = host.encode('idna').decode('utf-8')
        except UnicodeError:
            return False

        return True
    
    def merge(self, infiles, outfile, opts, timeout=10, nice=None, get_output=False, title=None):
        """
        """
        cmds = [self.mkvmerge_path, '-o', outfile]
        count = 0
        for i in infiles:
            if not os.path.exists(i) and not self.is_url(i):
                raise MKVMergeError("Input file doesn't exist: " + i)

            if i in opts:
                cmds += opts[i]
            
            cmds.append(i)
                
        return self._run_mkvmerge(cmds, timeout=timeout, nice=nice, get_output=get_output, title=title)
        
    def _run_mkvmerge(self, cmds, timeout=10, nice=None, get_output=False, title=None):
        if nice is not None:
            if 0 < nice < 20:
                cmds = ['nice', '-n', str(nice)] + cmds
            else:
                raise MKVMergeError("Invalid nice value: "+str(nice))

        try:
            p = self._spawn(cmds)
        except OSError:
            raise MKVMergeError('Error while calling mkvmerge binary')
            
        if timeout:
            def on_sigvtalrm(*_):
                try:
                    signal.signal(signal.SIGVTALRM, signal.SIG_DFL)
                except ValueError:
                    pass
                if p.poll() is None:
                    p.kill()
                raise Exception('timed out while waiting for mkvmerge')

            try:
                signal.signal(signal.SIGVTALRM, on_sigvtalrm)
            except ValueError:
                pass
                
        yielded = False
        buf = ''
        total_output = ''
        pat = re.compile(r'[a-zA-Z]*.\s+(\d*).*')
        
        def get_res(out):
            tmp = pat.findall(out)
            if len(tmp) == 1:
                percspec = tmp[0]
                return int(percspec)
            return None
            
        while True:
            if timeout:
                try:
                    signal.setitimer(signal.ITIMER_VIRTUAL, timeout)
                except ValueError:
                    pass

            ret = p.stdout.read(10)

            if timeout:
                try:
                    signal.setitimer(signal.ITIMER_VIRTUAL, 0)
                except ValueError:
                    pass

            if not ret:
                break

            ret = ret.decode(console_encoding, "replace")
            total_output += ret
            buf += ret
            
            if '\r' in buf:
                line, buf = buf.split('\r', 1)
                percspec = get_res(line)
                if percspec is not None:
                    yielded = True
                    yield percspec
        if not yielded:
            # There may have been a single time, check it
            percspec = get_res(total_output)
            if percspec is not None:
                yielded = True
                yield percspec

        if timeout:
            try:
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
            except ValueError:
                pass

        p.communicate()  # wait for process to exit
        
        if total_output == '':
            raise MKVMergeError('Error while calling mkvmerge binary')

        cmd = ' '.join(cmds)
        if '\n' in total_output:
            line = total_output.split('\n')[-2]

            if 'Signal' in line or 'signal' in line:
                # Received signal 15: terminating.
                raise MKVMergeError(
                    line.split(':')[0], cmd, total_output, pid=p.pid)
            if not yielded:
                raise MKVMergeError('Unknown mkvmerge error', cmd,
                                    total_output, line, pid=p.pid)
            if get_output:
                yield total_output
        if p.returncode != 0:
            raise MKVMergeError('Exited with code %d' % p.returncode, cmd,
                                total_output, pid=p.pid)