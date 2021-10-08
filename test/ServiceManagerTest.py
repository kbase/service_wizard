import pytest
from lib.installed_clients.CatalogClient import Catalog
from lib.biokbase.ServiceWizard.ServiceManager import start_service
from lib.biokbase.ServiceWizard.Impl import ServiceWizard
from configparser import ConfigParser
from unittest.mock import create_autospec, call
from pytest import fixture

# Module Name
MODULE_NAME = "StaticNarrative"
GIT_COMMIT_HASH = "9e1764dd92e86bcefb804127ac52a958b8dab186"
VERSION_TAG = "dev"

# Requests
sample_service_start_request = {"module_name": MODULE_NAME, "version": VERSION_TAG}

# Catalog Responses
catalog_get_module_version_response = {
    "module_name": MODULE_NAME,
    "released": 0,
    "released_timestamp": None,
    "notes": "",
    "timestamp": 1603397275959,
    "registration_id": "1603397275959_4114b375-4bd9-4a65-ba60-4931ae3b0238",
    "version": "0.0.14",
    "git_commit_hash": GIT_COMMIT_HASH,
    "git_commit_message": "Merge pull request #34 from MrCreosote/master\n\nFix None vs. int comparison bug",
    "narrative_methods": [],
    "local_functions": [],
    "docker_img_name": "dockerhub-ci.kbase.us/kbase:staticnarrative.9e1764dd92e86bcefb804127ac52a958b8dab186",
    "dynamic_service": 1,
    "git_url": "https://github.com/kbaseapps/StaticNarrative",
    "release_tags": ["beta", "dev"],
    "release_timestamp": None,
}
catalog_secure_vars_response = [
    {
        "module_name": MODULE_NAME,
        "version": "",
        "param_name": "service_token1",
        "param_value": "password123",
        "is_password": 1,
    },
    {
        "module_name": MODULE_NAME,
        "version": "",
        "param_name": "admin_token1",
        "param_value": "password321",
        "is_password": 1,
    },
]
catalog_volume_mounts_response = [
    {
        "module_name": MODULE_NAME,
        "function_name": "service",
        "client_group": "service",
        "volume_mounts": [
            {
                "host_dir": "/data/static_narratives",
                "container_dir": "/kb/module/work/nginx",
                "read_only": 0,
            }
        ],
    }
]


@fixture(scope="module")
def sw():
    """Mock out catalog and rancher clients"""
    c = ConfigParser()
    c.read("test.cfg")
    config = dict(c["ServiceWizard"])
    sw = ServiceWizard(config=config)
    sw.catalog_admin_client = create_autospec(Catalog, spec_set=True, instance=True)
    sw.catalog_admin_client.get_module_version.return_value = (
        catalog_get_module_version_response
    )
    sw.catalog_admin_client.get_secure_config_params.return_value = (
        catalog_secure_vars_response
    )
    sw.catalog_admin_client.list_volume_mounts.return_value = (
        catalog_volume_mounts_response
    )
    # sw.rancher_client = create_autospec(Rancher, spec_set=True, instance=True)
    return sw


#
#
# @fixture(scope="module")
# def catalog_():


def test_status_ok():
    c = ConfigParser()
    c.read("test.cfg")
    config = dict(c["ServiceWizard"])
    s = ServiceWizard(config=config)
    status = s.status(ctx=None)[0]
    assert status["message"] == ""
    assert status["state"] == "OK"
    assert status["version"] == ServiceWizard.VERSION
    assert status["git_url"] == ServiceWizard.GIT_URL
    assert status["git_commit_hash"] == ServiceWizard.GIT_COMMIT_HASH
    assert len(status.keys()) == 5


def test_start_service_catalog_call(sw):
    sw.start(ctx=None, service=sample_service_start_request)
    sw.catalog_admin_client.get_module_version.assert_called_with(
        {"module_name": MODULE_NAME, "version": VERSION_TAG}
    )
    sw.catalog_admin_client.get_secure_config_params.assert_called_with(
        {"module_name": MODULE_NAME, "version": GIT_COMMIT_HASH}
    )
    sw.catalog_admin_client.list_volume_mounts.assert_called_with(
        {
            "module_name": MODULE_NAME,
            "version": GIT_COMMIT_HASH,
            "client_group": "service",
            "function_name": "service",
        }
    )
