/* 
 * compile it:
 *  ~$ gcc -fPIC -DPIC -shared -rdynamic -o pam_fingerprint.so pam_fingerprint.c
 *
 * Before compiling install package:
 * libpam0g-dev
 * 
 * install it:
 * ~# cp pam_fingerprint.so /lib/x86_64-linux-gnu/security/pam_fingerprint.so
 * ~# chown root:root /lib/x86_64-linux-gnu/security/pam_fingerprint.so
 * ~# chmod 644 /lib/x86_64-linux-gnu/security/pam_fingerprint.so
 */
 
#define PAM_SM_AUTH

/* Include PAM headers */
#include <security/pam_modules.h>
#include <security/_pam_macros.h>

/*#include <Python.h>*/
/*#include <stdio.h>
#include <unistd.h>
#include <pwd.h>*/


/* PAM entry point for authentication verification */
PAM_EXTERN
int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    /*FILE *f;

    Py_Initialize(); 
    PySys_SetPath("."); 
    Py_InitModule("Fingerprint");

    f = fopen("fingerprint-check.py", "r"); 
    PyRun_SimpleFile(f, "fingerprint-check.py"); 
    fclose(f);

    Py_Finalize();*/ 

    return(PAM_SUCCESS);
}

/*
 * PAM entry point for setting user credentials (that is, to actually
 * establish the authenticated user's credentials to the service provider)
*/
PAM_EXTERN
int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_SUCCESS);
}
