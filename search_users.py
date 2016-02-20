#!/usr/bin/python

import sys
sys.path.append("MemberDB")
import MemberDatabase
import Role
import Group
import Member
import Permission
import helper
from optparse import OptionParser

mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    # Define command-line options
    usage = """
    %prog options arguments
      -i :  in member id mode, argument is member id for which to search
      -n :  in name mode, argument is part of name for which to search
      -e :  in e-mail address mode, argument is part of e-mail address for which to search
      -u :  in username mode, argument is part of a username for which to search
      -a :  search all members, not just users"""
    parser = OptionParser(usage)
    parser.add_option(
        "-i", "--id", action="store_true", dest="id", help="search by member id")
    parser.add_option(
        "-n", "--name", action="store_true", dest="name", help="search by (part of) name")
    parser.add_option(
        "-e", "--email", action="store_true", dest="email", help="search by e-mail address")
    parser.add_option(
        "-u", "--username", action="store_true", dest="username", help="search by username")
    parser.add_option(
        "-a", "--all", action="store_true", dest="all", help="search all members, not just users")
    # Read options and check sanity 
    (options, args) = parser.parse_args()
    numoptions = 0
    if options.id:
        numoptions += 1
    if options.name:
        numoptions += 1
    if options.email:
        numoptions += 1
    if options.username:
        numoptions += 1
    if numoptions != 1:
        parser.error("Choose one of the options -i, -n, -u and -e.")
    if len(args) != 1:
        parser.error("Need 1 argument")
    
    # Construct the search filter
    searchFilter = ""
    
    if options.id:
        try:
            searchFilter = "cn=%s" % str(int(args[0]))
        except ValueError:
            parser.error("Lidnummer is not of correct form.")
            sys.exit()
        if not Member.is_valid_lidnummer_filter(searchFilter):
            parser.error("Lidnummer is not of correct form.")
            sys.exit()
    
    if options.name:
        naam = str(args[0])
        if not naam.startswith("*"):
            naam = "*"+naam
        if not naam.endswith("*"):
            naam = naam + "*"
        searchFilter = "sn="+naam
        if not Member.is_valid_full_name_filter(searchFilter):
            parser.error("Not a valid name part. Please replace diacritics with '*'.")
            sys.exit()

    if options.username:
        username = str(args[0])
        searchFilter = "uid=*"+username+"*"
        if not Member.is_valid_username_filter(searchFilter):
            parser.error("Not a valid username part. Aborting...")
            sys.exit()

    if options.email:
        email = str(args[0])
        searchFilter = "mail=*"+email+"*"
        if not Member.is_valid_mail_filter(searchFilter):
            parser.error("Not a valid part of an e-mail address. Aborting...")
            sys.exit()
    if searchFilter == "":
        parser.error("Invalid option.")
    
    # Search for users or members, depending on -a option.
    if options.all:
        members = mdb.search_members(searchFilter)
    else:
        members = mdb.search_users(searchFilter)
        
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