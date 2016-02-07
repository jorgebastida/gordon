import pkg_resources


def get_version():
    return pkg_resources.require("gordon")[0].version
