#!/usr/bin/env python3

# Copyright (c) Huan He (hehuan2112@gmail.com)
# All rights reserved.
#
# This source code is licensed under the Apache 2.0 license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import json
import pathlib
import shutil
import argparse

from scene import p_IO_default

def kacha(keystr, cq_abbr, output_path):
    '''
    Take a snapshot
    '''
    # first of all, remove the old kacha?
    prj_path = os.path.join(
        output_path, keystr, cq_abbr
    )
    if os.path.exists(prj_path):
        shutil.rmtree(prj_path)
        print('* removed existed %s pub site data' % (
            keystr
        ))
    
    if keystr == 'IO':
        if cq_abbr == 'default':
            p_IO_default.kacha(prj_path)
    
    else:
        print('* not defined [%s].[%s]' % (
            keystr, cq_abbr
        ))

    return 1



if __name__ == "__main__":
    parser = argparse.ArgumentParser('LNMA Snapshoter')
    parser.add_argument("--keystr", type=str,
        help="The keystr for the project. Use `all` for all projects"
    )
    parser.add_argument("--cq", type=str, default="default",
        help="The cq abbr. default is default"
    )
    parser.add_argument("--output", type=str,
        help="The output path for the static website"
    )

    args = parser.parse_args()

    if args.keystr == 'all':
        pass

    else:
        kacha(args.keystr, args.cq, args.output)

    print('* done snapshot!')