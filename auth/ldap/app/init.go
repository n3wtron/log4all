package app

import (
	"errors"
	ldap "github.com/mqu/openldap"
	secure "github.com/n3wtron/log4all/log4all/app"
	"github.com/revel/revel"
)

type LDAPAuth struct {
	secure.AuthInterface
}

var _auth LDAPAuth

func init() {
	secure.Register(&_auth)
}

func Connect() (*ldap.Ldap, error) {
	ldapServer, found := revel.Config.String("ldap.connection")
	if !found {
		revel.ERROR.Fatalf("Error initializing LDAP: configuration not found \"ldap.connection\"\n")
	}
	ldapConn, err := ldap.Initialize(ldapServer)
	if err == nil {
		ldapConn.SetOption(ldap.LDAP_OPT_PROTOCOL_VERSION, ldap.LDAP_VERSION2)
	} else {
		revel.ERROR.Printf("LDAP Error:%s\n", err.Error())
	}
	return ldapConn, err
}

func (this *LDAPAuth) Initialize() {
	revel.INFO.Println("Initializing LDAP auth system")
	ldapConn, err := Connect()
	if err != nil {
		revel.ERROR.Fatalf("Error initializing LDAP:%s\n", err.Error())
	} else {
		ldapConn.Close()
	}
}

func (this LDAPAuth) Name() string {
	return "LDAP"
}

func (this *LDAPAuth) Login(username, password string) (error, *secure.AuthUser) {
	ldapConn, err := Connect()
	if err != nil {
		revel.ERROR.Printf("LDAP Login Error:%s\n", err.Error())
		return err, nil
	}

	baseDn, found := revel.Config.String("ldap.baseDn")
	if !found {
		err = errors.New("LDAP Configuration \"ldap.baseDn\" not found")
		revel.ERROR.Printf("LDAP Login Error:%s\n", err.Error())
		return err, nil
	}

	//check username/password
	ldapUsername := "uid=" + username + "," + baseDn

	err = ldapConn.Bind(ldapUsername, password)
	if err != nil {
		revel.ERROR.Printf("LDAP Login Error:%s\n", err.Error())
		return err, nil
	}
	defer ldapConn.Close()
	//retrieve user information

	revel.INFO.Printf("LDAP BaseDn:%s\n", baseDn)
	//var userAttrs []string = []string{"cn"}

	userSearchResult, err := ldapConn.SearchAll(baseDn, ldap.LDAP_SCOPE_SUBTREE, "uid="+username, nil)
	if err != nil {
		revel.ERROR.Printf("LDAP Login Error:%s\n", err.Error())
		return err, nil
	}
	revel.INFO.Printf("%v\n", userSearchResult)

	// ldapsearch -x -h vlxioldap01.intra.infocamere.it -p389 -b "ou=gruppi,o=sistema camerale,c=it" "(uniqueMember= uid=YYI3842,ou=utenti,o=Sistema Camerale,c=It)"

	groupsSearchResult, err := ldapConn.SearchAll(baseDn, ldap.LDAP_SCOPE_SUBTREE, "uid="+username, nil)
	if err != nil {
		revel.ERROR.Printf("LDAP Login Error:%s\n", err.Error())
		return err, nil
	}
	revel.INFO.Printf("%v\n", groupsSearchResult)

	return nil, nil
}

func (this LDAPAuth) Logout(secure.AuthUser) {
}
