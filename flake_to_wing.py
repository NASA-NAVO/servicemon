#!/Users/donald/anaconda/envs/servicemon_env/bin/python
import sys
import subprocess
import re

def version_only():
    version_only = False
    for a in sys.argv[1:]:
        if a == '--version':
            version_only = True
    return version_only

def get_input_files():
    files = []
    for a in sys.argv[1:]:
        if not a.startswith('-'):
            files.append(a)
    return files

def run_flake(input_files):
    result = subprocess.run(['/Users/donald/anaconda/envs/servicemon_env/bin/flake8',
        '--max-line-length=120', input_files[0]], stdout=subprocess.PIPE, universal_newlines=True)

    return result

def flake_to_wing(flakeout):
    pylint_out = ''
    lines = flakeout.split('\n')
    for i, line in enumerate(lines):

        parts = line.split(':')
        if line.startswith('/') and len(parts) == 4:
            abspath = parts[0]
            lineno = parts[1]
            colno = parts[2]
            msg_info = {
                'msg_id': 'E000',
                'msg': 'Unknown message'
            }
            match = re.match(r'\s*(?P<msg_id>[^\s]*)\s+(?P<msg>.*)', parts[3])
            if match is not None:
                msg_info.update(match.groupdict())

            pylint_out += f"{msg_info['msg_id']}:::::{abspath}:::::{lineno}:::::{colno}:::::{msg_info['msg']}\n"

    pylint_out += """
------------------------------------------------------------------
Your code has been rated at 6.38/10 (previous run: 6.79/10, -0.41)
    """

    return pylint_out

def runit():
    if version_only():
        print("""pylint 2.2.2
astroid 2.1.0
Python 3.6.6 |Anaconda, Inc.| (default, Jun 28 2018, 11:07:29)
""")
    else:
        input_files = get_input_files()
        flake_result = run_flake(input_files)
        wing_result = flake_to_wing(flake_result.stdout)
        print(wing_result)


if __name__ == '__main__':
    runit()
