# DEFENSE

def weak_planet_under_threat(state):
    for planet in state.my_planets():
        incoming_enemy_ships = sum(f.num_ships for f in state.enemy_fleets() if f.destination_planet == planet.ID)
        if incoming_enemy_ships >= planet.num_ships:
            return True
    return False

def enemy_has_more_strong_planets(state, margin=1):
    STRONG_GROWTH = 3

    my_strong = sum(
        1 for p in state.my_planets()
        if p.growth_rate >= STRONG_GROWTH
    )

    enemy_strong = sum(
        1 for p in state.enemy_planets()
        if p.growth_rate >= STRONG_GROWTH
    )

    return enemy_strong >= my_strong + margin

def enemy_growth_advantage(state, factor=1.3):
    my_growth = sum(p.growth_rate for p in state.my_planets())
    enemy_growth = sum(p.growth_rate for p in state.enemy_planets())

    if my_growth == 0:
        return True
    
    return enemy_growth >= my_growth * factor

def should_turtle(state):
    return (
        weak_planet_under_threat(state)
        or enemy_growth_advantage(state, factor=1.25)
    )


# EARLY

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


# OFFENSIVE 

def have_largest_fleet(state):
    my_total = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    return my_total > enemy_total

# def have_largest_fleet(state):
#     return sum(planet.num_ships for planet in state.my_planets()) \
#              + sum(fleet.num_ships for fleet in state.my_fleets()) \
#            > sum(planet.num_ships for planet in state.enemy_planets()) \
#              + sum(fleet.num_ships for fleet in state.enemy_fleets())