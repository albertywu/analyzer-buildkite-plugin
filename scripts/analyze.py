#!/usr/bin/env python

import os
import sys
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT, check_output, list2cmdline
from datetime import datetime
from analyzers import analyze_exitcode, analyze_sq_apply_diffs
import fileinput


def get_root():
    return check_output("git rev-parse --show-toplevel", shell=True, stderr=STDOUT).rstrip()


def analyze(config):
    if config['type'] == "exitcode":
        return analyze_exitcode(config)
    elif config['type'] == "sq_apply_diffs":
        return analyze_sq_apply_diffs(config)
    else:
        raise ValueError('unknown analyzer type %s' % config.type)


def wrapped_cmd(step, type, args, dir, cmd):
    log = "%s.log" % (step)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open("%s/%s" % (dir, log), 'w+') as f:
        start_time = get_timestamp()
        process = Popen(cmd, stdout=PIPE, stderr=STDOUT,
                        shell=True, executable="/bin/bash")
        for c in iter(lambda: process.stdout.read(1), ''):
            sys.stdout.write(c)
            f.write(c)
        end_time = get_timestamp()
        process.poll()
        exit_code = process.returncode
    config = {
        "step": step,
        "type": type,
        "args": args,
        "exit_code": exit_code,
        "log_path": "%s/%s" % (dir, log),
        "start_time": start_time,
        "end_time": end_time
    }
    if exit_code != 0:
        category, subcategory = analyze(config)
        with open("%s/failure" % dir, 'w+') as f:
            f.write("%s %s" % (category, subcategory))
    sys.exit(exit_code)


def get_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'


def parse_timestamp(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")


def main():
    parser = ArgumentParser(
        description='wrap a shell script invocation with analytics markers')
    parser.add_argument('--step', required=True,
                        help='unique identifier for this step')
    parser.add_argument('--type', required=True, choices=['exitcode', 'sq_apply_diffs'],
                        help='analyzer type (exitcode or sq_apply_diffs)')
    parser.add_argument('--args',
                        help='arguments for this analyzer (json string)')
    parser.add_argument('--dir', default="artifacts/analysis",
                        help='directory to deposit analysis results (relative to cwd)')
    parser.add_argument('rest', nargs='*',
                        help='pass all the rest to shell for execution')
    args = parser.parse_args()
    type, step, args, dir, rest = args.type, args.step, args.args, args.dir, args.rest

    dir_abs = "%s/%s" % (os.getcwd(), dir)

    if len(rest) == 0:
        # read from stdin if no command provided
        lines = ''
        for line in sys.stdin:
            lines += line
        wrapped_cmd(step, type, args, dir_abs, lines)
    else:
        cmd = list2cmdline(rest)
        wrapped_cmd(step, type, args, dir_abs, cmd)


if __name__ == "__main__":
    main()
