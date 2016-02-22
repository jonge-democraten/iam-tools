#!/usr/bin/python

import sys
sys.path.append("MemberDB")
import MemberDatabase
import Role
import Group
import Member
import helper
from optparse import OptionParser
import smtplib
from email.mime.text import MIMEText
import errno
import socket
import ldap
import make_user

mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    # Parse arguments
    usage = """./make_user.py <full name> <username> <passwordType>
    
    Password types are as follows:
        
        0 -> 8 characters, uppercase, lowercase, digits, special
        1 -> 9 characters, uppercase, lowercase
        2 -> 11 characters, lowercase
        3 -> 5 random Dutch words, lowercase"""
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) < 3:
        parser.error("I require three arguments")
    fullName = ' '.join(args[:-2])
    username = str(args[-2])
    try:
        passwordType = int(str(args[-1]))
    except ValueError:
        parser.error("passwordType should be a digit.")
    
    # Check validity of arguments
    if passwordType < 0 or passwordType > 3:
        parser.error("passwordType should be 0, 1, 2 or 3.")
    if not Member.is_valid_username(username):
        parser.error("Username contains illegal characters.")
    if not Member.is_valid_full_name(fullName):
        parser.error("Full name contains invalid characters.")
    
    # Determine which Member is meant by fullName
    try:
        members = mdb.search_members("sn=*%s*" % fullName)
    except ldap.NO_RESULTS_RETURNED:
        helper.logger.error("No member found by that name.")
        sys.exit()
    if len(members) > 1:
        helper.logger.error("Name does not uniquely identify Several members match the given full name. Aborting...")
        sys.exit()
    else:
        member = members[0]
        
        # The function make_user also checks whether the provided lidnummer is not already a user.
        try:
            password = member.make_user(username, passwordType)
        except Member.UsernameError:
            helper.logger.error("Username has been used before. Choose a different username.")
            sys.exit()
        except Member.MemberError, e:
            helper.logger.error(e)
            sys.exit()
        except Member.LidnummerError, e:
            helper.logger.error(e)
            sys.exit()
        
        # Send confirmation e-mail
        fullName = member.get_full_name()
        mail = member.get_mail()
        make_user.send_confirmation_email(fullName, username, password, mail)
    
        helper.logger.info("Promoted member %s (%s) to user %s" % (fullName, member.get_lidnummer(), username))
        
