import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):

    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    if not my_planets or not neutral_planets:
        return False

    # 1. Identify the strongest planet
    strongest = max(my_planets, key=lambda p: p.num_ships)
    
    # 2. Local budget (keep 5 ships for defense)
    available_budget = strongest.num_ships - 5
    
    # 3. Sort by Value: (Growth) / (Cost + Distance)
    # This prioritizes high growth and low cost, but penalizes far-away planets.
    best_value_neutrals = sorted(
        neutral_planets, 
        key=lambda p: p.growth_rate / (p.num_ships + state.distance(strongest.ID, p.ID) + 1), 
        reverse=True
    )
    
    issued_any_order = False

    for target in best_value_neutrals:
        # Don't double-target a planet already being captured
        if any(f.destination_planet == target.ID for f in state.my_fleets()):
            continue
            
        ships_needed = target.num_ships + 10
        
        # 4. If we have enough in our budget, send the fleet
        if available_budget >= ships_needed:
            issue_order(state, strongest.ID, target.ID, int(ships_needed))
            
            # Update budget for the next loop iteration
            available_budget -= ships_needed
            issued_any_order = True
        else:
            # If we can't afford a high-value one, keep looking for a cheaper high-value one
            continue
            
    return issued_any_order


# DEFENSE

def reinforce_weak_planets(state):
    threatened = [
        p for p in state.my_planets()
        if sum(f.num_ships for f in state.enemy_fleets() if f.destination_planet == p.ID) > p.num_ships
    ]
    if not threatened:
        return False

    strongest = max(state.my_planets(), key=lambda p: p.num_ships)
    for planet in threatened:
        needed = sum(f.num_ships for f in state.enemy_fleets() if f.destination_planet == planet.ID) - planet.num_ships + 1
        if strongest.num_ships > needed:
            return issue_order(state, strongest.ID, planet.ID, needed)
    return False


# EARLY

# def spread_to_weakest_neutral_planet(state):
#     if not state.my_planets() or not state.neutral_planets():
#         return False

#     strongest = max(state.my_planets(), key=lambda p: p.num_ships)
#     weakest_neutral = min(state.neutral_planets(), key=lambda p: p.num_ships)

#     needed = weakest_neutral.num_ships + 1
#     if strongest.num_ships > needed:
#         return issue_order(state, strongest.ID, weakest_neutral.ID, needed)
#     return False

# OFFENSIVE

# def attack_weakest_enemy_planet(state):
#     if not state.my_planets() or not state.enemy_planets():
#         return False

#     strongest = max(state.my_planets(), key=lambda p: p.num_ships)
#     weakest_enemy = min(state.enemy_planets(), key=lambda p: p.num_ships)

#     if strongest.num_ships > weakest_enemy.num_ships + 5:
#         return issue_order(state, strongest.ID, weakest_enemy.ID, strongest.num_ships // 2)
#     return False