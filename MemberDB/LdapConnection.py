import ldap
import ldap.modlist as modlist
import sys
import logging
import re

class LdapConnection:
    """
    Class to set up and employ an LDAP connection.
    """
    SUFFIX = ",dc=jd,dc=nl"
    MEMBERS_BASEDN = "ou=users"
    GROUPS_BASEDN = "ou=groups"
    SYSUSERS_BASEDN = "ou=sysUsers"
    EMPTY_MEMBER_FILTER = "objectClass=inetOrgPerson"
    STRUCTURAL_USER = "cn=structuraluser," + SYSUSERS_BASEDN + SUFFIX
    ROLE_PREFIX = "role-"
   
    def __init__(self, hostname, DN, password, loggingFacility):
        '''
        (LdapConnection, str, str, str, Logger) -> None
        
        Takes all the credentials to start an LDAP connection and creates the connection object.
        
        Will handle any LDAP errors itself and stop exection upon failure.
        '''
        self._hostname = hostname
        self._dn = DN
        self._connection = ldap.initialize(hostname)
        self._logger = loggingFacility
        try:
            self._connection.simple_bind_s(DN, password)
        except ldap.LDAPError, e:
            self._logger.error(str(e))
            sys.exit()

    def __str__(self):
        '''
        (LdapConnection) -> str
        
        Returns a human-readable representation of the connection that includes the DN used to connect and the hostname where the server runs.
        '''
        return self._dn + " @ " + self._hostname

    def search(self, searchFilter, baseDN, searchScope, targetAttributes, suppressNoResults = True):
        '''
        (LdapConnection, str, str, ldap.SCOPE, list, bool) -> list
        
        Searches for the records matching searchFilter under the baseDN, according to the searchScope provided. For each record, retrieves the  attributes specified in targetAttributes. Will return a list of records, with each record being a tuple (DN, attributes). attributes is a dict of lists, with each key being one attribute. The list associated with each key contains the values assigned to this attribute in this record.
        
        By default, will not throw an LDAP exception (ldap.NO_RESULTS_RETURNED) if the search returns no results, but rather return an empty list. This behavior can be set in the suppressNoResults argument. 
        '''
        ldapResultId = self._connection.search(baseDN, searchScope, searchFilter, targetAttributes)
        while 1:
            resultType, resultData = self._connection.result(ldapResultId, 1)
            if (resultData == []) and not suppressNoResults:
                raise ldap.NO_RESULTS_RETURNED 
            elif resultType == ldap.RES_SEARCH_RESULT:
                return resultData
            else:
                return []

    def attributes(self, DN, extraAttributes = None):
        '''
        (LdapConnection, str, list) -> list
        
        Retrieves the attributes of the record specified in DN. For this attributes, the default attributes are retrieved, together with the extra attributes defined in the list extraAttributes. Will return a dict of lists, with each key being one attribute. The list associated with each key contains the values assigned to this attribute in the record DN.
        
        Will throw an LDAP exception (ldap.NO_RESULTS_RETURNED) if the search returns no results.
        '''
        targetAttributes = ['*']
        targetAttributes.extend(extraAttributes)
        results = self.search("(cn=*)", DN, ldap.SCOPE_BASE, targetAttributes)
        return results[0][1]

    def add(self, toAddDN, attributes):
        '''
        (LdapConnection, str, dict) -> None
        
        Adds a record to the LDAP directory at toAddDN. attributes is a dict of lists, with each key being one attribute. The list associated with each key contains the values to be assigned to this attribute in the record toAddDN.
        
        Will throw an LDAP exception if adding does not succeed.
        '''
        ldif = modlist.addModlist(attributes)
        self._connection.add_s(toAddDN, ldif)
        self._logger.debug("Added " + toAddDN)

    def delete(self, toDeleteDN):
        '''
        (LdapConnection, str) -> None
        
        Deletes the record in the LDAP directory at toDeleteDN.
        
        Will throw an LDAP exception if deleting does not succeed.
        '''
        self._connection.delete_s(toDeleteDN)
        self._logger.debug("Deleted " + toDeleteDN)

    def modify(self, toModifyDN, modifications):
        '''
        (LdapConnection, str, list) -> None
        
        Modifies the record in the LDAP directory at toModifyDN. modifications specifies what to change: it is a list of modifications to make. Each element is a 3-tuple (operation, attribute, value).
        
        Example:
        
        connection.modify(recordDN, [(ldap.MOD_REPLACE, "uid", "myuser".encode("utf-8"))]
        
        Will throw an LDAP exception if modifying does not succeed.
        '''
        self._connection.modify_s(toModifyDN, modifications)
        modifiedAttributes = []
        for mod in modifications:
            modifiedAttributes.append(mod[1])
        self._logger.debug("Modified " + toModifyDN + " " + str(modifiedAttributes))
    
    def password(self, memberDN, passwordToSet):
        '''
        (LdapConnection, str, str) -> None
        
        Modifies the member record in the LDAP directory at memberDN. The modification is that the password is set to passwordToSet.
        '''
        self._connection.passwd_s(memberDN, None, passwordToSet)
        
    def search_members(self, searchFilter, targetAttributes):
        '''
        (LdapConnection, str, list) -> list
        
        Searches for the member records matching searchFilter. For each record, retrieves the attributes specified in targetAttributes. Will return a list of records, with each record being a tuple (DN, attributes). attributes is a dict of lists, with each key being one attribute. The list associated with each key contains the values assigned to this attribute in this record.

        Will throw an LDAP exception (ldap.NO_RESULTS_RETURNED) if the search returns no results.
        '''
        return self.search(searchFilter, self.MEMBERS_BASEDN + self.SUFFIX, ldap.SCOPE_ONELEVEL, targetAttributes)

    def extract_cn(self, dn):
        '''
        (LdapConnection, str) -> str
        
        Extracts the cn attribute from a given DN. Returns the cn as a str.
        '''
        p = re.compile('^cn=([^,]+),.*'+self.SUFFIX+'$')
        m = p.match(dn)
        return m.group(1)
        
    def extract_group_sub_ou(self, dn):
        '''
        (LdapConnection, str) -> str
        
        Extracts the subOU attribute from a given DN. Returns the subOU as a str.
        '''
        p = re.compile('^cn=[^,]+,(.*)'+self.GROUPS_BASEDN+self.SUFFIX+'$')
        m = p.match(dn)
        return m.group(1)
        
