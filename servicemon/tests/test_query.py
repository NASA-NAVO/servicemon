import re
from servicemon.query import compute_user_agent


def test_user_agent(capsys):
    custom_agent = 'MyUserAgent/4.3 (comment string)'
    ua = compute_user_agent(custom_agent)
    assert ua == custom_agent

    default_ua = compute_user_agent(None)
    expected = (
        r'servicemon\/[0-9]\.[0-9][^ ]* \(IVOA\-monitor https\:\/\/github.com\/NASA-NAVO\/servicemon\) Python/3\.')
    match = re.search(expected, default_ua)
    assert match
