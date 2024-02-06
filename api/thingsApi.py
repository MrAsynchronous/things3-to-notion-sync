from datetime import date
import things

def getAllThingsTasks():
    tasks = {}

    # iterate through all tasks
    for task in things.tasks():

        # get the checklist items for the task
        for item in things.checklist_items(task['uuid']):
            tasks[item['uuid']] = item

        tasks[task["uuid"]] = task

    for task in things.logbook():
        tasks[task["uuid"]] = task

    return tasks;

def getTaskChecklist(task):
    return things.checklist_items(task['uuid'])

def getAllChecklistUuids():
    items = {}

    for task in things.tasks():
        taskUuid = task.get('uuid')
        checkList = []

        for item in things.checklist_items(taskUuid):
            checkList.append(item.get('uuid'))

        if (len(checkList) > 0):
            items[taskUuid] = checkList

    return items