#!/usr/bin/python
import sys
import subprocess

# Copied this from the internet, as Python 2.6 does not yet support check_output in module subprocess
def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        #raise error
    return output

# The initial filler function. Returns the main menu and the tool header.
def begin_it():
    output = """
*************************************
*            JD IAM-tool            *
*************************************
"""

    menu = """
(1) Give overview
(2) Search for members
(3) Search for users
(4) List all users with their roles
(5) Make member a user
(6) Make member a user (search by name)
(7) Remove user (demote to member)
(8) Reset password for user
(9) List all roles
(0) Assign role to user
(-) Remove role from user
(=) Quit
"""
    state = "main"
    return output, menu, state

# The menu runner function. Displays provided information, asks for user input.
def run_menu(output, menu):
    print output
    print menu

    print "----------------------------------------------------------------"
    user_input = raw_input("> ")
    return user_input

# The processing function for state searchmembers
def process_input_searchmembers(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    if not ' ' in user_input:
        return output, menu, state
    input_parts = user_input.split(' ', 1)
    if input_parts[0] == "1":
        search_option = "-i"
    elif input_parts[0] == "2":
        search_option = "-n"
    elif input_parts[0] == "3":
        search_option = "-e"
    elif input_parts[0] == "4":
        search_option = "-u"
    else:
        return output, menu, state
    output = check_output(["python", "search_users.py", "-a", search_option, input_parts[1]])
    return output, menu, state

# The processing function for state searchusers
def process_input_searchusers(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    if not ' ' in user_input:
        return output, menu, state
    input_parts = user_input.split(' ', 1)
    if input_parts[0] == "1":
        search_option = "-i"
    elif input_parts[0] == "2":
        search_option = "-n"
    elif input_parts[0] == "3":
        search_option = "-e"
    elif input_parts[0] == "4":
        search_option = "-u"
    else:
        return output, menu, state
    output = check_output(["python", "search_users.py", search_option, input_parts[1]])
    return output, menu, state

# The processing function for state makeuser
def process_input_makeuser(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    input_parts = user_input.split(' ', 2)
    if len(input_parts) < 3:
        return output, menu, state
    output = check_output(["python", "make_user.py", input_parts[0], input_parts[1], input_parts[2]])
    return output, menu, state

# The processing function for state makeuserbyname
def process_input_makeuserbyname(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    input_parts = user_input.rsplit(' ', 2)
    if len(input_parts) < 3:
        return output, menu, state
    output = check_output(["python", "make_user_by_name.py", input_parts[0], input_parts[1], input_parts[2]])
    return output, menu, state

# The processing function for state resetpassword
def process_input_resetpassword(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    input_parts = user_input.split(' ', 1)
    if len(input_parts) < 2:
        return output, menu, state
    output = check_output(["python", "reset_password.py", input_parts[0], input_parts[1]])
    return output, menu, state

# The processing function for state removeuser
def process_input_removeuser(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    if not ' ' in user_input:
        return output, menu, state
    input_parts = user_input.split(' ', 1)
    output = check_output(["python", "remove_user.py", input_parts[0], input_parts[1]])
    return output, menu, state

# The processing function for state giverole
def process_input_giverole(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    if not ' ' in user_input:
        return output, menu, state
    input_parts = user_input.split(' ', 1)
    output = check_output(["python", "give_role.py", input_parts[0], input_parts[1]])
    return output, menu, state

# The processing function for state removerole
def process_input_removerole(user_input):
    output = "Input not recognized, returning to main menu."
    dummy, menu, state = begin_it()
    if not ' ' in user_input:
        return output, menu, state
    input_parts = user_input.split(' ', 1)
    output = check_output(["python", "remove_role.py", input_parts[0], input_parts[1]])
    return output, menu, state

# The processing function for state main
# (the main menu)
def process_input_main(user_input):
    output = ""
    menu = ""
    state = ""
    if user_input == "1":
        dummy, menu, state = begin_it()
        output = check_output(["python", "generate_overview.py"])
    elif user_input == "2":
        output = "== Search for members =="
        menu = """(1) Search for lidnummer
(2) Search for part of name
(3) Search for part of e-mail address
(4) Search for part of username

Enter the number of the option followed by your search entry, separated by a space (e.g. '2 Rogaar').
"""
        state = "searchmembers"
    elif user_input == "3":
        output = "== Search for users =="
        menu = """(1) Search for lidnummer
(2) Search for part of name
(3) Search for part of e-mail address
(4) Search for part of username

Enter the number of the option followed by your search entry, separated by a space (e.g. '2 Rogaar').
"""
        state = "searchusers"
    elif user_input == "4":
        dummy, menu, state = begin_it()
        output = check_output(["python", "list_users.py"])
    elif user_input == "5":
        output = "== Make member a user =="
        menu = """Enter lidnummer, desired username and desired password type, separated by spaces (e.g. '12345 myuser 3').

Password type is one of the following:

0   Password contains lowercase, uppercase, digits and special characters (shortest)
1   Password contains lowercase and uppercase
2   Password contains only lowercase
3   Password consists of five concatenated Dutch words

Password entropy is always at least 50 bits. Password length is adjusted accordingly.
"""
        state = "makeuser"
    elif user_input == "6":
        output = "== Make member a user (search by name) =="
        menu = """Enter the name of the member, followed by the desired username (e.g. 'Firstname Lastname username passwordType').
        
Password type is one of the following:

0   Password contains lowercase, uppercase, digits and special characters (shortest)
1   Password contains lowercase and uppercase
2   Password contains only lowercase
3   Password consists of five concatenated Dutch words

Password entropy is always at least 50 bits. Password length is adjusted accordingly.
"""
        state = "makeuserbyname"
    elif user_input == "7":
        output = "== Remove user =="
        menu = "Enter lidnummer and username, separated by a space (e.g. '12345 myuser')."
        state = "removeuser"
    elif user_input == "8":
        output = "== Reset password for a user =="
        menu = """Enter lidnummer or username and desired password type (0-3) for the user (e.g. myuser 3).

Password type is one of the following:

0   Password contains lowercase, uppercase, digits and special characters (shortest)
1   Password contains lowercase and uppercase
2   Password contains only lowercase
3   Password consists of five concatenated Dutch words

Password entropy is always at least 50 bits. Password length is adjusted accordingly.
"""
        state = "resetpassword"
    elif user_input == "9":
        dummy, menu, state = begin_it()
        output = check_output(["python", "list_roles.py"])
    elif user_input == "0":
        output = "== Assign role to user =="
        menu = "Enter role and username, separated by a space (e.g. 'role-lb myuser')."
        state = "giverole"
    elif user_input == "-":
        output = "== Remove role from user =="
        menu = "Enter role and username, separated by a space (e.g. 'role-lb myuser')."
        state = "removerole"
    elif user_input == "=":
        state = "quit"
    return output, menu, state

# Whenever there is user input, we process it
# The appropriate place to process user input depends on the state we are in
# Each state has its own processing function
def process_input(user_input, state):
    if state == "main":
        return process_input_main(user_input)
    elif state == "searchmembers":
        return process_input_searchmembers(user_input)
    elif state == "searchusers":
        return process_input_searchusers(user_input)
    elif state == "makeuser":
        return process_input_makeuser(user_input)
    elif state == "makeuserbyname":
        return process_input_makeuserbyname(user_input)
    elif state == "resetpassword":
        return process_input_resetpassword(user_input)
    elif state == "removeuser":
        return process_input_removeuser(user_input)
    elif state == "giverole":
        return process_input_giverole(user_input)
    elif state == "removerole":
        return process_input_removerole(user_input)
    return "", "", "main"

# The main loop
if __name__ == "__main__":
    output, menu, state = begin_it()
    while state != "quit":
        user_input = run_menu(output, menu)
        output, menu, state = process_input(user_input, state)
