#!/usr/bin/python

import sys
sys.path.append("MemberDB")
import MemberDatabase
import Role
import Group
import Member
import Permission
import helper

mdb = MemberDatabase.MemberDatabase(helper.ldapcfg, helper.dbcfg, helper.logger)
l,s = mdb.get_connectors()

SMALL_TAB = 3
LARGE_TAB = 40

monitoredRoleNames = ["ALL"]

def fill_with_spaces(inputString, resultingLength, frontSpaces = 0):
    '''
    (str, int) -> str
    
    Will add frontSpaces spaces to the front of inputString, and then fill it up with spaces from the back until it is of resultingLength. The resulting string will be returned. If the length of inputString plus frontSpaces is greater than resultingLength, inputString with the specified number of frontSpaces will be returned.
    '''
    inputString = (" " * frontSpaces) + inputString
    spaces = " " * (resultingLength - len(inputString))
    return inputString + spaces
    
if __name__ == "__main__":
    print "*****************************************************************"
    print "*                                                               *"
    print "*             Identity & Access Management Overview             *"
    print "*                                                               *"
    print "*****************************************************************"
    print ""
    print fill_with_spaces("Number of members:", LARGE_TAB) + str(mdb.number_of_members())
    print fill_with_spaces("Of which out-of-band:", LARGE_TAB, SMALL_TAB) + str(len(mdb.out_of_band_members()))
    print fill_with_spaces("Number of users:", LARGE_TAB) + str(mdb.number_of_users())
    print ""
    print "Out-of-band members:"
    for member in mdb.out_of_band_members():
        fullName = member.get_full_name()
        print fill_with_spaces(fullName, 0, LARGE_TAB)
    
    print ""
    print "Number of users per role"
    roleList = mdb.all_roles()
    for role in roleList:
        rolestring = fill_with_spaces(role.get_name()+":", LARGE_TAB, SMALL_TAB)
        print(rolestring + str(len(role.members())))

    print ""
    print "Monitored roles"
    monitoredRoles = []
    if monitoredRoleNames[0] == "ALL":
        monitoredRoles = roleList
    else:
        for roleName in monitoredRoleNames:
            role = Role.Role(l, s, roleName)
            monitoredRoles.append(role)    
    
    for role in monitoredRoles:
        if not role.exists():
            print "WARNING: Monitored role %s does not exist." % str(role)
        else:
            print fill_with_spaces(role.get_name()+":", 0, SMALL_TAB)
            roleUsers = role.members()
            for user in roleUsers:
                print fill_with_spaces(user.get_full_name(), 0, LARGE_TAB)
                
    print ""
    print "Roles and permissions"
    for role in roleList:
        print fill_with_spaces(role.get_name() + ":", 0, SMALL_TAB)
        for permission in role.permissions():
            print fill_with_spaces(permission.get_name(), 0, LARGE_TAB)
            
    print ""
    print "Number of users with permission"
    permissionList = mdb.all_permissions()
    for permission in permissionList:
        permstring = " "*SMALL_TAB+permission.get_name()+":"
        spaces = " "*(LARGE_TAB - len(permstring))
        print(fill_with_spaces(permission.get_name()+":", LARGE_TAB, SMALL_TAB) + str(permission.number_of_users()))

