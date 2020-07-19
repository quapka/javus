import pytest

# FIXME finish live testing
# due to the complexity of the JavaCard world we'll test the framework using a fixed and
# only example attack


LIVE_ATR = [59, 123, 24, 0, 0, 0, 49, 192, 100, 119, 227, 3, 0, 130, 144, 0]


@pytest.mark.live
def test_using_correct_live_card():
    pass


@pytest.mark.live
class TestLiveCardRun:
    def __init__(self):
        super().__init__()
