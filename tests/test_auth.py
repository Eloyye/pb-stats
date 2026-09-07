"""Unit coverage for the loopback session credential and origin checks."""

import pytest

from pb_stats.auth import SAFE_METHODS, LocalAuth


def test_authority_and_origin_derive_from_port() -> None:
    auth = LocalAuth(port=8765, session_token="test-session")
    assert auth.authority == "127.0.0.1:8765"
    assert auth.origin == "http://127.0.0.1:8765"


def test_empty_session_token_is_rejected() -> None:
    with pytest.raises(ValueError, match="session credential"):
        LocalAuth(port=8765, session_token="")


def test_host_verification_rejects_untrusted_hosts() -> None:
    auth = LocalAuth(port=8765, session_token="test-session")
    assert auth.verify_host("127.0.0.1:8765")
    assert not auth.verify_host("127.0.0.1:9999")
    assert not auth.verify_host("attacker.example:8765")
    assert not auth.verify_host("")
    assert not auth.verify_host(None)


def test_origin_rules_distinguish_reads_from_mutations() -> None:
    auth = LocalAuth(port=8765, session_token="test-session")
    assert auth.allows_origin(None)
    assert auth.allows_origin(auth.origin)
    assert not auth.allows_origin("https://attacker.example")
    assert not auth.allows_mutation_origin(None)
    assert auth.allows_mutation_origin(auth.origin)


def test_token_comparison_rejects_wrong_credentials() -> None:
    auth = LocalAuth(port=8765, session_token="test-session")
    assert auth.verify_token("test-session")
    assert not auth.verify_token("wrong")
    assert not auth.verify_token("")


def test_safe_methods_cover_read_only_verbs() -> None:
    assert frozenset({"GET", "HEAD", "OPTIONS"}) == SAFE_METHODS
