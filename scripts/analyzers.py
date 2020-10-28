import json


SUCCESS_RESULT = ("success", None)


# this analyzer type allows users to tag failures with (category, subcategory) of their choosing
# every result is a (category, subcategory) pair
def analyze_exitcode(config):
  args = json.loads(config['args'])
  if config['exit_code'] != 0:
    return (args['category'], args['subcategory'])
  else:
    return SUCCESS_RESULT

# categorizes failures when applying diffs for SQ
def analyze_sq_apply_diffs(config):
  already_landed_error = 'The previous cherry-pick is now empty, possibly due to conflict resolution.'

  if config['exit_code'] != 0:
    with open(config['log_path']) as f:
      log = f.read()
      if already_landed_error in log:
        return ('user_failure', 'diff_already_landed')
    return ('infra_failure', 'sq_apply_diffs')
  else:
    return SUCCESS_RESULT
