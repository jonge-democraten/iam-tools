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

    def grant(self, member):
        '''
        (ApplicationPermission, Member) -> None

        Grants the ApplicationPermission to the Member.
        '''
        if self._name != self.APP_PREFIX+"-access":
            try:
                Group.Group(self._directory, self._database, self._name, self.SUB_OU).add(member)
            except ldap.ALREADY_EXISTS:
                raise Exception("Member already has permission.")
        else:
            self._directory.modify(member.DN(), [(ldap.MOD_ADD, "o", (self.APP_PREFIX+"-access").encode('utf-8'))])

    def revoke(self, member):
        '''
        (ApplicationPermission, Member) -> None

        Revokes the ApplicationPermission from member.
        '''
        if self._name != self.APP_PREFIX+"-access":
            try:
                Group.Group(self._directory, self._database, self._name, self.SUB_OU).remove(member)
            except ldap.NO_SUCH_ATTRIBUTE:
                raise Exception("Member does not have permission.")
        else:
            self._directory.modify(member.DN(), [(ldap.MOD_DELETE, "o", (self.APP_PREFIX+"-access").encode('utf-8'))])

    def granted_to(self, member):
        '''
        (ApplicationPermission, Member) -> bool

        Returns True iff the ApplicationPermission has been granted to member.
        '''
        if self._name != self.APP_PREFIX+"-access":
            return member in Group.Group(self._directory, self._database, self._name, self.SUB_OU)
        else:
            return self.APP_PREFIX+"-access" in member.attributes(['o'])['o']

    def number_of_users(self):
        '''
        (ApplicationPermission) -> int

        Returns the number of users to whom the permission has been granted.
        '''
        if self._name != self.APP_PREFIX+"-access":
            return len(Group.Group(self._directory, self._database, self._name, self.SUB_OU).members())
        else:
            return len(self._directory.search("o="+self.APP_PREFIX+"-access", self._directory.MEMBERS_BASEDN+self._directory.SUFFIX, ldap.SCOPE_ONELEVEL, ['cn']))
