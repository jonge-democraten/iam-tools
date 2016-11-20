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
    usage = "./admin_create_oob_member.py <memberID> <full name> <email> <department> <username>"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 5:
        parser.error("I require five arguments")
    memberId = str(args[0])
    fullName = str(args[1])
    email = str(args[2])
    department = str(args[3])
    username = str(args[4])

    # Check validity of arguments
    if not Member.is_valid_lidnummer(memberId):
        parser.error("Not a valid member ID. Aborting...")
    if not Member.is_valid_full_name(fullName):
        parser.error("Not a valid full name. Aborting...")
    if not Member.is_valid_mail(email):
        parser.error("Not a valid email address. Aborting...")
    if not Member.is_valid_afdeling(department):
        parser.error("Not a valid department. Aborting...")
    if not Member.is_valid_username(username):
        parser.error("Not a valid username. Aborting...")
    newMember = Member.Member(l,s,int(memberId))
    if newMember.exists():
        helper.logger.error("Member %s already exists. Aborting..." % memberId)
        sys.exit()

    # Create out-of-band member
    newMember.create(fullName, email, department)
    newMember.make_user(username, 3)
    group = Group.Group(l,s,"type-outofband")
    group.add(newMember)
    helper.logger.info("Created out-of-band member %s (%s)." % (fullName, memberId))
