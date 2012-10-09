#/tutorial.py
import ldap.modlist as modlist
import ldap
import os

######
'''this is the "conf" section'''
######

class credentials(object):
    '''a class to hold credentials.'''
    def __init__(self):
        '''init method.'''
        #default values.
        self.creds = {
            'server':'',
            'username':'',
            'password':'',
        }
        #check for conf file.
        #print 'cwd: {0}'.format(os.getcwd()) #debug
        if 'conf.py' in os.listdir(os.getcwd()):
            from conf import conf
            self.edit_creds(conf['username'],
                conf['password'], conf['server'])
            del(conf)
            print('creds.py file found. setting credentials accordingly:'+\
                '\ncreds = {0}'.format(self.creds))

    def __str__(self):
        '''to string method.'''
        return str(self.creds)

    def edit_creds(self, username, password, server=''):
        '''this function will change the credentials that the ldap
            connection object will use in trying to connect.

            @params:
                username - the username to use.
                password - the password to use.
                server(=server(as defined above)) - the server to bind to.
        '''
        self.creds['username'] = username
        self.creds['password'] = password
        if server is not '':
            self.creds['server']   = server

    def edit_username(self, username=''):
        '''setter for username.

        @params:
            username - the username to set.'''
        if username is not '':
            self.creds['username'] = username

    def edit_password(self, password=''):
        '''setter for username.

        @params:
            password - the password to set.'''
        if password is not '':
            self.creds['password'] = password

    def edit_server(self, server=''):
        '''setter for server.

        @params:
            server - the server to set.'''
        if server is not '':
            self.creds['server'] = server

#default object created
my_creds = credentials()
print 'my_creds: {0}'.format(my_creds)  #debug

######
'''here are some methods to facilitate a subset of ldap operations.'''
######

def connect(creds_obj=my_creds):
    '''this method will return a connection object.
        Takes a single param, specified by default in this script.

        @params:
            servername() - the name of the server to connect to'''

    try:
        l = ldap.open(creds_obj.creds['server'])
        print "binding to server: {0}".format(creds_obj.creds['server']) #debug
        print 'creds: {0}'.format(creds_obj) #debug
        l.simple_bind_s(my_creds.creds['username'], my_creds.creds['password'])
        print 'bound to server' #debug
        return l
    except Exception, error:
        print "error connecting to server: {0}\n\t{1}".format(creds_obj.creds['server'], error)
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
            l                  - an ldap connection.
            existing_dn        - a dn for the record you want to change.
            before_change_dict - dict of attrs+values you would like to 
                change for the given record.
            after_change_dict  - dict of the attrs+values to change to.'''

    try:
        this_modlist = modlist.modifyModlist(before_change_dict,
            after_change_dict)
        r_id = l.modify(existing_dn, this_modlist)
        return r_id
    except Exception, error:
        print("error performing modify transaction: {0}\n\t{1}"\
            .format(Exception, error))
        return None

def _modify_rdn(l, existing_dn, modification, delete_orig):
    '''modifies the rdn of an existing record.

        @params:
            l              - and ldap connection.
            existing_dn    - the dn we wnat to change.
            modification   - a string representation of the change.
            delete_orig    - boolean value, whether to delete the original
                             rdn value.'''
    try:
        r_id = l.modrdn(existing_dn, modification, delete_orig)
        return r_id
    except Exception, error:
        print('error performing modify_rdn transaction: {0}\n\t{1}'\
            .format(Exception, error))
        return None

def _search(l, search, baseDN='ou=people,dc=pdx,dc=edu', scope=ldap.SCOPE_SUBTREE):
    '''this method will return a results id based on the search specified.

        @params:
            l       - an ldap connection.
            search  - a string or list of the search filters.
            baseDN(='ou=people,dc=pdx,dc=edu') - the base distinguished 
                name to search from.
            scope(=ldap.SCOPE_SUBTREE) - the type of search scope to use.'''

    #print 'search: {0}, type(search): {1}'.format(search, type(search)) #debug

    if type(search) == str:
        r_id = l.search(baseDN, scope, search)
        return r_id
    elif type(search) == list:
        search_string = ','.join(search)
        r_id = l.search(baseDN, scope, search)
        return r_id
    elif type(search) == unicode:
        r_id = l.search(baseDN, scope, search)
        return r_id
    else:
        print "the second parameter must be a string or list of strings."
        return None

def get_results(l, r_id):
    '''returns the results for a specific query, specified by r_id.

        @params:
            l    = an ldap connection.
            r_id = the id of the results you are looking for.'''

    try:
        return l.result(r_id)
    except Exception, error:
        print("Error retrieving results:{0}\n\t{1}".format(Exception, error))

def modify(existing_dn, before_dict, after_dict, creds_obj=None):
    '''wraps the _modify method. cleans up.

        @params:
            existing_dn - the dn of the record you want to modify.
            before_dict - a key:value dict of fields to be changed and their
                initial values.
            after_dict  - a key:value dict of fields to be changed and the
                values they should have afterwards.'''
    if creds_obj is not None:
        try:
            ldap_obj = connect(creds_obj)
        except Exception, err:
            print 'error with specified config: {0}\n\t{1}'\
                .format(Exception, error)
            try:
                ldap_obj = connect()
            except Exception, error:
                print 'error with default config: {0}\n\t{1}'\
                    .format(Exception, error)
    r_id = _modify(ldap_obj, existing_dn, before_dict, after_dict)
    results = ldap_obj.result(r_id)
    return results

def modify_rdn(existing_dn, modification, creds_obj=None, delete_orig=True):
    '''wraps the _modify method. cleans up.

        @params:
            existing_dn - the dn of the record you want to modify.
            before_dict - a key:value dict of fields to be changed and their
                initial values.
            after_dict  - a key:value dict of fields to be changed and the
                values they should have afterwards.'''
    if creds_obj is not None:
        try:
            ldap_obj = connect(creds_obj)
        except Exception, error:
            print 'error with specified config: {0}\n\t{1}'\
                .format(Exception, error)
            try:
                ldap_obj = connect()
            except Exception, error:
                print 'error with default config: {0}\n\t{1}'\
                    .format(Exception, error)
    r_id = _modify_rdn(ldap_obj, existing_dn, modification, delete_orig)
    results = ldap_obj.result(r_id)
    return results

def search(search_in, search_params={}, creds_obj=None):
    '''does all of the search stuff in one fell swoop. then cleans up.

        @params:
            search - the search filter/s.'''

    if creds_obj is not None:
        try:
            ldap_obj = connect(creds_obj)
        except Exception, error:
            print 'error with specified config: {0}\n\t{1}'\
                .format(Exception, error)
            try:
                ldap_obj = connect()
            except Exception, error:
                print 'error with default config: {0}\n\t{1}'\
                    .format(Exception, error)

    has_base_dn = False
    has_scope = False

    #unpack and analyze the keys of the optional param
    for key in search_params.keys():
        if key.lower() == 'basedn':
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
        r_id = _search(ldap_obj, search_in, base_dn, scope)
    elif has_base_dn:
        r_id = _search(ldap_obj, search_in, base_dn)
    elif has_scope:
        r_id = _search(ldap_obj, search_in, 'ou=people,dc=pdx,dc=edu', scope)
    else:
        r_id = _search(ldap_obj, search_in)

    #retrieve results
    results = get_results(ldap_obj, r_id)
    disconnect(ldap_obj, True)
    print 'results: {0}'.format(results) #debug
    return results
