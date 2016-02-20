import Group
import Member
import LdapConnection
import SqlConnection
import ldap

class ApplicationPermission:
    '''
    Super-class for application-specific permissions. Contains the standard way to represent permissions: in LDAP groups. Can be modified by providing your own methods.
    '''
    # These values will be modified in the subclass
    SUB_OU = '' # Example: 'ou=go-groups,'
    APP_PREFIX = '' # Example: 'go'
    #
    
    def __init__(self, directory, database, permissionName):
        '''
        (ApplicationPermission, LdapConnection, SqlConnection, str) -> None
        
        Initializes the Permission instance by its name.
        '''
        self._name = permissionName
        self._application, self._localName = permissionName.split('-', 1)
        if self._application != self.APP_PREFIX:
            raise Exception("Permission name does not have correct format: " + permissionName)
        self._directory = directory
        self._database = database
    
    def grant(self, member):
        '''
        (ApplicationPermission, Member) -> None
        
        Grants the ApplicationPermission to the Member.
        '''
        try:
            Group.Group(self._directory, self._database, self._name, self.SUB_OU).add(member)
        except ldap.ALREADY_EXISTS:
            raise Exception("Member already has permission.")
    
    def revoke(self, member):
        '''
        (ApplicationPermission, Member) -> None
        
        Revokes the ApplicationPermission from member.
        '''
        try:
            Group.Group(self._directory, self._database, self._name, self.SUB_OU).remove(member)
        except ldap.NO_SUCH_ATTRIBUTE:
            raise Exception("Member does not have permission.")
    
    def granted_to(self, member):
        '''
        (ApplicationPermission, Member) -> bool
        
        Returns True iff the ApplicationPermission has been granted to member.
        '''
        return member in Group.Group(self._directory, self._database, self._name, self.SUB_OU)
        
    def number_of_users(self):
        '''
        (ApplicationPermission) -> int
        
        Returns the number of users to whom the permission has been granted.
        '''
        return len(Group.Group(self._directory, self._database, self._name, self.SUB_OU).members())
