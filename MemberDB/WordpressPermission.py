import Group
import Member
import LdapConnection
import SqlConnection
import ApplicationPermission
import ldap

class WordpressPermission(ApplicationPermission.ApplicationPermission):
    '''
    Class to manipulate a Wordpress permission in the MemberDatabase.
    '''
    SUB_OU = 'ou=wp-groups,'
    APP_PREFIX = 'wp'