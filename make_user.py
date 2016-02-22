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

def send_confirmation_email(fullName, username, password, mail):
    '''
    (str, str, str, str) -> None
    
    Sends a confirmation e-mail to a member who has just been promoted to user. The e-mail contains instructions and login credentials.
    '''
    msg = MIMEText("""Beste %s,

Er is voor jou een MijnJD-account aangemaakt. Met een MijnJD-account kun je op een aantal systemen van de Jonge Democraten inloggen met dezelfde inloggegevens. Jouw inloggegevens staan hieronder. Bewaar ze goed, en houd ze geheim. Als je je wachtwoord bent vergeten, kan de AS van het Landelijk Bestuur je een nieuw wachtwoord geven.

  Gebruikersnaam: %s
  Wachtwoord: %s

Op http://mijn.jongedemocraten.nl vind je een overzicht van plaatsen waar je met deze gegevens in kunt loggen. Daar vind je ook gebruikershandleidingen voor die systemen.

Als je nog vragen hebt over dit systeem, neem dan contact op met het ICT-team op ict@jd.nl.

Hartelijke groeten,

Het ICT-team""" % (fullName, username, password))
    
    msg['Subject'] = "Nieuw MijnJD-account aangemaakt"
    msg['From'] = "Jonge Democraten ICT-team <ict@jd.nl>"
    msg['To'] = "%s <%s>" % (fullName, mail)

    try:
        sm = smtplib.SMTP('localhost')
        sm.sendmail("ict@jd.nl", mail, msg.as_string())
        sm.quit()
    except socket.error, v:
        errorCode = v[0]
        if errorCode == errno.ECONNREFUSED:
            helper.logger.error("Could not send confirmation e-mail to %s: connection refused." % (fullName))

mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

if __name__ == "__main__":
    # Parse arguments
    usage = """./make_user.py <lidnummer> <username> <passwordType>
    
    Password types are as follows:
        
        0 -> 8 characters, uppercase, lowercase, digits, special
        1 -> 9 characters, uppercase, lowercase
        2 -> 11 characters, lowercase
        3 -> 5 random Dutch words, lowercase"""
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error("I require three arguments")
    lidnummer = str(args[0])
    username = str(args[1])
    try:
        passwordType = int(str(args[2]))
    except ValueError:
        parser.error("passwordType should be a digit.")
    
    # Check validity of arguments
    if passwordType < 0 or passwordType > 3:
        parser.error("passwordType should be 0, 1, 2 or 3.")
    if not Member.is_valid_username(username):
        parser.error("Username contains illegal characters.")
    if not Member.is_valid_lidnummer(lidnummer):
        parser.error("Lidnummer is not numerical. Remember: lidnummer first, then username. Aborting...")
    
    # The function make_user also checks whether the provided lidnummer is not already a user.
    member = Member.Member(l,s,int(lidnummer))
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
    
    send_confirmation_email(fullName, username, password, mail)

    helper.logger.info("Promoted member %s (%s) to user %s" % (fullName, lidnummer, username))
    
