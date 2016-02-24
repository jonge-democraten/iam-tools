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
    usage = "./admin_delete_oob_member.py <memberID>"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("I require one argument")
    memberId = str(args[0])

    # Check validity of arguments
    if not Member.is_valid_lidnummer(memberId):
        parser.error("Not a valid member ID. Aborting...")
    member = Member.Member(l,s,int(memberId))
    group = Group.Group(l,s,"type-outofband")
    if not member.exists():
        helper.logger.error("Member %s does not exist. Aborting..." % memberId)
        sys.exit()
    if not member in group:
        helper.logger.error("Member %s is not an out-of-band member. Aborting..." % memberId)
        sys.exit()

    # Delete out-of-band member
    fullName = member.get_full_name()
    member.delete()
    helper.logger.info("Deleted out-of-band member %s (%s)." % (fullName, memberId))
