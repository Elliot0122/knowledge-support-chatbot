import secrets
from src.utils.nlu_unit import name_entity_recognition

def check_goal_is_exhausted(user, event):
    if user.get_parent_fsm_state() == "goal clarification":
        choices = user.get_goal_setting_current_task_choices()
        if (len(choices) == 1 and event == "negate") or len(choices) == 0:
            event = "done"
    return event

def goal_clarification_task_manipulation(user, user_input):
    if user.get_subfsm_state() == "task identification":
        user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
        current_task_name = user.get_goal_setting_next_task_selection()
        if user.get_location() == None:
            if current_task_name == "share location" or current_task_name == "save location" or current_task_name == "get directions":
                user.set_location(name_entity_recognition(user_input))
    elif user.get_subfsm_state() == "correct task":
        current_task_name = user.get_goal_setting_next_task_selection()
        print(f"current_task_name: {current_task_name}")
        user.add_to_workflow_trajectory(current_task_name)
        user.select_goal_setting_next_task(current_task_name)             
    elif user.get_subfsm_state() == "incorrect task identification":
        user.remove_goal_setting_task(user.get_goal_setting_next_task_selection())
        user.set_goal_setting_next_task_selection(secrets.choice(user.get_goal_setting_current_task_choices()))
        current_task_name = user.get_goal_setting_next_task_selection()
    return current_task_name