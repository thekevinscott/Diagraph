from .historical_bidict import HistoricalBidict


def describe_historical_bidict():
    def test_it_instantiates():
        HistoricalBidict()

    def test_it_instantiates_with_data():
        hdict = HistoricalBidict()
        hdict["foo"] = "bar"

        assert hdict["foo"] == "bar"
        assert hdict.inverse("bar") == "foo"

    def test_it_appends_new_data():
        hdict = HistoricalBidict()
        hdict["foo"] = "bar"

        assert hdict["foo"] == "bar"
        hdict["foo"] = "baz"
        assert hdict["foo"] == "baz"
        assert hdict.historical("foo", -1) == "baz"
        assert hdict.historical("foo", -2) == "bar"
