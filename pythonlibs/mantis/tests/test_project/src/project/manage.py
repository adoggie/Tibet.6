#!/usr/bin/env python


import os,sys
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,PATH+'/../')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)