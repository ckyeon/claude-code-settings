from banner import banner
from greet import greet


def test_greet():
    assert greet("Ann") == "Hello, Ann!"


def test_banner():
    assert banner("Ann") == "HELLO, ANN!!!"
