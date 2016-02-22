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


mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    # Parse arguments
    usage = """./reset_password.py <lidnummer> <passwordType> or ./resetpassword.py <username> <passwordType>
    
    Password types are as follows:
        
        0 -> 8 characters, uppercase, lowercase, digits, special
        1 -> 9 characters, uppercase, lowercase
        2 -> 11 characters, lowercase
        3 -> 5 random Dutch words, lowercase"""
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("I require two arguments.")
    numberOrName = str(args[0])
    try:
        passwordType = int(str(args[1]))
    except ValueError:
        parser.error("passwordType should be a digit.")
    
    # Check validity of arguments
    if passwordType < 0 or passwordType > 3:
        parser.error("passwordType should be 0, 1, 2 or 3.")
    if Member.is_valid_lidnummer(numberOrName):
        lidnummer = numberOrName
        member = Member.Member(l,s,int(lidnummer))
        if not member.exists():
            logger.error("Could not find lidnummer in MemberDatabase. Aborting...")
            sys.exit()
        elif not member.is_user():
            logger.error("Member is not a user. Promote him to user to set a password.")
            sys.exit()
        username = member.get_username()
    elif Member.is_valid_username(numberOrName):
        username = numberOrName
        try:
            member = Member.Member.from_username(l,s,username)
        except Member.UsernameError:
            logger.error("Could not find username in MemberDatabase. Aborting...")
            sys.exit()
    else:
        parser.error("This is neither a valid lidnummer, nor a valid username. Aborting...")
    
    # Calculate and set new password
    fullName = member.get_full_name()
    mail = member.get_mail()
    password = member.generate_password(passwordType)
    helper.logger.debug("Setting password for username %s (%s) to newly generated value." % (username, fullName))
    member.set_password(password)
    
    # Send new password to user
    msg = MIMEText("""Beste %s,

Er is een nieuw wachtwoord ingesteld voor je MijnJD-account. Je inloggegevens vind je hieronder. Bewaar ze goed, en houd ze geheim. Als je je wachtwoord nog eens vergeet, kan de Algemeen Secretaris van het Landelijk Bestuur je een nieuw wachtwoord geven.

  Gebruikersnaam: %s
  Wachtwoord: %s

Als je nog vragen hebt over dit systeem, neem dan contact op met het ICT-team op ict@jd.nl.

Hartelijke groeten,

Het ICT-team""" % (fullName, username, password))

    msg['Subject'] = "Wachtwoord-reset voor MijnJD-account"
    msg['From'] = "Jonge Democraten ICT-team <ict@jd.nl>"
    msg['To'] = "%s <%s>" % (fullName, mail)

    try:
        sm = smtplib.SMTP('localhost')
        sm.sendmail("ict@jd.nl", mail, msg.as_string())
        sm.quit()
    except socket.error, v:
        errorCode = v[0]
        if errorCode == errno.ECONNREFUSED:
            helper.logger.error("Could not send new password e-mail to %s: connection refused." % (fullName))

    helper.logger.info("Performed a password reset for %s (%s), username %s " % (fullName, member.get_lidnummer(), username))
