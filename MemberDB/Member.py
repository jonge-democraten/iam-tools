import LdapConnection
import SqlConnection

import ldap
import subprocess
from subprocess import Popen
import random
sysrand = random.SystemRandom()
import re
import logging


WORDLIST_FILE = "woordenlijst"

class Member:
    '''
    Class to manipulate a member in the MemberDatabase.
    '''
    
    def __init__(self, directory, database, lidnummer):
        '''
        (Member, LdapConnection, SqlConnection, int) -> None
        
        Initialize the Member instance of database from the lidnummer.
        '''
        self._directory = directory
        self._database = database
        self._lidnummer = lidnummer
    
    def __str__(self):
        '''
        (Member) -> str
        
        Returns a human-readable representation of Member, which is a string containing lidnummer.
        '''
        return str(self._lidnummer)
    
    def __eq__(self, otherMember):
        '''
        (Member, Member) -> bool
        
        Returns True iff the two Members are equivalent (i.e. have the same lidnummer).
        '''
        if isinstance(otherMember, self.__class__):
            return self._lidnummer == otherMember.get_lidnummer()
        else:
            return False
    
    def __ne__(self, otherMember):
        '''
        (Member, Member) -> bool
        
        Returns True iff the two Groups are not equivalent (i.e. have different group names).
        '''
        return not self.__eq__(otherMember)

    @classmethod
    def from_username(cls, directory, database, username):
        '''
        (method, LdapConnection, SqlConnection, str) -> class
        
        Convert username to lidnummer, then call constructor. Raises a UsernameError if the username does not exist.
        '''
        try:
            lidnummer = int(directory.search_members("uid="+username, ['cn'])[0][1]['cn'][0])
        except IndexError:
            raise UsernameError("Username not found.")
        return cls(directory, database, lidnummer)
    
    def group_list(self):
        '''
        (Member) -> list
        
        Looks up the names of the groups to which Member belongs and returns a list of them.
        '''
        #groupDNs = self.attributes(['memberOf'])['memberOf']
        groupResults = self._directory.search('member=%s'%(self.DN()), self._directory.GROUPS_BASEDN+self._directory.SUFFIX, ldap.SCOPE_SUBTREE, ['cn'])
        groupDNs = []
        for groupResult in groupResults:
            groupDNs.append(groupResult[0])    
        grouplist = []
        for groupDN in groupDNs:
            grouplist.append(self._directory.extract_cn(groupDN))
        return grouplist

    def role_list(self):
        '''
        (Member) -> list
        
        Returns a list of names of Roles that the Member has.
        '''
        roleList = []
        for groupName in self.group_list():
            if groupName.startswith(self._directory.ROLE_PREFIX):
                roleList.append(groupName)
        return roleList
    
    def exists(self):
        '''
        (Member) -> bool
        
        Returns True iff the Member exists in the MemberDatabase.
        '''
        try:
            self.attributes()
        except ldap.NO_SUCH_OBJECT:
            return False;
        return True;
    
    def create(self, fullName, mail, department):
        '''
        (Member, str, str, str) -> None
        
        Creates a new Member in the MemberDatabase with attributes as provided. fullName becomes sn, mail becomes mail and department becomes ou.
        '''
        attributes = {}
        attributes['objectClass'] = ['inetOrgPerson']
        attributes['sn'] = [fullName]
        attributes['mail'] = [mail]
        attributes['ou'] = [department]
        self._directory.add(self.DN(), attributes)
        
    def delete(self):
        '''
        (Member) -> None
        
        Deletes the Member from the MemberDatabase.
        '''
        self._directory.delete(self.DN())
    
    def attributes(self, extraAttributes = []):
        '''
        (Member) -> dict
        
        Returns a dict of attributes for the Member. The dict includes the default attributes and the ones specified in extraAttributes. Each key is an attribute name, and the corresponding element is a list of values assigned to this attribute.
        '''
        return self._directory.attributes(self.DN(), extraAttributes)
    
    def is_user(self):
        '''
        (Member) -> bool
        
        Returns True iff the Member is a user (i.e. has a username).
        '''
        return 'uid' in self.attributes()
    
    def username_exists(self, username):
        '''
        (Member, str) -> bool
        
        Returns whether a username is in use or has ever been used before.
        '''
        sql = "SELECT * FROM usernames WHERE username = %s" 
        value = (username)
        rows = self._database.dosql(sql, value, True)
        for row in rows:
            return True
        return False
    
    def register_username(self, username):
        '''
        (Member, str) -> None
        
        Registers a username in the usernames table for this Member. This prevents the assignment of duplicate usernames in the future.
        '''
        sql = "INSERT INTO usernames (lidnummer, username) VALUES (%s, %s)"
        value = (str(self._lidnummer), username)
        self._database.dosql(sql, value, False)
        
    def make_user(self, username, passwordType):
        '''
        (Member, str, int) -> None
        
        Promotes member to user, by assigning a username and password. Returns the generated password. Will raise a UsernameError if the username has been used before. Will raise a UserError if the member is already a user. Will raise a LidnummerError if the lidnummer provided does not refer to a Member.
        
        Password types are as follows:
        
        0 -> 8 characters, uppercase, lowercase, digits, special
        1 -> 9 characters, uppercase, lowercase
        2 -> 11 characters, lowercase
        3 -> 5 random Dutch words, lowercase
        '''
        if not self.exists():
            raise LidnummerError("The lidnummer does not correspond with an actual Member.")
        elif self.is_user():
            raise MemberError("Member already is a user, with username %s." % self.get_username())
        elif self.username_exists(username):
            raise UsernameError("Username has already been assigned before.")
        else:
            logging.debug("Registering username %s.", username)
            self.register_username(username)
            logging.debug("Setting username %s for lidnummer %s.", username, str(self._lidnummer))
            self._directory.modify(self.DN(), [(ldap.MOD_ADD, "uid", username.encode("utf-8"))])
            password = self.generate_password(passwordType)
            logging.debug("Setting generated password for username %s.", username)
            self.set_password(password)
            return password
    
    def remove_user(self, lidnummer, username):
        '''
        (Member, int, str) -> None
        
        Demotes user to member, by deleting his username and resetting his password. Caller should require the username be provided separately as an additional check.
        
        Will raise a UsernameError if there is username is not the username of this user. Will raise a LidnummerError if lidnummer does not refer to a Member. Will raise MemberError if the member referred to by lidnummer is not a user.
        '''
        if not self.exists():
            raise LidnummerError("Lidnummer does not refer to a Member.")
        elif not self.is_user():
            raise MemberError("Member referred to by lidnummer is not a user.")
        elif self.attributes()['uid'][0] != username:
            raise UsernameError("Provided username does not match provided lidnummer. User removal canceled.")
        self._directory.modify(self.DN(), [(ldap.MOD_DELETE, "uid", None)])
    
    def set_password(self, password):
        '''
        (Member, str) -> None
        
        Sets the password of Member to password.
        '''
        self._directory.password(self.DN(), password)    
    
    def generate_password(self, passwordType):
        '''
        (int) -> str
        
        Generates and returns one password of type passwordType.
        
        Password types are as follows:
            
            0 -> 8 characters, uppercase, lowercase, digits, special
            1 -> 9 characters, uppercase, lowercase
            2 -> 11 characters, lowercase
            3 -> 5 random Dutch words, lowercase
        '''
        if passwordType == 0:
            passToSet = Popen(["pwgen", "-ncs", "-y", "8", "1"], stdout=subprocess.PIPE).communicate()[0]
        elif passwordType == 1:
            passToSet = Popen(["pwgen", "-0cs", "9", "1"], stdout=subprocess.PIPE).communicate()[0]
        elif passwordType == 2:
            passToSet = Popen(["pwgen", "-0As", "11", "1"], stdout=subprocess.PIPE).communicate()[0]
        elif passwordType == 3:
            file = open(WORDLIST_FILE, 'r')
            words = file.read().splitlines()
            passToSet = ''.join(sysrand.sample(words, 5))
        else:
            raise Exception("Password type should be 0, 1, 2 or 3.")
        return passToSet
    
    def get_lidnummer(self):
        '''
        (Member) -> int
        
        Returns the lidnummer of the Member instance.
        '''
        return self._lidnummer
    
    def DN(self):
        '''
        (Member) -> str
        
        Constructs and returns the DN at which Member should be located in directory.
        '''
        return "cn=%i,%s%s" % (self._lidnummer, self._directory.MEMBERS_BASEDN, self._directory.SUFFIX)
    
    def get_full_name(self):
        '''
        (Member) -> int
        
        Returns the full name of the Member.
        '''
        return self.attributes()['sn'][0]
    
    def get_mail(self):
        '''
        (Member) -> int
        
        Returns the e-mail address of the Member.
        '''
        return self.attributes()['mail'][0]
    
    def get_afdeling(self):
        '''
        (Member) -> int
        
        Returns the afdeling of the Member.
        '''
        return self.attributes()['ou'][0]
    
    def get_username(self):
        '''
        (Member) -> str
        
        Returns the username of the Member. Raises UsernameError if the username does not exist.
        '''
        try:
            return self.attributes()['uid'][0]
        except IndexError:
            raise UsernameError("Member does not have a username.")

