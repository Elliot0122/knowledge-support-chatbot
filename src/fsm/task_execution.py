import secrets

def task_execution_get_instruction(user):
    if user.get_workflow_trajectory() == []:
        return 
    
    current_task = user.get_task(user.get_workflow_trajectory()[user.get_workflow_trajectory_index()])

    if user.get_subfsm_state() == "provide detail":
        current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
        current_primitive.subtract_one_from_proficiency()
        return current_primitive.get_detail()

    elif user.get_subfsm_state() == "provide other instruction":
        current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
        current_primitive.subtract_one_from_proficiency()
        current_task.remove_primitive(current_task.get_next_primitive_selection())

    elif user.get_subfsm_state() == "provide instruction" and current_task.get_next_primitive_selection():
        current_task.select_next_primitive()
        if current_task.is_done():
            user.add_one_to_workflow_trajectory_index()
            current_task = user.get_task(user.get_workflow_trajectory()[user.get_workflow_trajectory_index()])

    current_task.set_next_primitive_selection(secrets.choice(current_task.get_current_primitive_options()))
    current_primitive = user.get_primitive(current_task.get_next_primitive_selection())
    current_primitive.add_one_to_proficiency()
    if current_primitive.get_proficiency() > 3:
        return f'Now, you should {current_primitive.get_name()}.'
    else: 
        return current_primitive.get_detail()