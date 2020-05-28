import subprocess

from jinja2 import Environment
from jinja2 import FileSystemLoader

from lnma.settings import *

def gen_rscript(rscript_tpl_folder, rscript_tpl, fn_rscript, r_params):
    jinja2_env = Environment(loader=FileSystemLoader(rscript_tpl_folder),
                             trim_blocks=True)
    tpl = jinja2_env.get_template(rscript_tpl)
    r_src_code = tpl.render(**r_params)

    with open(os.path.join(TMP_FOLDER, fn_rscript), 'w') as f:
        f.write(r_src_code)

    return r_src_code


def run_rscript(fn_rscript):
    cmd_r = '/usr/bin/Rscript'
    cmd = [cmd_r, fn_rscript]
    x = subprocess.check_output(cmd, universal_newlines=True, cwd=TMP_FOLDER)
    return 0