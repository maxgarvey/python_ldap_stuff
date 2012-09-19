from psu_ldap import *

fd = open('../out.file')
fs = fd.read()
fsl = fs.split('\n')

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

results = {}

#this loop takes care of the migration
with open('migration_out.txt','w') as fd:
    for i in fsl:
        if i is not '':
            do_modify = False
            try:
                i_parts = i.split(',')
                i1 = i_parts[0].strip()
                i2 = i_parts[1].strip()
                i3 = i_parts[2].strip()
                print_and_write('searching cn="{}"\n'.format(i2), fd)
                a = search('cn={}'.format(i2), {'baseDN':'dc=pdx,dc=edu'}, my_creds)
                if a != (101,[]):
                    results[i2] = a
                    print_and_write(str(a), fd)
                    do_modify = True
            except Exception, error:
                print_and_write('error: {}\n\t{}'.format(Exception, error), fd)

            if do_modify: #try:
                print_and_write('\nadding labeledUri field to {}\n'.format(i2), fd)
                try:
                    print_and_write('b = modify("{}", {{}}, {{"labeledUri":"{}")}})\n'\
                        .format(str(results[i2][1][0][0]), i3), fd)

                    ######
                    '''this next line modifies the record, but it won't work
                    for ou=Group because of the object class. 9-14-12.'''
                    ######
                    try:
                        b = modify(results[i2][1][0][0], {}, {'labeledUri':str(i3)}, my_creds)
                    except Exception, error:
                        print_and_write('there was an error adding labeledUri: {}\n\t{}\n'\
                            .format(Exception, error),fd)
                        b_ = modify(results[i2][1][0][0], {}, {'objectClass':'labeledURIObject'}, my_creds)
                        b_ = modify(results[i2][1][0][0], {}, {'labeledUri':str(i3)}, my_creds)
                except Exception, error:
                    print_and_write('results[i2]: {}\n'.format(results[i2]), fd)
                    print_and_write('error: {}\n\t{}\n\n'.format(Exception, error), fd)

                try:
                    print_and_write('re-searching cn="{}"\n'.format(i2), fd)
                    a = search('cn={}'.format(i2), {'baseDN':'dc=pdx,dc=edu'}, my_creds)
                    if a != (101,[]):
                        results[i2] = a
                        print_and_write(str(results[i2][1][0][1]['labeledUri'])+'\n', fd)
                        print_and_write('{} in record for: {}? {}\n'.format(i1, i2, (str(i1) in results[i2][1][0][1]['labeledUri'])), fd)
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
