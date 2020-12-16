import sys
sys.path.append('..')

import asyncio

import typing
from termcolor import cprint
from nubia import command, argument, context
from prettytable import PrettyTable

# app settings
from lnma import db, create_app
from lnma.models import *
from lnma import dora
from lnma import ss_state

# app for using LNMA functions and tables
app = create_app()
db.init_app(app)
app.app_context().push()


@command("overview")
def overview():
    """
    Show the overview of current database status.
    """

    cprint("So ... let's see how many data we have: \n", "red")

    # count the projects
    n_projects = Project.query.count()

    table = PrettyTable([
        'Table', '# Records'
    ])
    
    # the USAFacts county covid
    table.add_row([
        '- projects', n_projects
    ])

    print(table)


@command("be-blocked")
def be_blocked():
    """
    This command is an example of command that blocked in configerator.
    """

    cprint("If you see me, something is wrong, Bzzz", "red")


@command
@argument("number", type=int)
async def triple(number):
    "Calculates the triple of the input value"
    cprint("Input is {}".format(number))
    cprint("Type of input is {}".format(type(number)))
    cprint("{} * 3 = {}".format(number, number * 3))
    await asyncio.sleep(2)


@command
@argument("style", description="Pick a style", choices=["test", "toast", "toad"])
@argument("stuff", description="more colors", choices=["red", "green", "blue"])
@argument("code", description="Color code", choices=[12, 13, 14])
def pick(style: str, stuff: typing.List[str], code: int):
    """
    A style picking tool
    """
    cprint("Style is '{}' code is {}".format(style, code), "yellow")


@command(aliases=["lookup"])
@argument("hosts", description="Hostnames to resolve", aliases=["i"])
@argument("bad_name", name="nice", description="testing")
def lookup_hosts(hosts: typing.List[str], bad_name: int):
    """
    This will lookup the hostnames and print the corresponding IP addresses
    """
    ctx = context.get_context()
    cprint("Input: {}".format(hosts), "yellow")
    cprint("Verbose? {}".format(ctx.verbose), "yellow")
    for host in hosts:
        cprint("{} is {}".format(host, socket.gethostbyname(host)))

    # optional, by default it's 0
    return 0