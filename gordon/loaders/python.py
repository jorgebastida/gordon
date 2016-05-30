import sys
import time
import json
import uuid
import importlib


class LambdaContext(object):

    def __init__(self, function_name, memory_limit_in_mb, timeout, function_version='current'):
        self.function_name = function_name
        self.memory_limit_in_mb = memory_limit_in_mb
        self.timeout = timeout
        self.function_version = function_version
        self.timeout = timeout
        self.invoked_function_arn = 'invoked_function_arn'
        self.log_group_name = 'log_group_name'
        self.log_stream_name = 'log_stream_name'
        self.identity = None
        self.client_context = None
        self.aws_request_id = str(uuid.uuid4())
        self.start_time = time.time() * 1000

    def get_remaining_time_in_millis(self):
        return max(self.timeout * 1000 - int((time.time() * 1000) - self.start_time), 0)


def main(handler, name, memory, timeout):
    sys.path.insert(0, '.')
    module_name, handler_name = handler.rsplit('.', 1)
    module = importlib.import_module(module_name)
    out = getattr(module, handler_name)(
        json.loads(sys.stdin.read()),
        LambdaContext(
            function_name=name,
            memory_limit_in_mb=memory,
            timeout=timeout
        )
    )
    print("output: {}".format(out))

if __name__ == '__main__':
    main(
        handler=sys.argv[1],
        name=sys.argv[2],
        memory=sys.argv[3],
        timeout=sys.argv[4],
    )