### END OF CLASS


class MemberError(Exception):
    '''
    Base class for Member-related errors.
    '''
    def __init__(self, value):
        '''
        (UserError, str) -> None
        
        Initiate a UserError.
        '''
        self._value = value
    
    def __str__(self):
        '''
        (UserError) -> str
        
        Return a human-readable version of UserError.
        '''
        return str(self._value)

class UsernameError(MemberError):
    '''
    A UsernameError indicates that something went wrong with the validity or existence of a username. For example, a new Member instance was created based on a username, but the username does not actually exist.
    '''
    
class LidnummerError(MemberError):
    '''
    A LidnummerError indicates that something went wrong with the validity or existence of a lidnummer. For example, a Member is asked to be promoted to user, but the lidnummer provided does not match the member.
    '''

def is_valid_lidnummer(lidnummer):
    '''
    (Member, str) -> bool
    
    Returns True iff lidnummer is a valid lidnummer (in str form) for Member.
    '''
    try:
        int(lidnummer)
        return True
    except ValueError:
        return False

def is_valid_lidnummer_filter(lidnummerFilter):
    '''
    (str) -> bool
    
    Returns True iff lidnummerFilter is a valid lidnummer search query for Member.
    '''
    return re.match("^cn=\*?[0-9]+\*?", lidnummerFilter)
    
