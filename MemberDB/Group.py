import Member
import LdapConnection
import SqlConnection
import ldap

class Group():
    '''
    Class to manipulate a group in the MemberDatabase.
    '''

    def __init__(self, directory, database, groupName, groupSubOU = ''):
        '''
        (Group, LdapConnection, SqlConnection, str, str) -> None
        
        Initialize the Group instance from the groupName. groupSubOU indicates whether the group is in the group root (default) or in some subOU of the groups-OU (e.g. for some permission groups).
        
        Example:
        If groups are in 'ou=groups,dc=example,dc=com' by default, to place your group in 'ou=new,ou=groups,dc=example,dc=com', groupsSubOU should be 'ou=new,'. Do not forget the trailing comma.
        '''
        self._directory = directory
        self._database = database
        self._name = groupName
        self._subOU = groupSubOU
    
    @classmethod
    def from_dn(cls, directory, database, groupDN):
        '''
        (method, LdapConnection, SqlConnection, str) -> class
        
        Convert groupDN to groupName and subOU, then call constructor.
        '''
        return cls(directory, database, directory.extract_cn(groupDN), directory.extract_group_sub_ou(groupDN))
        
    def __str__(self):
        '''
        (Group) -> str
        
        Returns a human-readable representation of Group, which is the group name.
        '''
        return self._name
    
    def __eq__(self, otherGroup):
        '''
        (Group, Group) -> bool
        
        Returns True iff the two Groups are equivalent (i.e. have the same group name).
        '''
        if isinstance(otherGroup, self.__class__):
            return self._name == otherGroup.get_name() and self._subOU == otherGroup.getSubOU()
        else:
            return False
    
    def __ne__(self, otherGroup):
        '''
        (Group, Group) -> bool
        
        Returns True iff the two Groups are not equivalent (i.e. have different group names).
        '''
        return not self.__eq__(otherGroup)

    def __contains__(self, member):
        '''
        (Group, Member) -> bool
        
        Returns True iff the Member is a member of the Group.
        '''
        return member in self.members()
    
    def exists(self):
        '''
        (Group) -> bool
        
        Returns True iff the group exists in the MemberDatabase.
        '''
        try:
            self.attributes()
        except ldap.NO_SUCH_OBJECT:
            return False;
        return True;
    
    def get_name(self):
        '''
        (Group) -> str
        
        Returns the name of the Group.
        '''
        return self._name
    
    def get_subOU(self):
        '''
        (Group) -> str
        
        Returns the value of the internal variable subOU.
        '''
        return self._subOU    
    
    def members(self):
        '''
        (Group) -> list
        
        Returns a list of Members who are a member of the Group.
        '''
        try:
            memberDNs = self.attributes(['member'])['member']
        except KeyError:
            return []
        members = []
        for memberDN in memberDNs:
            if memberDN != self._directory.STRUCTURAL_USER:
                members.append(Member.Member(self._directory, self._database, int(self._directory.extract_cn(memberDN))))
        return members
    
    def attributes(self, extraAttributes = []):
        '''
        (Group) -> dict
        
        Returns a dict of attributes for the Group. The dict includes the default attributes and the ones specified in extraAttributes. Each key is an attribute name, and the corresponding element is a list of values assigned to this attribute.
        '''
        return self._directory.attributes(self.DN(), extraAttributes)
    
    def create(self):
        '''
        (Group) -> None
        
        Creates the Group in the MemberDatabase.
        '''
        attributes = {}
        attributes['objectClass'] = ['groupOfNames']
        attributes['member'] = [self._directory.STRUCTURAL_USER]
        self._directory.add(self.DN(), attributes)        
            
    def delete(self):
        '''
        (Group) -> None
        
        Deletes the Group from the MemberDatabase.
        '''
        self._directory.delete(self.DN())
    
    def add(self, member):
        '''
        (Group, Member) -> None
        
        Add member to group.
        '''
        self._directory.modify(self.DN(), [(ldap.MOD_ADD, "member", member.DN())])
        
    def remove(self, member):
        '''
        (Group, Member) -> None
        
        Remove member from group.
        '''
        self._directory.modify(self.DN(), [(ldap.MOD_DELETE, "member", member.DN())])
    
    def DN(self):
        '''
        (Group) -> str
    
        Constructs and returns the DN at which Member should be located in directory.
        '''
        return "cn=%s,%s%s%s" % (self._name, self._subOU, self._directory.GROUPS_BASEDN, self._directory.SUFFIX)
