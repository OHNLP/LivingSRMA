#!/usr/bin/env python3

# Copyright (c) Huan He (hehuan2112@gmail.com)
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#

import sys
import commands
from nubia import Nubia, Options
from admin_plugin import AdminPlugin


if __name__ == "__main__":
    plugin = AdminPlugin()
    shell = Nubia(
        name="LNMA_ADMIN",
        command_pkgs=commands,
        plugin=plugin,
        options=Options(
            persistent_history=False
        ),
    )
    sys.exit(shell.run())