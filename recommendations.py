# recommendations.py
def get_support_recommendations(level):
    table = {
        "none": ["Nothing concerning"],
        "low": ["Maybe take a short break or talk to a friend"],
        "medium": [
            "Consider speaking with a support hotline like Eran 1201",
            "Take time to rest and reflect"
        ],
        "high": [
            "Immediate support recommended",
            "Contact Eran at 1201",
            "Reach out to someone you trust right now"
        ]
    }

    return table.get(level, [])
