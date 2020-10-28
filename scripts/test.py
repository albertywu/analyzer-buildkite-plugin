#!/usr/bin/env python

import os
import unittest
from job import get_root
from subprocess import call
from shutil import rmtree
from textwrap import dedent


class TestCli(unittest.TestCase):
  root = get_root()

  def test_failing_cmd(self):
    step = "test_failing_cmd"
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type exitcode \
      --args '{"category":"foo", "subcategory": "bar"}' \
      false
    """ % { "root": TestCli.root, "step": step }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 1)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, step)), True)
    with open("%s/artifacts/analysis/failure" % TestCli.root) as f:
      failure = f.read()
      self.assertEqual(failure, "foo bar")

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_passing_cmd(self):
    step = "test_passing_cmd"
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type exitcode \
      --args '{"category":"foo", "subcategory": "bar"}' \
      true
    """ % { "root": TestCli.root, "step": step }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 0)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, step)), True)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/failure" % TestCli.root), False)

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_multiple_steps(self):
    stepA = "step_A"
    stepB = "step_B"
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(stepA)s \
      --type exitcode \
      --args '{"category":"a", "subcategory": "b"}' \
      true

    %(root)s/tools/analysis/job.py \
      --step %(stepB)s \
      --type exitcode \
      --args '{"category":"c", "subcategory": "d"}' \
      false
    """ % { "root": TestCli.root, "stepA": stepA, "stepB": stepB }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 1)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, stepA)), True)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, stepB)), True)
    with open("%s/artifacts/analysis/failure" % TestCli.root) as f:
      failure = f.read()
      self.assertEqual(failure, "c d")

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_heredoc(self):
    step = "testing_heredoc"
    script = """\
    <<SCRIPT
    set -e
    echo "hi"
    echo "bye"
    false
    echo "ho"
    SCRIPT
    """
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type exitcode \
      --args '{"category":"a", "subcategory": "b"}' \
      %(script)s
    """ % { "root": TestCli.root, "step": step, "script": dedent(script) }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 1)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, step)), True)
    with open("%s/artifacts/analysis/failure" % TestCli.root) as f:
      failure = f.read()
      self.assertEqual(failure, "a b")
    with open("%s/artifacts/analysis/%s.log" % (TestCli.root, step)) as f:
      log = f.read()
      self.assertEqual(log, "hi\nbye\n")

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_sq_user_fail(self):
    step = "test_sq_user_fail"
    script = """\
    <<SCRIPT
    echo "applying diff 000..."
    echo "applying diff 001..."
    echo "The previous cherry-pick is now empty, possibly due to conflict resolution."
    exit 1
    SCRIPT
    """
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type sq_apply_diffs \
      %(script)s
    """ % { "root": TestCli.root, "step": step, "script": dedent(script) }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 1)
    with open("%s/artifacts/analysis/failure" % TestCli.root) as f:
      failure = f.read()
      self.assertEqual(failure, "user_failure diff_already_landed")

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_sq_infra_fail(self):
    step = "test_sq_infra_fail"
    script = """\
    <<SCRIPT
    echo "applying diff 000..."
    echo "applying diff 001..."
    exit 128
    SCRIPT
    """
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type sq_apply_diffs \
      %(script)s
    """ % { "root": TestCli.root, "step": step, "script": dedent(script) }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 128)
    with open("%s/artifacts/analysis/failure" % TestCli.root) as f:
      failure = f.read()
      self.assertEqual(failure, "infra_failure sq_apply_diffs")

    rmtree("%s/artifacts/analysis" % TestCli.root)

  def test_sq_passing(self):
    step = "test_sq_passing"
    script = """\
    <<SCRIPT
    echo "applying diff 000..."
    echo "applying diff 001..."
    SCRIPT
    """
    cmd = """
    %(root)s/tools/analysis/job.py \
      --step %(step)s \
      --type sq_apply_diffs \
      %(script)s
    """ % { "root": TestCli.root, "step": step, "script": dedent(script) }
    exitcode = call(cmd, shell=True)

    self.assertEqual(exitcode, 0)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/%s.log" % (TestCli.root, step)), True)
    self.assertEqual(os.path.exists("%s/artifacts/analysis/failure" % TestCli.root), False)

    rmtree("%s/artifacts/analysis" % TestCli.root)


if __name__ == '__main__':
  unittest.main()
