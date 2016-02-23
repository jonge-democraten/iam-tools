#!/usr/bin/python

import sys
sys.path.append("MemberDB")
import MemberDatabase
import Role
import Group
import Member
import helper
from optparse import OptionParser


mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    # Parse arguments
    usage = "./admin_delete_role.py <role>"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("I require one argument")
    roleName = str(args[0])

    # Check validity of arguments
    if not Role.is_valid_role_name(roleName):
        parser.error("Not a valid role name. Aborting...")
    role = Role.Role(l,s,roleName)
    if not role.exists():
        helper.logger.error("Role %s does not exist. Aborting..." % roleName)
        sys.exit()

    # Delete role
    role.delete()
    helper.logger.info("Deleted role %s." % roleName)
