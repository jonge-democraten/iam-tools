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
    usage = "./give_role.py <role> <username>"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("I require two arguments")
    roleName = str(args[0])
    username = str(args[1])

    # Check validity of arguments
    if not Role.is_valid_role_name(roleName):
        parser.error("Not a valid role name. Aborting...")
    role = Role.Role(l,s,roleName)
    if not role.exists():
        helper.logger.error("Role %s does not exist. Aborting..." % roleName)
        sys.exit()
    if not Member.is_valid_username(username):
        parser.error("Not a valid username. Aborting...")
    helper.logger.debug("Looking up username %s." % username)
    try:
        member = Member.Member.from_username(l,s,username)
    except Member.UsernameError:
        helper.logger.error("Username %s does not exist. Aborting..." % username)
        sys.exit()
    if member in role.members():
        helper.logger.error("User %s already has role %s. Aborting..." % (username, roleName))
        sys.exit()
    
    # Grant role to user
    role.grant(member)
    helper.logger.info("Granted role %s to user %s." % (roleName, username))
