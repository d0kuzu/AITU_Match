from aiogram.fsm.state import State, StatesGroup


class QuestionState(StatesGroup):
    wait_answer = State()
    wait_answer_extra_survey = State()
    wait_answer_held_out_comment = State()

class AdviceState(StatesGroup):
    wait_question = State()

class TestState(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    q9 = State()

class RegisterState(StatesGroup):
    wait_age = State()
    wait_name = State()
    wait_addiction = State()
    wait_addiction_other = State()
    wait_experience = State()
    wait_last_use = State()
    wait_motivation = State()

class GoalState(StatesGroup):
    wait_area_selection = State()
    wait_goal_input = State()
    wait_goal_details = State()
    wait_plan_confirmation = State()

class SurveyState(StatesGroup):
    wait_user_info = State()
    wait_features = State()
    wait_bad_features = State()
    wait_new_features = State()
    wait_cost = State()
    wait_contacts = State()

class RestartState(StatesGroup):
    wait_reason = State()
    wait_confirmation = State()

class SettingsState(StatesGroup):
    wait_affirmation_time = State()
    wait_confirm_time = State()
