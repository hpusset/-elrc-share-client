# Copyright 2018 ILSP/Athena R.C. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the following
#     disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials
#     provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY ILSP/Athena R.C. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ILSP/Athena R.C. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of ILSP/Athena R.C.

import logging
import optparse
from argparse import Namespace

import sys

import os
from cmd2.clipboard import get_paste_buffer
from cmd2.cmd2 import Statekeeper
from cmd2.parsing import Statement

from cmd2 import Cmd, constants
from elrc_client.client import ELRCShareClient
from elrc_client.settings import DOWNLOAD_DIR


class ELRCShell(Cmd):
    prompt = '(ELRC Shell) # '
    client = ELRCShareClient()
    parser = optparse.OptionParser()
    # alias_list = [
    #     Namespace(command='!del', name='rm', command_args=[]),
    #     Namespace(command='!cd', name='cd', command_args=[]),
    #     Namespace(command='!dir', name='ls', command_args=[])
    # ]
    parser.add_option('-d', '--dest', dest='destination')
    parser.add_option('-f', '--file', dest='xml_file')
    parser.add_option('-z', '--zip', dest='data_file', default=None)
    parser.add_option('-p', '--pretty', dest='pretty', default=False, action='store_true')

    def _redirect_output(self, statement: Statement) -> None:
        """Handles output redirection for >, >>, and |.

        :param statement: a parsed statement from the user
        """
        import io
        import subprocess

        if statement.pipe_to:
            self.kept_state = Statekeeper(self, ('stdout',))

            # Create a pipe with read and write sides
            read_fd, write_fd = os.pipe()
            # Open each side of the pipe and set stdout accordingly
            # noinspection PyTypeChecker
            self.stdout = io.open(write_fd, 'w', encoding='utf-8')
            self.redirecting = True
            # noinspection PyTypeChecker
            subproc_stdin = io.open(read_fd, 'r')

            # We want Popen to raise an exception if it fails to open the process.  Thus we don't set shell to True.
            try:
                self.pipe_proc = subprocess.Popen(statement.pipe_to, stdin=subproc_stdin)
            except Exception as ex:
                # Restore stdout to what it was and close the pipe
                self.stdout.close()
                subproc_stdin.close()
                self.pipe_proc = None
                self.kept_state.restore()
                self.kept_state = None
                self.redirecting = False

                # Re-raise the exception
                raise ex
        elif statement.output:
            import tempfile
            if (not statement.output_to) and (not self.can_clip):
                raise EnvironmentError("Cannot redirect to paste buffer; install 'pyperclip' and re-run to enable")
            self.kept_state = Statekeeper(self, ('stdout',))
            self.kept_sys = Statekeeper(sys, ('stdout',))
            self.redirecting = True
            if statement.output_to:
                # going to a file
                mode = 'w'
                # statement.output can only contain
                # REDIRECTION_APPEND or REDIRECTION_OUTPUT
                if statement.output == constants.REDIRECTION_APPEND:
                    mode = 'a'
                try:
                    # Send to default output directory if only a filename is specified
                    if os.path.split(statement.output_to)[0] == '':
                        sys.stdout = self.stdout = open(os.path.join(DOWNLOAD_DIR, statement.output_to),
                                                        mode, encoding='utf-8')
                    else:
                        sys.stdout = self.stdout = open(statement.output_to, mode, encoding='utf-8')
                except OSError as ex:
                    self.perror('Not Redirecting because - {}'.format(ex), traceback_war=False)
                    self.redirecting = False
            else:
                # going to a paste buffer
                sys.stdout = self.stdout = tempfile.TemporaryFile(mode="w+")
                if statement.output == constants.REDIRECTION_APPEND:
                    self.poutput(get_paste_buffer())

    def do_exit(self, args):
        '''\tLogout and exit the shell'''
        return True

    def emptyline(self):
        pass

    def do_login(self, args):
        if not args:
            logging.error("No credentials provided!")
            return
        credentials = args.split()
        if len(credentials) != 2:
            logging.error("Invalid number of arguments. 2 required: username, password")
            return
        username = credentials[0]
        password = credentials[1]
        self.client.login(username, password)

    def do_logout(self, args):
        self.client.logout()

    def do_getj(self, args):
        """

        :param args:
        :return: A json represenatation of a resource's metadata record
        """
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return
        if arg_list:
            for r in arg_list:
                print(self.client.get_resource(r, as_json=True, pretty=options.pretty))
                print('')
        else:
            print(self.client.get_my_resources(as_json=True, pretty=options.pretty))
            print('')

    def do_getx(self, args):
        """

        :param args:
        :return: An XML represenatation of a resource's metadata record
        """
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return

        for r in arg_list:
            print(self.client.get_resource(r, as_xml=True, pretty=options.pretty))
            print('')

    def do_my_resources(self, args):
        print(self.client.get_my_resources(as_json=False))

    def do_create(self, args):
        """

        :param args: An ELRC-SHARE resource id or a space seperated list of resource ids
        :return:
        """
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return
        for r in arg_list:
            self.client.create_resources(r, dataset=options.data_file)

    def do_update(self, args):
        """
            Update a resource description from an xml file, or multiple description from a zip archive
            containing valid ELRC-SHARE xml files.
        """
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return
        for r in arg_list:
            self.client.update_resource(r, options.xml_file)

    def do_download(self, args):
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return

        if arg_list:
            for arg in arg_list:
                self.client.download_data(arg, destination=options.destination or '')
        else:
            self.client.get_my_resources()
        return

    def do_upload(self, args):
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return

        for arg in arg_list:
            self.client.upload_data(arg, data_file=options.data_file or '')
        return
