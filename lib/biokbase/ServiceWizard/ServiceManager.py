from installed_clients.CatalogClient import Catalog
from biokbase.ServiceWizard.Exceptions import IncorrectParamsException
import logging


def _lookup_service_info(catalog: Catalog, get_module_version_params: dict):
    mv = catalog.get_module_version(get_module_version_params)
    if 'dynamic_service' not in mv or mv['dynamic_service'] != 1:
        raise ValueError(
            f"Specified module is not marked as a dynamic service. ({mv['module_name']} - {mv['git_commit_hash']}")

    secure_params = catalog.get_secure_config_params(
        {'module_name': mv['module_name'], 'version': mv['git_commit_hash']})

    mounts_list = catalog.list_volume_mounts({'module_name': mv['module_name'], 'version': mv['git_commit_hash'],
                                              'client_group': 'service', 'function_name': 'service'})

    mounts = []
    if len(mounts_list) > 0:
        mounts = mounts_list[0]['volume_mounts']

    return (mv, secure_params, mounts)


def start_service(start_service_params: dict, catalog: Catalog, rancher_client):
    if not isinstance(start_service_params, dict):
        raise IncorrectParamsException(
            f"Need to provide a mapping containing 'module_name' and 'version'. You provided {start_service_params}")
    if 'module_name' not in start_service_params:
        raise IncorrectParamsException("Missing 'module_name'")
    if 'version' not in start_service_params:
        raise IncorrectParamsException("Missing 'version'")

    logging.info('START REQUEST: ' + str(start_service_params))
    module_version, secure_params, mounts = _lookup_service_info(catalog=catalog, get_module_version_params=start_service_params)
