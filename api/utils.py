def compareTaskContent(taskA, taskB):
    print(f"Comparing {taskA.get('title')} and {taskB.get('title')}")

    if taskA.get('title') != taskB.get('title'):
        return False, 'title'
    elif taskA.get('notes') != taskB.get('notes'):
        return False, 'notes'
    elif taskA.get('start_date') != taskB.get('start_date'):
        return False, 'start_date'
    elif taskA.get('area') != taskB.get('area'):
        return False, 'area'
    elif taskA.get('project') != taskB.get('project'):
        return False, 'project'
    elif taskA.get('start') != taskB.get('start'):
        return False, 'start'
    elif taskA.get('tags') != taskB.get('tags'):
        return False, 'tags'

    return True