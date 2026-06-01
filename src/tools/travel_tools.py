from typing import Any, Dict, List, Optional


HOTELS = {
    "phu_quoc": [
        {
            "name": "Vinpearl Resort & Spa Phu Quoc",
            "fit": "family",
            "area": "Bai Dai",
            "estimated_price_vnd_per_night": 3200000,
            "highlights": ["near VinWonders", "beachfront", "family-friendly pool"],
            "source_url": "https://vinpearl.com/vi/hotels/vinpearl-resort-spa-phu-quoc",
        },
        {
            "name": "VinHolidays Fiesta Phu Quoc",
            "fit": "budget",
            "area": "Grand World",
            "estimated_price_vnd_per_night": 1800000,
            "highlights": ["near Grand World", "efficient for short stays"],
            "source_url": "https://vinpearl.com/vi/hotels/vinholidays-fiesta-phu-quoc",
        },
    ],
    "nha_trang": [
        {
            "name": "Vinpearl Resort Nha Trang",
            "fit": "family",
            "area": "Hon Tre",
            "estimated_price_vnd_per_night": 3000000,
            "highlights": ["island resort", "near VinWonders Nha Trang"],
            "source_url": "https://vinpearl.com/vi/hotels/vinpearl-resort-nha-trang",
        }
    ],
}

TICKETS = {
    "phu_quoc": [
        {
            "name": "VinWonders Phu Quoc standard ticket",
            "adult_price_vnd": 950000,
            "child_price_vnd": 710000,
            "source_url": "https://vinwonders.com/vi/tickets/",
            "warning": "Mock price for lab demo. Verify live price before booking.",
        },
        {
            "name": "Vinpearl Safari Phu Quoc standard ticket",
            "adult_price_vnd": 650000,
            "child_price_vnd": 490000,
            "source_url": "https://vinwonders.com/vi/tickets/",
            "warning": "Mock price for lab demo. Verify live price before booking.",
        },
    ],
    "nha_trang": [
        {
            "name": "VinWonders Nha Trang standard ticket",
            "adult_price_vnd": 950000,
            "child_price_vnd": 710000,
            "source_url": "https://vinwonders.com/vi/tickets/",
            "warning": "Mock price for lab demo. Verify live price before booking.",
        }
    ],
}


def hotel_lookup(
    destination: str = "phu_quoc",
    group_type: Optional[str] = None,
    budget_vnd: Optional[int] = None,
    nights: int = 2,
    **_: Any,
) -> Dict[str, Any]:
    destination_key = _normalize_destination(destination)
    hotels = HOTELS.get(destination_key, [])
    if group_type:
        preferred = [hotel for hotel in hotels if hotel["fit"] == group_type]
        hotels = preferred or hotels

    if budget_vnd:
        hotels = [
            hotel
            for hotel in hotels
            if hotel["estimated_price_vnd_per_night"] * max(nights, 1) <= budget_vnd
        ] or HOTELS.get(destination_key, [])

    return {
        "status": "success" if hotels else "no_data",
        "destination": destination_key,
        "hotels": hotels[:3],
        "warnings": [
            "Prices are mock values for the lab and must be verified on the official booking page."
        ],
    }


def ticket_offer_lookup(
    destination: str = "phu_quoc",
    adults: int = 2,
    children: int = 0,
    date: Optional[str] = None,
    **_: Any,
) -> Dict[str, Any]:
    destination_key = _normalize_destination(destination)
    offers = TICKETS.get(destination_key, [])
    enriched_offers = []

    for offer in offers:
        subtotal = offer["adult_price_vnd"] * adults + offer["child_price_vnd"] * children
        enriched = dict(offer)
        enriched["adults"] = adults
        enriched["children"] = children
        enriched["estimated_subtotal_vnd"] = subtotal
        enriched_offers.append(enriched)

    return {
        "status": "success" if enriched_offers else "no_data",
        "destination": destination_key,
        "date": date,
        "offers": enriched_offers,
    }


