import Group
import Member
import LdapConnection
import SqlConnection
import ApplicationPermission
import ldap

class GroupOfficePermission(ApplicationPermission.ApplicationPermission):
    '''
    Class to manipulate a Group-Office permission in the MemberDatabase.
    '''
    SUB_OU = 'ou=go-groups,'
    APP_PREFIX = 'go'