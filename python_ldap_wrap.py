#/tutorial.py
import ldap
import ldap.modlist as modlist

######
'''this is the "conf" section'''
######

server     = "idmdevl.oit.pdx.edu"
username   = ""
password   = ""

######
'''here are some methods to facilitate a subset of ldap operations.'''
######

def connect(servername=server):
    '''this method will return a connection object.
        Takes a single param, specified by default in this script.

        @params:
            servername(={})- the name of the server to connect to'''\
                .format(server)

    try:
        l = ldap.open(servername)
        print "binding to server: {}".format(servername)
        l.simple_bind_s(username, password)
        return l
    except Exception, error:
        print "error connecting to server: {}\n\t{}".format(servername, error)
        return None

def disconnect(l, delete=False):
    '''this method will close the connection, unbinding from the server.

        @params:
            delete(=False) - deletes the connection object when True.'''

    l.unbind()
    if delete:
        del(l)

def _modify(l, existing_dn, before_change_dict, after_change_dict):
    '''modifies an existing entry with attributes matching before dict
        to have the attributes in after dict.

        @params:
            l - an ldap connection.
            existing_dn - a dn for the record you want to change.
            before_change_dict - dict of attrs+values you would like to 
                change for the given record.
            after_change_dict - dict of the attrs+values to change to.'''

    try:
        this_modlist = modlist.modifyModlist(before_change_dict,
            after_change_dict)
        r_id = l.modify(existing_dn, this_modlist)
        return r_id
    except Exception, error:
        print("error performing modify transaction: {}\n\t{}"\
            .format(Exception, error))
        return None

def _search(l, search, baseDN='ou=people,dc=pdx,dc=edu', scope=ldap.SCOPE_SUBTREE):
    '''this method will return a results id based on the search specified.

        @params:
            l - an ldap connection.
            search - a string or list of the search filters.
            baseDN(='ou=people,dc=pdx,dc=edu') - the base distinguished 
                name to search from.
            scope(=ldap.SCOPE_SUBTREE) - the type of search scope to use.'''

    if type(search) == str:
        r_id = l.search(baseDN, scope, search)
        return r_id
    elif type(search) == list:
        search_string = ','.join(search)
        r_id = l.search(baseDN, scope, search)
        return r_id
    else:
        print "the second parameter must be a string or list of strings."
        return None

def get_results(l, r_id):
    '''returns the results for a specific query, specified by r_id.

        @params:
            l = an ldap connection.
            r_id = the id of the results you are looking for.'''

    try:
        return l.result(r_id)
    except Exception, error:
        print("Error retrieving results:{}\n\t{}".format(Exception, error))

def modify(existing_dn, before_dict, after_dict):
    '''wraps the _modify method. cleans up.'''
    ldap_obj = connect()
    r_id = modify(ldap_obje, existing_dn, before_dict, after_dict)
    results = ldap_obj.results(r_id)
    return results

def search(search, search_params={}):
    '''does all of the search stuff in one fell swoop. then cleans up.

        @params:
            search - the search filter/s.'''

    ldap_obj = connect()

    #unpack and analyze the keys of the optional param
    for key in search_params.keys():
        has_base_dn = False
        has_scope = False
        if key.lower() == 'baseDN':
            has_base_dn = True
            base_dn = search_params[key]
        if key.lower() == 'scope':
            has_scope = True
            if 'one' in search_params[key].lower():
                scope = ldap.SCOPE_ONELEVEL
            elif 'base' in search_params[key].lower():
                scope = ldap.SCOPE_BASE
            else:
                scope = ldap.SCOPE_SUBTREE
    #different cases for specified search fields
    if has_base_dn and has_scope:
        r_id = _search(ldap_obj, search, base_dn, scope)
    elif has_base_dn:
        r_id = search(ldap_obj, search, base_dn)
    elif has_scope:
        r_id = search(ldap_obj, search, 'ou=people,dc=pdx,dc=edu', scope)
    else:
        r_id = _search(ldap_obj, search)

    #retrieve results
    results = get_results(ldap_obj, r_id)
    disconnect(ldap_obj, True)
    return results
