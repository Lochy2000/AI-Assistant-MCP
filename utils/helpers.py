def parse_kwargs(arg_string):
    """
    Parses 'key=value' strings into a dictionary of kwargs.
    Example:
        'action=write path=test.txt content="Hello world"' ->
        {'action': 'write', 'path': 'test.txt', 'content': 'Hello world'}
    """
    import shlex
    import re

    # Use shlex to split while respecting quotes
    tokens = shlex.split(arg_string)
    kwargs = {}

    for token in tokens:
        if '=' in token:
            key, value = token.split('=', 1)
            # Remove quotes manually if present
            value = re.sub(r'^["\']|["\']$', '', value)
            kwargs[key] = value
    return kwargs
