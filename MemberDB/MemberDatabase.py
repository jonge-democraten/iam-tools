import Role
import Permission
import Group
import Member
import LdapConnection
import SqlConnection

import logging
import ldap

class MemberDatabase:
    '''
    Class to access and manage a member database in an LDAP directory and MySQL database.
    '''
    
    def __init__(self, ldapConfig, sqlConfig, loggingFacility):
        '''
        (MemberDatabase, dict, dict, Logger) -> None
        
        Initializes the MemberDatabase, by connecting to the associated LDAP directory and SQL database.
        
        ldapConfig contains three keys: name (hostname of server), dn (user as whom to bind), password.
        sqlConfig contains four keys: host (hostname of server), user (username as whom to connect), password and name (database to which to connect).
        '''
        self._directory = LdapConnection.LdapConnection(ldapConfig['name'], ldapConfig['dn'], ldapConfig['password'], loggingFacility)
        self._database = SqlConnection.SqlConnection(sqlConfig['host'], sqlConfig['name'], sqlConfig['user'], sqlConfig['password'], loggingFacility)
        self._logger = loggingFacility
        
    def get_connectors(self):
        '''
        (MemberDatabase) -> LdapConnection, SqlConnection
        
        Returns the connectors that are generated during the initiation of the MemberDatabase.
        '''
        return self._directory, self._database
        
    def search_users(self, searchFilter = "objectClass=inetOrgPerson"):
        '''
        (MemberDatabase, str, list) -> list
        
        Searches for the user records matching searchFilter and return them as a list of Members.
        
        Will throw an LDAP exception (ldap.NO_RESULTS_RETURNED) if the search returns no results.
        '''
        searchFilter = "(&("+searchFilter+")(uid=*))"
        return self.search_members(searchFilter)
        
    def search_members(self, searchFilter = "objectClass=inetOrgPerson"):
        '''
        (LdapConnection, str, list) -> list
        
        Searches for the member records matching searchFilter and return them as a list of Members.

        Will throw an LDAP exception (ldap.NO_RESULTS_RETURNED) if the search returns no results.
        '''
        memberEntries = self._directory.search_members(searchFilter, ['cn'])
        members = []
        for entry in memberEntries:
            members.append(Member.Member(self._directory, self._database, int(entry[1]['cn'][0])))
        return members        
    
    def number_of_members(self):
        '''
        (MemberDatabase) -> int
        
        Returns the number of members in the MemberDatabase.
        '''
        return len(self.search_members(self._directory.EMPTY_MEMBER_FILTER))
    
    def number_of_users(self):
        '''
        (MemberDatabase) -> int
        
        Returns the number of users in the MemberDatabase.
        '''
        return len(self.search_users(self._directory.EMPTY_MEMBER_FILTER))
    
    def out_of_band_members(self):
        '''
        (MemberDatabase) -> list
        
        Returns a list of Members with out-of-band status.
        '''
        return Group.Group(self._directory, self._database, "type-outofband").members()
        
    def revoke_all_roles(self, member):
        '''
        (MemberDatabase, Member) -> None
        
        Revokes all the roles that have been granted to member.
        '''
        memberRoleNameList = member.role_list()
        for memberRoleName in memberRoleNameList:
            Role.Role(self._directory, self._database, memberRoleName).revoke(member)
    
    def all_roles(self):
        '''
        (MemberDatabase) -> list
        
        Returns a list of Roles that have been defined in the MemberDatabase.
        '''
        roles = []
        searchFilter = "cn=%s*" % self._directory.ROLE_PREFIX
        results = self._directory.search(searchFilter, self._directory.GROUPS_BASEDN+self._directory.SUFFIX, ldap.SCOPE_ONELEVEL, ['cn'])
        for result in results:
            DN, attributes = result
            cn = attributes['cn'][0]
            roles.append(Role.Role(self._directory, self._database, cn))
        return roles
    
    def all_groups(self):
        '''
        (MemberDatabase) -> list
        
        Returns a list of all Groups that have been defined in the MemberDatabase.
        '''
        searchFilter = "objectClass=groupOfNames"
        baseDN = self._directory.GROUPS_BASEDN + self._directory.SUFFIX
        results = self._directory.search(searchFilter, baseDN, ldap.SCOPE_SUBTREE, ['cn'])
        groupList = []
        for groupEntry in results:
            groupList.append(Group.Group.from_dn(self._directory, self._database, groupEntry[0]))
        return groupList        
    
    def all_permissions(self):
        '''
        (MemberDatabase) -> list
        
        Returns a list of Permissions that have been defined in the MemberDatabase.
        '''
        permissions = []
        sql = "SELECT DISTINCT perm FROM roles_perms"
        rows = self._database.dosql(sql, "", True)
        for row in rows:
            permissions.append(Permission.Permission(self._directory, self._database, row[0]))
        return permissions
    
    def fix(self):
        '''
        (MemberDatabase) -> None
        
        Fix the assigned permissions: revoke all permissions, then grant permissions based on the roles of users.
        '''
        roles = self.all_roles()
        permissions = self.all_permissions()
        users = self.search_users()
        for user in users:
            for permission in permissions:
                if permission.granted_to(user):
                    permission.revoke(user)
        
        for role in roles:
            for member in role.members():
                for permission in role.permissions():
                    if not permission.granted_to(member):
                        permission.grant(member)
