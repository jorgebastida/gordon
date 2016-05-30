import pkg_resources


def get_version():  # pragma: no cover
    return pkg_resources.require("gordon")[0].version
