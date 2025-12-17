from models.user_profile import UserProfile

def update_state(user_profile: UserProfile, new_state: str):
    user_profile.state = new_state

def update_preference(user_profile: UserProfile, tag: str, weight: float):
    if tag not in user_profile.preferences:
        user_profile.preferences[tag] = 0.0
    user_profile.preferences[tag] += weight
