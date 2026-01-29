import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    #Offense will find the strongest ally nearest to the weakest enemy
    #and send the current number of ships the enemy has + 1 to take it over
    #this obviously won't capture the enemy as the enemy will be growing
    #ships while the fleets are sent out, but it will be weakened so the next
    #time fleets are sent out, it will capture the planet
    #also makes sure to prevent our planets from sending out a dangerous
    #amount of fleets to capture an enemy

    my_planets = state.my_planets()
    their_planets = state.enemy_planets()
    strongest_ally = max(my_planets, key=lambda p: p.num_ships, default=None)
    #weakest_enemy = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    MAX_DISTANCE = 15
    close_weakest = [
        p for p in their_planets
        if state.distance(strongest_ally.ID, p.ID) <= MAX_DISTANCE
    ]   
    
    if not close_weakest:
        close_weakest = their_planets

    for i in close_weakest:
        distance = state.distance(strongest_ally.ID, i.ID)
        future_ships = i.num_ships + i.growth_rate * distance
        ships_needed = future_ships + 1
        issue_order(state, strongest_ally.ID, i.ID, ships_needed)

    return True


def spread_to_weakest_neutral_planet(state):

    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    #when this returns then we go on offense
    if not my_planets or not neutral_planets:
        return False

    # 1. Identify the strongest planet
    strongest = max(my_planets, key=lambda p: p.num_ships)
    
    # 2. Local budget (keep 5 ships for defense)
    #note: a dynamic num of min ships takes too much time
    
    available_budget = strongest.num_ships - 5
    
    MAX_DISTANCE = 15

    close_neutrals = [
        p for p in neutral_planets
        if state.distance(strongest.ID, p.ID) <= MAX_DISTANCE
    ]

    if not close_neutrals:
        close_neutrals = neutral_planets
    # 3. Sort by Value: (Growth) / (Cost + Distance)
    # This prioritizes high growth and low cost, but penalizes far-away planets.
    best_value_neutrals = sorted(
        close_neutrals, 
        key=lambda p: p.growth_rate / (p.num_ships + state.distance(strongest.ID, p.ID) + 1), 
        reverse=True
    )
    #from my planet to 
    issued_any_order = False

    for target in best_value_neutrals:
        # Don't double-target a planet already being captured
        if any(f.destination_planet == target.ID for f in state.my_fleets()):
            continue
        distance = state.distance(strongest.ID, target.ID)
        future_ships = target.num_ships + target.growth_rate * distance
        ships_needed = future_ships + 1
        ships_needed = target.num_ships + 1
        
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
    #find threatened planets through seeing if enemy ships are coming to a planet
    #and the planet has less ships than the ships the enemy is sending
    threatened = []
    for p in state.my_planets():
        incoming = sum(
            f.num_ships
            for f in state.enemy_fleets()
            if f.destination_planet == p.ID
        )
        if incoming > p.num_ships:
            threatened.append((p, incoming))
    
    if not threatened:
        return False
    
    #which ally planet is most threatened and how many incoming ships are there?
    most_threatened, incoming = max(
        threatened, 
        key=lambda x: (x[0].growth_rate, x[1] - x[0].num_ships))

    needed = incoming - most_threatened.num_ships + 1

    
    MAX_DISTANCE = 15

    #strongest and closest ally planets to send troops from
    candidates = [
        p for p in state.my_planets()
        if p.ID != most_threatened.ID
        and state.distance(p.ID, most_threatened.ID) <= MAX_DISTANCE
        and p.num_ships > needed
    ]

    if not candidates:
        return False
    
    #find which planet to send troops from

    helper = max(candidates, key= lambda p: (p.num_ships, -state.distance(p.ID, most_threatened.ID)))
    
    issue_order(state, helper.ID, most_threatened.ID, needed)
    return True


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