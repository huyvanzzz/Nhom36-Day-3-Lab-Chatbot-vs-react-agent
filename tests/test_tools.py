from src.tools.travel_tools import hotel_lookup, itinerary_planner, ticket_offer_lookup


def test_hotel_lookup_returns_sources():
    result = hotel_lookup(destination="phu_quoc", group_type="family", nights=2)

    assert result["status"] == "success"
    assert result["hotels"][0]["source_url"].startswith("https://")


def test_ticket_offer_lookup_calculates_group_total():
    result = ticket_offer_lookup(destination="phu_quoc", adults=2, children=2)

    assert result["offers"][0]["estimated_subtotal_vnd"] > 0
    assert result["offers"][0]["source_url"].startswith("https://")


def test_itinerary_planner_returns_budget_and_sources():
    result = itinerary_planner(destination="phu_quoc", adults=2, children=2, budget_vnd=15000000)

    assert result["estimated_cost_vnd"] > 0
    assert result["sources"]
