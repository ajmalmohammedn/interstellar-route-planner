from app.constants import (
    PERSONAL_TRANSPORT_COST_PER_AU,
    PERSONAL_TRANSPORT_PARKING_PER_DAY,
    PERSONAL_TRANSPORT_MAX_PASSENGERS,
    HSTC_TRANSPORT_COST_PER_AU,
    HSTC_TRANSPORT_MAX_PASSENGERS,
)

def cheapest_transport(distance_au: float, passengers: int, parking_days: int) -> dict:
    if distance_au < 0:
        raise ValueError("distance must be >= 0")
    if passengers < 1:
        raise ValueError("passengers must be >= 1")
    if parking_days < 0:
        raise ValueError("parking_days must be >= 0")
    if passengers > HSTC_TRANSPORT_MAX_PASSENGERS:
        raise ValueError(f"Too many passengers: max is {HSTC_TRANSPORT_MAX_PASSENGERS}")
    
    options = []

    # Personal Transport: up to 4 passengers, fuel + parking
    if passengers <= PERSONAL_TRANSPORT_MAX_PASSENGERS:
        fuel = distance_au * PERSONAL_TRANSPORT_COST_PER_AU
        parking = parking_days * PERSONAL_TRANSPORT_PARKING_PER_DAY
        total_cost = fuel + parking   
        options.append({
            "type": "Personal",
            "total_cost": total_cost,
            "fuel_cost": fuel,
            "parking_cost": parking,
        })

    # HSTC Transport: up to 5 passengers, no parking cost
    if passengers <= HSTC_TRANSPORT_MAX_PASSENGERS:
        fuel = distance_au * HSTC_TRANSPORT_COST_PER_AU
        total_cost = fuel
        options.append({
            "type": "HSTC",
            "total_cost": total_cost,
            "fuel_cost": fuel,
            "parking_cost": 0,
        })

    chosen = min(options, key=lambda x: x["total_cost"])

    return {
        "transport_type": chosen["type"],
        "total_cost_gbp": round(chosen["total_cost"], 2),
        "breakdown": {
            "fuel_cost": round(chosen["fuel_cost"], 2),
            "parking_cost": round(chosen["parking_cost"], 2),
        },
    }

        


