



VALID_CATEGORIES = {
    "Access",
    "Hardware",
    "Software",
    "Account Management",
    "Onboarding",
    "Offboarding",
    "Facilities",
    "Security",
}


# Transition Validator 
ALLOWED_TRANSITIONS = {
    "user": {
        "pending": {"cancelled"},
        "approved": {"cancelled"},
        "in_progress": {"cancelled"},  # Users can cancel in-progress requests too
    },
    "admin": {
        "pending": {"approved", "denied", "in_progress"},
        "approved": {"in_progress"},  # Keep this for backwards compatibility
        "in_progress": {"completed", "denied"},  # ✅ CHANGED THIS LINE
    }
}

def validate_transition(current_status, new_status, actor_role):
    allowed = ALLOWED_TRANSITIONS.get(actor_role, {})
    return new_status in allowed.get(current_status, set())

