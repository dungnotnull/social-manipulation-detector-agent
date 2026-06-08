# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# sys.path prefixed to this
prepend_sys_path = .

# use env.py in this directory
%(here)s/env.py

# the output encoding used when revision files are written from script.py.mako
output_encoding = utf-8
