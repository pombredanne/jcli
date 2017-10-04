#!/usr/bin/env python
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

import collections
import json
import logging
import six
from time import sleep
import yaml

from jcli import exception
from jcli.executor.server import Server

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


def allof(arg):
    """Allows to parse params that could be strings or lists.

    String itself is iterable, so we need to avoid parsing
    each char.
    """

    if isinstance(arg, collections.Iterable) and \
            not isinstance(arg, six.string_types):
        return arg
    else:
        return [arg]


class Job(Server):
    """Manages job command execution"""

    def __init__(self, url, user, password, job_args=None, action=None):
        super(Job, self).__init__(url, user, password)
        self.action = action
        self.job_args = job_args

    def get_jobs_names(self):
        """Returns list of all jobs name"""

        jobs_names = []

        jobs = self.server.get_jobs()
        if self.job_args.name:
            for name in allof(self.job_args.name):
                for job_object in jobs:
                    if name in job_object['name']:
                        jobs_names.append(job_object['name'])
        else:
            for job_object in jobs:
                jobs_names.append(job_object['name'])

        return sorted(set(jobs_names))

    def delete_job(self):
        """Removes job from the server"""

        if self.job_args.name:
            for name in allof(self.job_args.name):
                try:
                    self.server.delete_job(name)
                    logger.info("Removed job: {}".format(name))
                except Exception as e:
                    raise exception.JcliException(e)
        else:
            logger.info("No name provided. Exiting...")

    def disable_job(self):
        """Disables job"""

        for name in allof(self.job_args.name):

            try:
                self.server.disable_job(name)

            except Exception:
                raise exception.JcliException(
                    "No such job: {}".format(name))

            logger.info("Disabled job: {}".format(name))

    def enable_job(self):
        """Enables job"""

        for name in allof(self.job_args.name):

            try:
                self.server.enable_job(name)

            except Exception:
                raise exception.JcliException(
                    "No such job: {}".format(name))

            logger.info("Enabled job: %s", name)

    def build_job(self):
        """Starts job build"""

        for name in allof(self.job_args.name):

            if self.job_args.parameters:
                self.server.build_job(name,
                                      json.loads(self.job_args.parameters))
                logger.info("Starting job build with parameters: %s",
                            name)
            elif self.job_args.params_yml:
                with open(self.job_args.params_yml, 'r') as f:
                    self.server.build_job(name,
                                          json.loads(json.dumps(yaml.load(f))))
                logger.info("Starting job build with parameters: %s",
                            name)
            else:
                self.server.build_job(name, json.loads('{"delay": "0sec"}'))
                logger.info("Starting job build without params: %s",
                            name)

    def copy_job(self):
        """Copies job"""

        try:
            self.server.copy_job(self.job_args.source_job_name,
                                 self.job_args.dest_job_name)
            logger.info("Done copying: {}. The new job is called: {}".format(
                self.job_args.source_job_name, self.job_args.dest_job_name))
        except Exception as e:
            raise exception.JcliException(e)

    def last_build(self):
        """Output information on last build"""

        try:
            last_build_number = self.server.get_job_info(
                self.job_args.name)['lastCompletedBuild']['number']
            build_info = self.server.get_job_info(
                self.job_args.name, last_build_number)
            logger.info(
                "=================== Last build summary ===================\n")
            logger.info("Build Number: {}".format(last_build_number))

            # Log SCMs
            logger.info("\nSCMs:\n")
            for scm in build_info['scm']['configuredSCMs']:
                for info in scm['userRemoteConfigs']:
                    logger.info("  Url: {}".format(info['url']))
                    logger.info(
                        "  Refspec: {}\n  -----".format(info['refspec']))

            # Log Parameters
            logger.info("\n\nParameters:\n")
            for param in build_info['property'][6]['parameterDefinitions']:
                logger.info("  Parameter: {}\n  Value: {}\n  -----".format(
                    param['defaultParameterValue']['name'],
                    param['defaultParameterValue']['value']))

            # Log general build info
            logger.info("\n\nBuild Duration: {}".format(
                build_info['lastBuild']['duration']))
            logger.info("Built on slave: {}".format(
                build_info['lastBuild']['builtOn']))
            logger.info("URL: {}".format(build_info['lastBuild']['url']))
            logger.info(
                "\nResult: {}".format(build_info['lastBuild']['result']))

        except Exception as e:
            raise exception.JcliException(e)

    def count_jobs(self):
        """Returns number of jobs on Jenkins."""
        if self.job_args.string:
            jobs_count = 0
            jobs = self.server.get_jobs()
            for job_object in jobs:
                if self.job_args.string in job_object['name']:
                    jobs_count += 1
            logger.info("Number of jobs contain the string %s: %s",
                        self.job_args.string, jobs_count)

        else:
            logger.info("Number of jobs: %s", self.server.jobs_count())

    def build_number(self):
        return int(self.server.get_job_info(
            self.job_args.name)['lastCompletedBuild']['number'])

    def console_output(self):
        """Logs job's console output"""
        if self.job_args.build_num:
            build_number = self.job_args.build_num
        elif self.job_args.current:
            build_number = self.build_number() + 1
            while build_number != self.build_number():
                logger.info(
                    self.server.get_build_console_output(self.job_args.name,
                                                         build_number))
                sleep(5)
        else:
            logger.info(self.server.get_build_console_output(
                        self.job_args.name,
                        self.build_number()))

    def run(self):
        """Executes chosen action."""

        if self.action == 'list':
            for job in self.get_jobs_names():
                print(job)

        if self.action == 'count':
            self.count_jobs()

        if self.action == 'delete':
            self.delete_job()

        if self.action == 'build':
            self.build_job()

        if self.action == 'copy':
            self.copy_job()

        if self.action == 'disable':
            self.disable_job()

        if self.action == 'enable':
            self.enable_job()

        if self.action == 'last_build':
            self.last_build()

        if self.action == 'output':
            self.console_output()
