from pytest import approx

from app.analysis.query_analyzer import QueryAnalyzer


def test_annual_return_normalization_converts_percent_points_to_decimal():
    assert QueryAnalyzer._normalize_annual_return(
        10,
        "assuming 10% annual return",
    ) == approx(0.10)

    assert QueryAnalyzer._normalize_annual_return(
        0.10,
        "expected annual return",
    ) == approx(0.10)

    assert QueryAnalyzer._normalize_annual_return(
        1,
        "assuming 1% return",
    ) == approx(0.01)

    assert QueryAnalyzer._normalize_annual_return(
        10,
        "TCS 50%, INFY 50%, expected annual return 10%",
    ) == approx(0.10)