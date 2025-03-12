from src.utils.nlu_unit import task_classification, name_entity_recognition

def task_identification_task_manipulation(user, user_input):
    if user.workflow_task_input_is_None():
        user.set_workflow_task_input(user_input)
    if user.get_subfsm_state() == "task identification":
        current_task_name = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
        user.set_workflow_current_task(current_task_name)
        if user.get_location() == None:
            if current_task_name == "locate destination" or current_task_name == "get directions" or current_task_name == "share location" or current_task_name == "save location":
                user.set_location(name_entity_recognition(user_input))
    elif user.get_subfsm_state() == "incorrect task identification":
        user.remove_task_from_workflow_current_all_task_options(user.get_workflow_current_task())
        current_task_name = task_classification(user.get_workflow_task_input(), user.get_current_all_task_options())
        user.set_workflow_current_task(current_task_name)
        current_task_name = user.get_workflow_current_task()
        if user.get_location() == None:
            if current_task_name == "locate destination" or current_task_name == "get directions" or current_task_name == "share location" or current_task_name == "save location":
                user.set_location(name_entity_recognition(user_input))
    return current_task_name