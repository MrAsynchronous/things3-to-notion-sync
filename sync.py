from api.notionApi import getAllNotionTasks, createPagesFromThingsTasks, updatePagesFromThingsTasks, deletePagesFromThingsTasks, updateChecklistRelationForTask;
from api.thingsApi import getAllThingsTasks, getAllChecklistUuids;
from api.utils import compareTaskContent;

WRITE = True

async def sync():
    print("Syncing Things3 tasks to Notion!")

    # fetch tasks from Notion
    notion_tasks = await getAllNotionTasks(False);
    print(f"\tFound {len(notion_tasks)} tasks in Notion")

    things_tasks = getAllThingsTasks();    
    print(f"\tFound {len(things_tasks)} tasks in Things3")

    stale_tasks = []
    tasks_to_create = []
    tasks_to_delete = []

    # maps task uuid to checklists
    checklists = getAllChecklistUuids();
    uuid_page_id_map = {}

    # compare tasks from things to notion
    for uuid, task in things_tasks.items():
        notion_task = notion_tasks.get(uuid)

        # # if the task is not in notion, add it to the list of tasks to create
        if (not notion_task):
            tasks_to_create.append(task);
        elif (notion_task.get("modified") != task.get("modified")):
        # insert the page_id
            task["page_id"] = notion_task.get("page_id")

            stale_tasks.append(task);

    # find tasks that are in notion but not in things
    for uuid, task in notion_tasks.items():
        things_task = things_tasks.get(uuid)

        # extract the page id
        uuid_page_id_map[uuid] = task.get("page_id")

        if not things_task:
            tasks_to_delete.append(task);
    
    print(f"Found {len(stale_tasks)} tasks to update in Notion")
    print(f"Found {len(tasks_to_create)} tasks in Things3 that are not in Notion")
    print(f"Found {len(tasks_to_delete)} tasks in Notion that are not in Things3\n")

    edit_delta = len(stale_tasks) + len(tasks_to_create) + len(tasks_to_delete)

    # write only if we can
    if WRITE:
        # write the new tasks
        if (len(tasks_to_create) > 0):
            print(f"\tCreating {len(tasks_to_create)} new tasks in Notion")

            resultPageIds = await createPagesFromThingsTasks(tasks_to_create);
            
            # update the uuid_page_id_map
            for uuid, pageId in resultPageIds.items():
                uuid_page_id_map[uuid] = pageId

        # update the tasks
        if (len(stale_tasks) > 0):
            print(f"\tUpdating {len(stale_tasks)} tasks in Notion")

            await updatePagesFromThingsTasks(stale_tasks);
        
        # delete the tasks
        if (len(tasks_to_delete) > 0):
            print(f"\tDeleting {len(tasks_to_delete)} tasks in Notion")
                
            await deletePagesFromThingsTasks(tasks_to_delete);
        
        # sync subtasks
        for taskUuid, checklistUuids in checklists.items():
            taskPageId = uuid_page_id_map.get(taskUuid)
            checklistPageIds = []

            for checklistUuid in checklistUuids:
                checklistPageId = uuid_page_id_map.get(checklistUuid)
                checklistPageIds.append(checklistPageId)

            await updateChecklistRelationForTask(taskPageId, checklistPageIds)                    

        if edit_delta == 0:
            print("\tNo changes detected, skipping sync")
        else:
            print("Sync complete!")
    else:
        print("\tWrite is disabled, skipping write")

    return;