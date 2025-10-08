from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration"""
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_description = State()
    waiting_for_course = State()
    waiting_for_program = State()
    waiting_for_photo = State()


class EditProfileStates(StatesGroup):
    """States for editing profile"""
    choosing_field = State()
    editing_course = State()
    editing_program = State()
    editing_age = State()
    editing_name = State()
    editing_description = State()
    editing_photo = State()


class VerificationStates(StatesGroup):
    """States for verification process"""
    waiting_for_student_id = State()


class EventSelectionStates(StatesGroup):
    """States for selecting events"""
    selecting_events = State()


class MatchingStates(StatesGroup):
    """States for browsing profiles"""
    browsing = State()