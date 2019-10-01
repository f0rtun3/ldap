#!/usr/bin/python

import csv
from random import randint

import ldap
import ldap.modlist as modlist

try:
    conn = ldap.initialize('ldap://localhost:389')
    conn.simple_bind_s('cn=<ADMIN_COMMON_NAME>,dc=<DOMAIN_CONTROLLER>,dc=<DOMAIN_CONTROLLER>', '<PASSWORD>')

except ldap.LDAPError, e:
    print e


def check_replication(given_name, sn):
    """
    check whether a replication may occuur,
    if so add a string of random integer to the common name and the uid
    """
    if query_ldap(str(given_name + " " + sn)):
	random_str_addon = generate_random_digits()
        return {
            "cn": given_name + " " + sn + " " + random_str_addon,
            "uid": given_name + "." + sn + random_str_addon
        }

    return {
        "cn": given_name + " " + sn,
        "uid": given_name + "." + sn
    }


def query_ldap(query_uid):
    """
    query ldap for an existing user
    """
    query = "(cn=%s)" % query_uid
    ldap_base = "dc=ldap,dc=com"
    return conn.search_s(ldap_base, ldap.SCOPE_SUBTREE, query)


def generate_random_digits(n=4):
    """
    generate a random 4 digit string
    you may change this to whatever length you want when calling the function
    """
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return str(randint(range_start, range_end))


with open('<USER_CSV_FILE>') as csvfile:
    """
    sample csv is provided in the repo
    you may decide whatever default password policy you may choose however.
    """
    readCSV = csv.reader(csvfile, delimiter=',')

    for row in readCSV:
        new_user = check_replication(row[0],  row[1])
        uid = new_user['uid']
        print "Adding " + new_user['cn']
        dn = "cn=" + new_user['cn'] + ",dc=ldap,dc=com"
        attrs = {
            'objectClass': ['top', 'person', 'organizationalPerson', 'InetOrgPerson'],
            'sn': str(row[1]),
            'givenName': str(row[0]),
            'uid': new_user['uid'],
            'cn': new_user['cn'],
            'userPassword': str(row[1]) + "2019"
        }

        ldif = modlist.addModlist(attrs)

        conn.add_s(dn, ldif)

conn.unbind_s()
print "All Done"
