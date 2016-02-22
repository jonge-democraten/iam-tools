import Group
import LdapConnection
import SqlConnection
import re

class Role:
    '''
    Class to manipulate a role in the MemberDatabase.
    '''
    
    def __init__(self, directory, database, roleName):
        '''
        (Role, LdapConnection, SqlConnection, str) -> None
        
        Initialize the Role instance from the role name.
        '''
        self._directory = directory
        self._database = database
        self._name = roleName
        self._roleGroup = Group.Group(directory, database, roleName)
        
    def __str__(self):
        '''
        (Role) -> str
        
        Return a human-readable representation of the Role, namely its name.
        '''
        return self._name
    
    def __eq__(self, otherRole):
        '''
        (Role, Role) -> bool
        
        Returns True iff the two Roles are equivalent (i.e. have the same roleName).
        '''
        if isinstance(otherRole, self.__class__):
            return self._name == otherRole.get_name()
        else:
            return False
    
    def __ne__(self, otherRole):
        '''
        (Role, Role) -> bool
        
        Returns True iff the two Roles are not equivalent.
        '''
        return not self.__eq__(otherRole)
    
    def create(self):
        '''
        (Role) -> None
        
        Creates the Role in the MemberDatabase.
        '''
        if is_valid_role_name(self._name):
            self._roleGroup.create()
        else:
            raise Exception("Could not create role: invalid name.")
        
    def delete(self):
        '''
        (Role) -> None
        
        Deletes the Role from the MemberDatabase.
        '''
        if not self.exists():
            raise Exception("Could not delete role: role does not exist.")
        else:
            self._roleGroup.delete()
    
    def grant(self, member):
        '''
        (Role, Member) -> None
        
        Grant this Role to this Member.
        '''
        if not member.is_user():
            raise Exception("Can not grant role to members who are not users.")
        else:
            self._roleGroup.add(member)
    
    def revoke(self, member):
        '''
        (Role, Member) -> None
        
        Revoke this Role from this Member.
        '''
        if not member.is_user():
            raise Exception("Can not revoke role from members who are not users.")
        else:
            self._roleGroup.remove(member)
    
    def get_name(self):
        '''
        (Role) -> str
        
        Returns the name of the role.
        '''
        return self._name
    
    def members(self):
        '''
        (Role) -> list
        
        Returns all users who have this role as a list of Members.
        '''
        return self._roleGroup.members()
    
    def exists(self):
        '''
        (Role) -> bool
        
        Returns True iff the Role exists (i.e. the Group exists in the MemberDatabase).
        '''
        return self._roleGroup.exists()
    
### END OF CLASS

def is_valid_role_name(roleName):
    '''
    (str) -> bool
    
    Returns True iff roleName would be a valid role name in the directory.
    '''
    return re.match("^role-[a-z\-]+$", roleName)
