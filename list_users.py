#!/usr/bin/python

import sys
sys.path.append("MemberDB")
import MemberDatabase
import Role
import Group
import Member
import helper

mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    members = mdb.search_users()
    # Print results
    for member in members:
        print "SN:          " + member.get_full_name()
        print "CN:          " + str(member.get_lidnummer())
        print "E-mail:      " + member.get_mail()
        print "Afdeling:    " + member.get_afdeling()
        if member.is_user():
            print "Username:    " + member.get_username()
            print "Rollen:      " + str(member.role_list())
        print ""
