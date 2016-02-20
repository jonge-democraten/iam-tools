import Group
import Permission
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
    
    def __contains__(self, permission):
        '''
        (Role, Permission) -> bool
        
        Returns True iff the Role contains the Permission specified.
        '''
        sql = "SELECT 1 from roles_perms WHERE role = %s AND perm = %s"
        value = (self._name, permission.get_name())
        rows = self._database.dosql(sql, value, True)
        for row in rows:
            return True
        return False
    
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
            for permission in self.permissions():
                self.remove(permission)
            self._roleGroup.delete()
    
    def add(self, permission):
        '''
        (Role, Permission) -> None
        
        Adds permission to this Role.
        '''
        if permission in self:
            raise Exception("Could not add permission: role already contains permission.")
        else:
            sql = "INSERT INTO roles_perms (role, perm) VALUES (%s, %s);"
            value = (self._name, permission.get_name())
            self._database.dosql(sql, value, False)
            for member in self._roleGroup.members():
                try:
                    permission.grant(member)
                except Exception, e:
                    if not e == "Member already has permission.":
                        raise Exception(e)
                    
    def remove(self, permission):
        '''
        (Role, Permission) -> None
        
        Removes permission from this Role.
        '''
        if not permission in self:
            raise Exception("Could not remove permission: role does not contain permission.")
        else:
            for member in self._roleGroup.members():
                memberRoles = member.roles()
                found = False
                for memberRole in memberRoles:
                    if not memberRole == self and permission in memberRole:
                        found = True
                        break
                if not found:
                    try:
                        permission.revoke(member)
                    except Exception, e:
                        if not e == "Member does not have permission.":
                            raise Exception(e)
            sql = "DELETE FROM roles_perms WHERE role = %s AND perm = %s"
            value = (self._name, permission.get_name())
            self._database.dosql(sql, value, False)
            
    def grant(self, member):
        '''
        (Role, Member) -> None
        
        Grant this Role to this Member. All associated permissions will be granted as well.
        '''
        if not member.is_user():
            raise Exception("Can not grant role to members who are not users.")
        else:
            self._roleGroup.add(member)
            for permission in self.permissions():
                if not permission.granted_to(member):
                    try:
                        permission.grant(member)
                    except Exception, e:
                        if not e == "Member already has permission.":
                            raise Exception(e)
    
    def revoke(self, member):
        '''
        (Role, Member) -> None
        
        Revoke this Role from this Member. All associated permissions will also be revoked, unless the user also posesses them through an other role.
        '''
        if not member.is_user():
            raise Exception("Can not revoke role from members who are not users.")
        else:
            permissionsToRevoke = self.permissions()
            roleNameList = member.role_list()
            otherRoleList = []
            for roleName in roleNameList:
                otherRoleList.append(Role(self._directory, self._database, roleName))
            for permission in permissionsToRevoke:
                found = False
                for otherRole in otherRoleList:
                    if permission in otherRole:
                        found = True
                        break
                if not found:
                    permission.revoke(member)
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
    
    def permissions(self):
        '''
        (Role) -> list
        
        Returns a list of all Permissions that are associated with the role.
        '''
        sql = "SELECT perm FROM roles_perms WHERE role = %s"
        value = (self._name)
        rows = self._database.dosql(sql, value, True)
        permissions = []
        for row in rows:
            permissions.append(Permission.Permission(self._directory, self._database, row[0]))
        return permissions
    
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