def is_valid_full_name(fullName):
    '''
    (str) -> bool
    
    Returns True iff fullName is a valid full name for Member.
    '''
    return re.match("^[a-zA-Z \-]+$", fullName)

def is_valid_full_name_filter(fullNameFilter):
    '''
    (str) -> bool
    
    Returns True iff fullNameFilter is a valid full name search query for Member.
    '''
    return re.match("^sn=[a-zA-Z \-\*]+$", fullNameFilter)

def is_valid_mail(mail):
    '''
    (str) -> bool
    
    Returns True iff mail is a valid e-mail address for Member.
    '''
    return re.match("^[a-zA-Z0-9\._+\-]+@[a-zA-Z0-9\.\-]+$", mail)
    
def is_valid_mail_filter(mailFilter):
    '''
    (str) -> bool
    
    Returns True iff mailFilter is a valid e-mail address search query for Member.
    '''
    return re.match("^mail=\*?[a-zA-Z0-9\._+\-@]+\*?$", mailFilter)

def is_valid_username(username):
    '''
    (str) -> bool
    
    Returns True iff username is a valid username for Member.
    '''
    return re.match("^[a-z]+$", username)
    
def is_valid_username_filter(usernameFilter):
    '''
    (str) -> bool
    
    Returns True iff usernameFilter is a valid username search query for Member.
    '''
    return re.match("^uid=\*?[a-z]+\*?$", usernameFilter)

def is_valid_afdeling(afdeling):
    '''
    (str) -> bool
    
    Returns True iff afdeling is a valid afdeling for Member. Does not do whitelisting on valid names.
    '''
    return re.match("^[A-Za-z \-]+$")

def is_valid_afdeling_filter(afdelingFilter):
    '''
    (str) -> bool
    
    Returns True iff afdelingFilter is a valid afdeling search query for Member.
    '''
    return re.match("^ou=\*?[A-Za-z \-]+\*?$")

