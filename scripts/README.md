# Job Analysis CLI tool

Analyzes shell executable code by examining exit status & log output of shell execution.

The analyzer wraps the shell code to be analyzed. The general form of the API is as follows:

```
analyze \
  --step <STEP_NAME> \
  --type <ANALYZER_NAME> \
  --args <ANALYZER_ARGS> \
  -- <COMMAND / SHELL SCRIPT / STDIN>
```

Currently, a single analyzer type `exitcode` exists which will annotate failures with the specified category and subcategory. If an `exitcode` analyzer detects failure, it will store the specified { category, subcategory } of the failure in `artifacts/analysis/failure`. Upon completion of each Buildkite job, any failure results in `artifacts/analysis/failure` will be uploaded to S3 for downstream processing.

Additional analyzers like log analyzers can be supported if the need arises.

## Example 1: wrap a bash command

```
lang=shell
analyze \
  --step run_lint \
  --type exitcode \
  --args '{"category":"UserFailure", "subcategory": "lint"}' \
  -- jazelle lint --cwd "$PACKAGE" --color
```

## Example 2: wrap a shell script

```
lang=shell
analyze \
  --step do_something \
  --type exitcode \
  --args '{"category":"UserFailure", "subcategory": "do_something"}' \
  -- ./do_something.sh
```

## Example 2: wrap a sequence of bash commands

```
lang=shell
analyze \
  --step heredoc_example \
  --type exitcode \
  --args '{"category":"UserFailure", "subcategory": "heredoc_example"}' \
  <<CMD
set -e
echo "hi"
echo "ho"
false
echo "this will never run, since the previous command failed"
CMD
```

An integration test suite for this CLI tool is located at test.py
