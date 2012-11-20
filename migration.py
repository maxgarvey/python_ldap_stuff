from psu_ldap import *

#open up a file containing newline separated entries for each share/website
#in /vol/ read in and separate by line
fd = open('../out.file')
fs = fd.read()
fsl = fs.split('\n')
fd.close()

#print to screen and write to file given an fd and a string to write
def print_and_write(print_string, fd):
    try:
        print(print_string)
        fd.write(str(print_string))
    except Exception, error:
        print('error: {}\n\t{}'.format(Exception, error))
        try:
            fd.write('error: {}\n\t{}'.format(Exception, error))
        except:
            pass

#a dict to hold all of the results keyed on the share name
results = {}

#this loop takes care of the migration
with open('migration_out.txt','w') as fd:
    for i in fsl:
        if i is not '':
            do_modify = False #initialize do_modify variable
            try:
                i_parts = i.split(',')  #split on comma
                i1 = i_parts[0].strip() #the first part is share name
                i2 = i_parts[1].strip() #the second is owner of the share/www
                i3 = i_parts[2].strip() #the third is url of the share/www

                print_and_write(
                    'searching cn="{}"\n'.format(i2),
                    fd) #debug

                #search for the share owner in ldap
                a = search(
                    'cn={}'.format(i2),
                    {'baseDN':'dc=pdx,dc=edu'},
                    my_creds)

                #if we get a valid result
                if a != (101,[]):
                    results[i2] = a #put a record into results dict
                    print_and_write(str(a), fd) #write something
                    do_modify = True #set do_modify to true

            #error case
            except Exception, error:
                print_and_write(
                    'error: {}\n\t{}'.format(
                    Exception, error),
                    fd)

            #if successful query
            if do_modify:
                print_and_write(
                    '\nadding labeledUri field to {}\n'.format(i2),
                    fd)
                try:
                    print_and_write(
                        'b = modify("{}", {{}}, {{"labeledUri":"{}")}})\n'\
                        .format(str(results[i2][1][0][0]), i3),
                        fd)

                    try:
                        #modify the record, assuming it's already been given
                        #objectclass = labeledUriObject
                        b = modify(results[i2][1][0][0],
                            {},
                            {'labeledUri':str(i3)},
                            my_creds)
                    #this except block will be triggered if the objectclass
                    #hasn't been set.
                    except Exception, error:
                        print_and_write('there was an error adding labeledUri: {}\n\t{}\n'\
                            .format(Exception, error),fd)

                        #sets objectClass
                        b_ = modify(
                            results[i2][1][0][0],
                            {},
                            {'objectClass':'labeledURIObject'},
                            my_creds)

                        #sets labeledUri field
                        b_ = modify(
                            results[i2][1][0][0],
                            {},
                            {'labeledUri':str(i3)},
                            my_creds)

                except Exception, error:
                    print_and_write(
                        'results[i2]: {}\n'.format(results[i2]),
                        fd)
                    print_and_write(
                        'error: {}\n\t{}\n\n'.format(Exception, error),
                        fd)

                #this block does a search and attempts to verify the change
                try:
                    print_and_write(
                        're-searching cn="{}"\n'.format(i2),
                         fd)
                    a = search(
                        'cn={}'.format(i2),
                        {'baseDN':'dc=pdx,dc=edu'},
                        my_creds)

                    #if the search turns up anything
                    if a != (101,[]):
                        results[i2] = a  #set results var to the result
                        #print the labeledUri for the record
                        print_and_write(
                            str(results[i2][1][0][1]['labeledUri'])+'\n',
                            fd)
                        #print a little logic here
                        print_and_write(
                            '{} in record for: {}? {}\n'.format(
                                i1,
                                i2,
                                str(i1) in results[i2][1][0][1]['labeledUri']
                                ),
                             fd)
                except Exception, error:
                    print_and_write('error: {}\n\t{}'.format(Exception, error), fd)


def reset(outfile='migraction_out.txt'):
    with open(outfile,'w') as fd:
        for i in fsl:
            if i is not '':
                do_modify = False
                try:
                    i_pair = i.split(',')
                    i1 = i_pair[0].strip()
                    i2 = i_pair[1].strip()
                    print_and_write('searching cn="{}"\n'.format(i2), fd)
                    a = search('cn={}'.format(i2), {'baseDN':'dc=pdx,dc=edu'}, my_creds)
                    if a != (101,[]):
                        results[i2] = a
                        print_and_write(str(a), fd)
                        do_modify = True
                except Exception, error:
                    print_and_write('error: {}\n\t{}\n'.format(Exception, error), fd)

                if do_modify: #try:
                    print_and_write('\nremoving labeledUri field from {}\n'.format(i2), fd)
                    try:
                        print_and_write('b = modify("{}", {{"labeledUri":"{}")}}, {{}})\n'\
                            .format(str(results[i2][1][0][0]), i1), fd)
                        b = modify(results[i2][1][0][0], {'labeledUri':str(i1)}, {}, my_creds)
                    except Exception, error:
                        print_and_write('results[i2]: {}\n'.format(results[i2]), fd)
                        print_and_write('error: {}\n\t{}\n\n'.format(Exception, error), fd)
