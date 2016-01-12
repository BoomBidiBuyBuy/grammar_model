from cases_dns import *
from cases_dhsm import *
from cases_ldap import *
from cases_ndmp import *
from cases_nfs import *
from cases_nis import *
from cases_cifs import *
from cases_nfs_share import *
from cases_cifs_share import *
from cases_nas import *
from core.timer import Timer

if __name__ == '__main__':
    Timer.enable()

    funcs = [t_nis_warnings, t_ldap_dep_errors, t_cifs_share_replication, t_ndmp_errors, t_nfs_secure, t_nas_name, t_cifs_org_unit, t_nas_change_sp, t_nas_mp_with_fs, t_nas_mp_standalone_cifs, t_ldap_cifs_using_other_account, t_ldap_bind_password, t_nfs_ahare_filesystem, t_ldap_download_upload_cacert, t_nfs_secure_win_kdc_deps, t_nas_no_dir_service_health, t_cifs_standalone, t_ldap_kerberos_credentials, t_dns_async, t_ldap_upload_content_cacert, t_cifs_share_on_filesystem_implicit_delete, t_cifs_skip_unjoin_reuse, t_nfs_share_on_snapshot, t_nfs_secure_win_kdc_deps, t_dns_errors, t_cifs_credentials, t_nas_simple, t_dns_enable, t_nas_mp_check_deps, t_nas_mp_fs_remapping, t_cifs_rename, t_dhsm_enable, t_ldap_profiledn, t_ndmp_enable, t_cifs_share_on_snapshot, t_ldap_auto_switch, t_nas_mp_health_ldap, t_cifs_standalone_errors, t_nas_mapping_report, t_ldap_simple, t_nfs_share_on_filesystem_implicit_delete, t_nfs_share_on_snapshot_implicit_delete, t_ldap_kerberos_use_cifs, t_dhsm_error, t_nfs_secure, t_nfs_secure_custom_kdc_deps, t_cifs_errors, t_ldap_basedn, t_ldap_download_upload_conf, t_cifs_domain, t_nas_mp_users, t_cifs_share_acl, t_ldap_kerberos, t_nas_mp_health_nis, t_nas_download_upload_locals, t_nfs_enable, t_ldap_binddn, t_cifs_description_field, t_nis_auto_switch, t_cifs_share_on_filesystem, t_cifs_change_type, t_ldap_ip_addresses, t_ldap_warnings, t_nis_enable, t_nas_bulk_delete, t_nfs_enable, t_nfs_secure_custom_kdc_deps ]

    for func in funcs:
        func()

    print(Timer.time())
