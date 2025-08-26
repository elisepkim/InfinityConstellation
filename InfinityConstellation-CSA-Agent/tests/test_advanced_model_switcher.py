import pytest
from src.agents.advanced_model_switcher import AdvancedModelSwitcher


@pytest.fixture
def switcher():
    return AdvancedModelSwitcher()


def test_select_model_routing():
    s = AdvancedModelSwitcher()
    assert s.select_model("lead_generation") == "gpt5"
    assert s.select_model("customer_support") == "claude"
    assert s.select_model("research_query") == "mistral"
    assert s.select_model("unknown_task") == "gpt5"


def test_generate_minimal_latency(switcher):
    out = switcher.generate("Short prompt for speed", task_type="lead_generation", verbosity="minimal")
    assert isinstance(out, str)
    # Stubs mark output with provider + mode
    assert any(tag in out for tag in ("[gpt5|min]", "[claude|min]", "[mistral|min]"))


def test_invalid_verbosity_raises(switcher):
    with pytest.raises(ValueError):
        switcher.generate("x", verbosity="ultra")  # invalid verbosity


def test_fast_primary_always_minimal(switcher):
    res = switcher.fast_primary("Test primary", task_type="research_query")
    assert isinstance(res, str)
    # fast primary should indicate minimal-style output
    assert any(mark in res for mark in ("[gpt5|min]", "[claude|min]", "[mistral|min]"))