from . import base


class Dynamodb(base.BaseStream):
    """Resource which consumes ``Dynamodb``streams."""
    grn_type = 'dynamodb-stream'
