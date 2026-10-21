from app.analysis.rule_based_query_analyzer import QueryAnalyzer


def test_risk_query():
    analyzer = QueryAnalyzer()

    result = analyzer.analyze(
        "Analyze the risk of my portfolio."
    )

    assert result.query == "Analyze the risk of my portfolio."
    assert "risk_analysis" in result.required_capabilities


def test_portfolio_query():
    analyzer = QueryAnalyzer()

    result = analyzer.analyze(
        "Create a diversified portfolio."
    )

    assert result.query == "Create a diversified portfolio."
    assert "portfolio_management" in result.required_capabilities
    assert "investment_analysis" in result.required_capabilities


def test_investment_query():
    analyzer = QueryAnalyzer()

    result = analyzer.analyze(
        "Suggest an investment strategy."
    )

    assert result.query == "Suggest an investment strategy."
    assert "investment_analysis" in result.required_capabilities


def test_general_query():
    analyzer = QueryAnalyzer()

    result = analyzer.analyze(
        "Give me a financial overview."
    )

    assert result.query == "Give me a financial overview."
    assert "financial_analysis" in result.required_capabilities