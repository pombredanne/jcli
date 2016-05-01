# Copyright 2016 Arie Bregman
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
from executor.job import Job
import getpass
import sys


def get_version():
    """Returns jeni version."""
    return "Jeni 0.0.1"


def create_parser():
    """Returns argument parser"""

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--user', '-u', default=getpass.getuser(),
                               help='username')
    parent_parser.add_argument('--debug', required=False, action='store_true',
                               dest="debug", help='debug flag')

    main_parser = argparse.ArgumentParser()
    jeni_subparsers = main_parser.add_subparsers(title="jeni",
                                                 dest="main_command")

    job_parser = jeni_subparsers.add_parser("job", parents=[parent_parser])
    job_action_subparser = job_parser.add_subparsers(title="action",
                                                     dest="job_command")

    job_list_parser = job_action_subparser.add_parser(
        "list", help="list job(s)", parents=[parent_parser])
    job_list_parser.add_argument('name(s)', help='job(s) name(s)')

    job_delete_parser = job_action_subparser.add_parser(
        "delete", help="delete job", parents=[parent_parser])
    job_delete_parser.add_argument('name(s)', help='job(s) name(s)')

    return main_parser


def main():
    """Jeni Main Entry."""

    parser = create_parser()
    args = parser.parse_args()

    if args.main_command == 'job':
        job_executor = Job(args.job_command)
        job_executor.run()

    print("Jeni is not ready yet. Try again at 2017.")

if __name__ == '__main__':
    sys.exit(main())