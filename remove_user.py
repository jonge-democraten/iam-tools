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
    usage = """./makeuser.py <lidnummer> <username>"""
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("I require two arguments")
    lidnummer = str(args[0])
    username = str(args[1])
    
    # Check validity of arguments
    if not Member.is_valid_username(username):
        parser.error("Username contains illegal characters.")
    if not Member.is_valid_lidnummer(lidnummer):
        parser.error("Lidnummer is not numerical. Remember: lidnummer first, then username. Aborting...")
    
    # The function make_user also checks whether the provided lidnummer is actually a user.
    member = Member.Member(l,s,int(lidnummer))
    if not member.exists():
        helper.logger.error("User with this lidnummer does not exist. Aborting...")
        sys.exit()
    if len(member.role_list()) > 0:
        helper.logger.error("User has roles. Remove roles of user before removing user. Aborting...")
        sys.exit()
    try:
        password = member.remove_user(lidnummer, username)
    except Member.UsernameError, e:
        helper.logger.error(e)
        sys.exit()
    except Member.LidnummerError, e:
        helper.logger.error(e)
        sys.exit()
    except Member.MemberError, e:
        helper.logger.error(e)
        sys.exit()
    helper.logger.info("User status and username %s were successfully taken away from member %s (%s)" % (username, member.get_full_name(), lidnummer))
