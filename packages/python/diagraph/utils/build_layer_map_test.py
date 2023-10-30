from .build_layer_map import build_layer_map
import networkx as nx


def describe_build_layer_map():
    def test_it_builds_empty_layer_map():
        G = nx.DiGraph({})
        assert build_layer_map(G) == ({}, {})

    def test_it_builds_single_layer_map():
        G = nx.DiGraph({"a": []})
        assert build_layer_map(G) == ({0: ["a"]}, {"a": 0})

    def test_it_builds_double_layer_map():
        G = nx.DiGraph({"a": ["b"], "b": []})
        assert build_layer_map(G) == ({1: ["a"], 0: ["b"]}, {"a": 1, "b": 0})

    def test_it_builds_triple_layer_map():
        G = nx.DiGraph({"a": ["b"], "b": ["c"], "c": []})
        assert build_layer_map(G) == (
            {2: ["a"], 1: ["b"], 0: ["c"]},
            {
                "a": 2,
                "b": 1,
                "c": 0,
            },
        )

    def test_it_builds_triple_interconnected_layer_map():
        G = nx.DiGraph({"a": ["b", "c"], "b": ["c"], "c": []})
        assert build_layer_map(G) == (
            {2: ["a"], 1: ["b"], 0: ["c"]},
            {
                "a": 2,
                "b": 1,
                "c": 0,
            },
        )

    def test_it_builds_double_root_node_layer_map():
        G = nx.DiGraph({"a": ["c"], "b": ["c"], "c": []})
        assert build_layer_map(G) == (
            {1: ["a", "b"], 0: ["c"]},
            {"a": 1, "b": 1, "c": 0},
        )

    def test_it_builds_double_terminal_node_layer_map():
        G = nx.DiGraph({"a": ["b", "c"], "b": [], "c": []})
        assert build_layer_map(G) == (
            {1: ["a"], 0: ["b", "c"]},
            {"a": 1, "b": 0, "c": 0},
        )

    def test_it_builds_diamond_map():
        G = nx.DiGraph({"a": ["b", "c"], "b": ["d"], "c": ["d"]})
        assert build_layer_map(G) == (
            {2: ["a"], 1: ["b", "c"], 0: ["d"]},
            {
                "a": 2,
                "b": 1,
                "c": 1,
                "d": 0,
            },
        )

    def test_it_builds_interconnected_diamond_map():
        G = nx.DiGraph({"a": ["b", "c", "d"], "b": ["d"], "c": ["d"]})
        assert build_layer_map(G) == (
            {2: ["a"], 1: ["b", "c"], 0: ["d"]},
            {
                "a": 2,
                "b": 1,
                "c": 1,
                "d": 0,
            },
        )

    def test_it_builds_complicated_graph():
        G = nx.DiGraph(
            {
                "l3_l": ["l2_l"],
                # "l3_l": ["l2_l", "l1_r", "l0"],
                "l2_r": ["l1_r"],
                "l2_l": ["l1_l", "l1_r"],
                "l1_r": ["l0"],
                "l1_l": ["l0"],
                "l0": [],
            }
        )
        assert build_layer_map(G) == (
            {
                0: ["l0"],
                1: ["l1_r", "l1_l"],
                2: ["l2_r", "l2_l"],
                3: ["l3_l"],
            },
            {"l0": 0, "l1_r": 1, "l1_l": 1, "l2_r": 2, "l2_l": 2, "l3_l": 3},
        )

    def test_it_builds_more_complicated_graph():
        G = nx.DiGraph(
            {
                "l4": ["l3_l", "l1_r", "l2_r"],
                "l3_l": ["l2_l", "l1_r", "l0"],
                "l2_r": ["l1_r"],
                "l2_l": ["l1_l", "l1_r"],
                "l1_r": ["l0"],
                "l1_l": ["l0"],
                "l0": [],
            }
        )
        assert build_layer_map(G) == (
            {
                0: ["l0"],
                1: ["l1_r", "l1_l"],
                2: ["l2_r", "l2_l"],
                3: ["l3_l"],
                4: ["l4"],
            },
            {"l0": 0, "l1_r": 1, "l1_l": 1, "l2_r": 2, "l2_l": 2, "l3_l": 3, "l4": 4},
        )
