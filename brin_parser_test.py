from datetime import datetime
from brin_parser import parse_datetime_tuple

def test_parse_datetime_tuple_millis_tz():
    res = parse_datetime_tuple("{2016-11-02 05:41:14.537+00 .. 2019-01-20 22:59:06.511+00}")
    assert res[0] == datetime(2016, 11, 2, 5, 41, 14)
    assert res[1] == datetime(2019, 1, 20, 22, 59, 6)

def test_parse_datetime_tuple_millis_no_tz():
    res = parse_datetime_tuple("{2016-11-02 05:41:14.537 .. 2019-01-20 22:59:06.511}")
    assert res[0] == datetime(2016, 11, 2, 5, 41, 14)
    assert res[1] == datetime(2019, 1, 20, 22, 59, 6)

def test_parse_datetime_tuple_no_millis_no_tz():
    res = parse_datetime_tuple("{2016-11-02 05:41:14 .. 2019-01-20 22:59:06}")
    assert res[0] == datetime(2016, 11, 2, 5, 41, 14)
    assert res[1] == datetime(2019, 1, 20, 22, 59, 6)

