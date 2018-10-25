import logging
import optparse
from argparse import Namespace

from cmd2 import Cmd
from elrc_client.client import ELRCShareClient


class ELRCShell(Cmd):
    prompt = '(ELRC Client) # '
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

    def do_get_json(self, args):
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return

        for r in arg_list:
            print(self.client.get_resource(r, as_json=True, pretty=options.pretty))
            print('')

    def do_my_resources(self, args):
        print(self.client.get_my_resources(as_json=True))

    def do_create(self, args):
        """
            Create a new resource description from an xml file, or multiple description from a zip archive
            containing valid ELRC-SHARE xml files.
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

        for arg in arg_list:
            self.client.download_data(arg, destination=options.destination or '')
        return

    def do_upload(self, args):
        try:
            (options, arg_list) = self.parser.parse_args(args.split())
        except (optparse.BadOptionError, optparse.OptionValueError):
            return

        for arg in arg_list:
            self.client.upload_data(arg, data_file=options.data_file or '')
        return

shell = ELRCShell()
# for a in shell.alias_list:
#     shell.alias_create(a)
shell.cmdloop()
