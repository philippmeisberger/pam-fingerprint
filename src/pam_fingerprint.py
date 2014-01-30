"""
"" PAM Fingerprint
"" PAM interface implementation
""
"" @author Philipp Meisberger
""
"" Copyright 2014 Bastian Raschke, Philipp Meisberger.
"" All rights reserved. 
"""

from fingerprint.FingerprintModule import *


"""
"" Is called when a user tries to authenticate.
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_authenticate(pamh, flags, argv):

    fingerprint = FingerprintModule()
    #
    #if ( fingerprint.authenticate() == True ):
    #    
    #    return pamh.PAM_SUCCESS
    #
    #return pamh.PAM_IGNORE
    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_setcred(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_acct_mgmt(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_open_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_close_session(pamh, flags, argv):

    return pamh.PAM_SUCCESS

"""
""
""
"" @param pamh
"" @param flags
"" @param argv
"" @return integer
"""
def pam_sm_chauthtok(pamh, flags, argv):

    return pamh.PAM_SUCCESS

# Tests:
pam_sm_authenticate('', '', '')
