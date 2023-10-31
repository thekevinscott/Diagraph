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

    def test_it_appends_all_kinds_of_data():
        hdict = HistoricalBidict()
        class FakeClass:
            pass
        for key, value in [
            ("int", 1),
            ("float", 1.5),
            ("tuple", (1,2,3)),
            ("list", [1,2,3]),
            ("dict", { "foo": "bar" }),
            ("set", set([1,2,3])),
            ("frozenset", frozenset([1,2,3])),
            ("class_def", FakeClass),
            ("instantiated_class", FakeClass()),
        ]:
            hdict[key] = value
            assert hdict.inverse(value) == key
            assert hdict.historical(key, -1) == value
