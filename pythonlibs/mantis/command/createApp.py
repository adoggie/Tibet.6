#coding:utf-8


"""
usage:
    export PYTHONPATH=~/Desktop/Projects/Branches
    python -m mantis.command.createApp MyApp ./

"""
import sys
from mantis.command import createApp

createApp(*sys.argv[1:])