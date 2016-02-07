from . import base


class Kinesis(base.BaseStream):
    """Resource which consumes ``Kinesis``streams."""
    grn_type = 'kinesis-stream'
