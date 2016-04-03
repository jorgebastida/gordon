from .base import BaseResource


class Vpc(BaseResource):

    grn_type = 'vpc'

    required_settings = (
        'security-groups',
        'subnet-ids'
    )
