from src.core.cleaner import clean_tick, clean_ohlc

def test_clean_tick_valid():
    assert clean_tick(1500.50, 1.0, 1700000000, 1600000000) == True

def test_clean_tick_invalid_price():
    assert clean_tick(-10.0, 1.0, 1700000000, 1600000000) == False

def test_clean_tick_invalid_volume():
    assert clean_tick(1500.50, -1.0, 1700000000, 1600000000) == False

def test_clean_tick_out_of_order():
    # current timestamp < last timestamp
    assert clean_tick(1500.50, 1.0, 1600000000, 1700000000) == False

def test_clean_ohlc_valid():
    assert clean_ohlc(100.0, 105.0, 95.0, 102.0, 1000.0) == True

def test_clean_ohlc_invalid():
    # High < Low -> Impossible
    assert clean_ohlc(100.0, 90.0, 105.0, 102.0, 1000.0) == False