def itinerary_planner(
    destination: str = "phu_quoc",
    days: int = 3,
    nights: int = 2,
    adults: int = 2,
    children: int = 0,
    budget_vnd: Optional[int] = None,
    preferences: Optional[List[str]] = None,
    **_: Any,
) -> Dict[str, Any]:
    destination_key = _normalize_destination(destination)
    preferences = preferences or ["relax", "family activities"]

    if destination_key == "nha_trang":
        itinerary = [
            {"day": 1, "time": "14:00-18:00", "activity": "Check-in and beach time"},
            {"day": 2, "time": "09:00-17:00", "activity": "VinWonders Nha Trang"},
            {"day": 3, "time": "09:00-11:00", "activity": "Resort breakfast and checkout"},
        ]
    elif any(pref in preferences for pref in ["beach", "bien", "du lich bien"]):
        itinerary = [
            {"day": 1, "time": "14:00-18:00", "activity": "Check-in at Bai Dai, sunset beach walk"},
            {"day": 2, "time": "08:30-16:30", "activity": "Island beach route: Hon Mong Tay, Hon Gam Ghi, snorkeling stop"},
            {"day": 3, "time": "08:30-12:00", "activity": "Relax at resort beach or visit Starfish Beach before checkout"},
        ]
    else:
        itinerary = [
            {"day": 1, "time": "14:00-18:00", "activity": "Check-in at Bai Dai, light Grand World walk"},
            {"day": 2, "time": "09:00-16:30", "activity": "VinWonders Phu Quoc for rides and family zones"},
            {"day": 3, "time": "09:00-12:00", "activity": "Vinpearl Safari or relaxed resort morning"},
        ]

    hotel_budget = nights * 2500000
    tickets = ticket_offer_lookup(destination_key, adults=adults, children=children)["offers"]
    ticket_budget = sum(item["estimated_subtotal_vnd"] for item in tickets[:1])
    estimated_cost = hotel_budget + ticket_budget

    return {
        "status": "success",
        "destination": destination_key,
        "days": days,
        "nights": nights,
        "group": {"adults": adults, "children": children},
        "preferences": preferences,
        "itinerary": itinerary[:days],
        "estimated_cost_vnd": estimated_cost,
        "budget_vnd": budget_vnd,
        "warnings": [
            "This is a lab itinerary based on mock tool data; verify live room and ticket prices before booking."
        ],
        "sources": [
            "https://vinpearl.com/",
            "https://vinwonders.com/vi/tickets/",
        ],
    }


def get_travel_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "hotel_lookup",
            "description": "Find Vinpearl hotels/resorts by destination, group type, budget, and nights.",
            "args_schema": '{"destination": "phu_quoc|nha_trang", "group_type": "family|budget", "budget_vnd": 15000000, "nights": 2}',
            "func": hotel_lookup,
        },
        {
            "name": "ticket_offer_lookup",
            "description": "Estimate VinWonders/Safari ticket costs for adults and children.",
            "args_schema": '{"destination": "phu_quoc|nha_trang", "adults": 2, "children": 2, "date": "2026-07-15"}',
            "func": ticket_offer_lookup,
        },
        {
            "name": "itinerary_planner",
            "description": "Create a short day-by-day itinerary using available mock travel data.",
            "args_schema": '{"destination": "phu_quoc|nha_trang", "days": 3, "nights": 2, "adults": 2, "children": 2, "budget_vnd": 15000000, "preferences": ["family"]}',
            "func": itinerary_planner,
        },
    ]


def _normalize_destination(destination: str) -> str:
    value = (destination or "phu_quoc").lower().strip()
    if value in {"phu quoc", "phú quốc", "phu-quoc"}:
        return "phu_quoc"
    if value in {"nha trang", "nha-trang"}:
        return "nha_trang"
    return value
