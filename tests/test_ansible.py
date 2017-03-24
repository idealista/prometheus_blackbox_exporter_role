import pytest


@pytest.fixture()
def AnsibleDefaults(Ansible):
    return Ansible("include_vars", "defaults/main.yml")["ansible_facts"]


@pytest.fixture()
def AnsibleVarBinDir(Ansible):
    return Ansible("debug", "msg={{ blackbox_exporter_bin_path }}")["msg"]


@pytest.fixture()
def AnsibleVars(Ansible):
    return Ansible("include_vars", "tests/group_vars/group01.yml")["ansible_facts"]


def test_blackbox_exporter_user(User, Group, AnsibleDefaults):
    assert User(AnsibleDefaults["blackbox_exporter_user"]).exists
    assert Group(AnsibleDefaults["blackbox_exporter_group"]).exists
    assert User(AnsibleDefaults["blackbox_exporter_user"]).group == AnsibleDefaults["blackbox_exporter_group"]


def test_blackbox_exporter_conf(File, User, Group, AnsibleDefaults):
    conf_path = File(AnsibleDefaults["blackbox_exporter_root_path"])
    assert conf_path.exists
    assert conf_path.is_directory
    assert conf_path.user == AnsibleDefaults["blackbox_exporter_user"]
    assert conf_path.group == AnsibleDefaults["blackbox_exporter_group"]


def test_blackbox_exporter_executable(File, Command, AnsibleDefaults, AnsibleVarBinDir):
    blackbox_exporter = File(AnsibleDefaults["blackbox_exporter_bin_path"] + "/blackbox_exporter")
    blackbox_exporter_link = File("/usr/bin/blackbox_exporter")
    assert blackbox_exporter.exists
    assert blackbox_exporter.is_file
    assert blackbox_exporter.user == AnsibleDefaults["blackbox_exporter_user"]
    assert blackbox_exporter.group == AnsibleDefaults["blackbox_exporter_group"]
    assert blackbox_exporter_link.exists
    assert blackbox_exporter_link.is_symlink
    assert blackbox_exporter_link.linked_to == AnsibleVarBinDir + "/blackbox_exporter"
    blackbox_exporter_version = Command("blackbox_exporter -version")
    assert blackbox_exporter_version.rc is 0
    assert "version " + AnsibleDefaults["blackbox_exporter_version"] in blackbox_exporter_version.stdout


def test_blackbox_exporter_service(File, Service, Socket, AnsibleVars):
    port = AnsibleVars["blackbox_exporter_port"]
    assert File("/etc/systemd/system/blackbox_exporter.service").exists
    assert Service("blackbox_exporter").is_running
    assert Socket("tcp://:::" + str(port)).is_listening
