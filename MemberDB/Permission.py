import Member
import LdapConnection
import SqlConnection

import GroupOfficePermission
import WordpressPermission
# ADD ADDITIONAL APPLICATIONS HERE

class Permission():
    def __init__(self, directory, database, permissionName):
        '''
        (Permission, LdapConnection, SqlConnection) -> None
        
        Initializes the Permission instance by its name.
        '''
        self._name = permissionName
        self._application, self._localName = permissionName.split('-', 1)
        if len(self._application)!= 2:
            raise Exception("Permission name does not have correct format: " + permissionName)
        self._directory = directory
        self._database = database 
    
    def __str__(self):
        '''
        (Permission) -> str
        
        Returns a human-readable representation of the Permission, namely its name.
        '''
        return self.get_name()
    
    def convert_to_appclass(self):
        '''
        (Permission) -> Application-specific Permission
        
        Convert the Permission to the specific Permission that is appropriate for the application to which the permission belongs. Returns the application-specific Permission.
        
        '''
        if self._application == "go": # Wolk-permissies
            return GroupOfficePermission.GroupOfficePermission(self._directory, self._database, self._name)
        if self._application == "wp": # Wordpress-permissies
            return WordpressPermission.WordpressPermission(self._directory, self._database, self._name)
        # ADD ADDITIONAL APPLICATIONS HERE
        raise Exception("Could not find application-specific methods: Class missing.")
    
    def get_name(self):
        '''
        (Permission) -> str
        
        Returns the name of the permission.
        '''
        return self._name
    
    def get_application(self):
        '''
        (Permission) -> str
        
        Returns the application to which the Permission belongs. The application is always a string of length 2.
        '''
        return self._application
    
    def get_local_name(self):
        '''
        (Permission) -> str
        
        Returns the local part of the Permission name.
        '''
        return self._localName
    
    def exists(self):
        '''
        (Permission) -> bool
        
        Returns True iff the permission is assigned to at least one role (i.e. exists).
        '''
        sql = "SELECT 1 FROM roles_perms WHERE perm = %s"
        value = (self._name)
        rows = self._database.dosql(sql, value, True)
        for row in rows:
            return True
        return False
   
    def grant(self, member):
        '''
        (Permission, Member) -> None
        
        Grant the Permission to user.
        '''
        if not member.is_user():
            raise Exception("Could not grant permission to member: member is not a user.")
        else:
            permission = self.convert_to_appclass()
            if not permission.granted_to(member):
                permission.grant(member)
            else:
                raise Exception("Member already has permission.")
            
    def revoke(self, member):
        '''
        (Permission, Member) -> None
        
        Revoke the Permission from user.
        '''
        if not member.is_user():
            raise Exception("Could not revoke the permission from member: member is not a user.")
        else:
            permission = self.convert_to_appclass()
            permission.revoke(member)
            
    def granted_to(self, member):
        '''
        (Permission, Member) -> bool
        
        Returns True iff the Permission has been granted to member.
        '''
        permission = self.convert_to_appclass()
        return permission.granted_to(member)
            
    def number_of_users(self):
        '''
        (Permission) -> int
        
        Returns the number of users to whom the permission has been granted.
        '''
        permission = self.convert_to_appclass()
        return permission.number_of_users()
