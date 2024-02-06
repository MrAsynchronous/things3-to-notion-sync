from notion_client import AsyncClient
import os
import asyncio

os.environ['NOTION_TOKEN'] = 'your_token_here'
os.environ['NOTION_DATABASE_ID'] = 'database_id_here'

notion = AsyncClient(auth=os.environ['NOTION_TOKEN'])

def formatThingsTaskForNotion(task):
    # default tags
    tags = task.get('tags') or [];

    formattedTask = {
        'Uuid': {'rich_text': [{'text': {'content': task.get('uuid')}}]},
        'Name': {'title': [{'text': {'content': task.get('title')}}]},
        'Status': {'select': {'name': task.get('status').capitalize()}},
        'Modified': {'rich_text': [{'text': {'content': task.get('modified')}}]},
        'Type': {'select': {'name': task.get('type') or 'Unknown'}},
        'Tags': {'multi_select': [{'name': tag} for tag in tags]}
    }

    # handle the propss that could be empty
    start_date = task.get('start_date');
    stop_date = task.get('stop_date');
    deadline = task.get('deadline');
    
    if start_date:
        formattedTask['Dates'] = {'date': {'start': start_date, 'end': deadline or start_date}}
    elif deadline:
        formattedTask['Dates'] = {'date': {'start': deadline, 'end': deadline}}

    area = task.get('area_title');
    if area:
        formattedTask['Area'] = {'select': {'name': area}}

    project = task.get('project_title');
    if project:
        formattedTask['Project'] = {'select': {'name': project}}

    start = task.get('start')
    if start:
        formattedTask['Start'] = {'select': {'name': start}}

    notes = task.get('notes')
    if notes:
        formattedTask['Notes'] = {'rich_text': [{'text': {'content': notes}}]}

    return formattedTask

async def getAllNotionTasks(light):
    start_cursor = None
    parsed_tasks = {}

    while True:
        print(f'Fetching Notion tasks with start_cursor: {start_cursor}')

        query_result = await notion.databases.query(
            os.environ['NOTION_DATABASE_ID'],
            start_cursor=start_cursor
        )

        query_pages = query_result.get('results')

        # Assuming you're parsing tasks here
        for page in query_pages:
            properties = page.get('properties', {})
            page_id = page.get('id')

            uuidParent = properties.get('Uuid').get('rich_text', [])
            modifiedParent = properties.get('Modified').get('rich_text', [])
            typeParent = properties.get('Type').get('select', {})

            # handle corrupt rows
            if len(uuidParent) == 0 or len(modifiedParent) == 0 or len(typeParent) == 0:
                continue

            uuid = uuidParent[0].get('plain_text')
            modified = modifiedParent[0].get('plain_text')
            type = typeParent.get('name')

            # only fetch the light version of the task
            if (light):
                parsed_tasks[uuid] = {
                    'uuid': uuid,
                    'page_id': page_id,
                    'modified': modified,
                    'type': type
                }
            else:
                dateParent = properties.get('Dates', {}).get('date', {})
                areaParent = properties.get('Area', {}).get('select', {})
                projectParent = properties.get('Project', {}).get('select', {})
                startParent = properties.get('Start', {}).get('select', {})
                tagsParent = properties.get('Tags', {}).get('multi_select', [])
                notesParent = properties.get('Notes', {}).get('rich_text', [])
                titleParent = properties.get('Name', {}).get('title', [])

                parsedData = {}

                if titleParent:
                    parsedData['title'] = titleParent[0].get('plain_text')
                
                if dateParent:
                    parsedData['start_date'] = dateParent.get('start')
                    parsedData['end_date'] = dateParent.get('end')
                
                if areaParent:
                    parsedData['area'] = areaParent.get('name')
                
                if projectParent:
                    parsedData['project'] = projectParent.get('name')
                
                if startParent:
                    parsedData['start'] = startParent.get('name')
                
                if tagsParent:
                    parsedData['tags'] = [tag.get('name') for tag in tagsParent]
                
                if notesParent:
                    parsedData['notes'] = notesParent[0].get('plain_text')
                
                parsedData['uuid'] = uuid
                parsedData['page_id'] = page_id
                parsedData['modified'] = modified

                parsed_tasks[uuid] = parsedData

        start_cursor = query_result.get('next_cursor')

        if start_cursor is None:
            break

    return parsed_tasks

async def createPageFromThingsTask(thingsTask):
    try:
        formattedTask = formatThingsTaskForNotion(thingsTask);

        query_result = await notion.pages.create(
            parent = {'type': 'database_id', 'database_id': os.environ['NOTION_DATABASE_ID']},
            properties = formattedTask
        )

        return {
            'uuid': thingsTask.get('uuid'),
            'page_id': query_result.get('id')
        }
    except Exception as e:
        print(f"Error creating page: {e}")
    finally:
        print(f"Created page for {thingsTask.get('title')}")

async def createPagesFromThingsTasks(thingsTasks):
    tasks = [createPageFromThingsTask(task) for task in thingsTasks]
    response = await asyncio.gather(*tasks)

    mappedPageIds = {}

    for pageIdSubMap in response:
        mappedPageIds[pageIdSubMap.get('uuid')] = pageIdSubMap.get('page_id')

    return mappedPageIds

async def updatePageFromThingsTask(thingsTask):
    page_id = thingsTask.get('page_id')
    del thingsTask['page_id']

    try:
        formattedTask = formatThingsTaskForNotion(thingsTask);

        await notion.pages.update(
            page_id = page_id,
            properties = formattedTask
        )
    except Exception as e:
        print(f"Error updating page: {e}")
    finally:
        print(f"Updated page for {thingsTask.get('title')}")

async def updatePagesFromThingsTasks(thingsTasks):
    tasks = [updatePageFromThingsTask(task) for task in thingsTasks]
    await asyncio.gather(*tasks)

async def deletePageFromThingsTask(thingsTask):
    page_id = thingsTask.get('page_id')

    try:
        await notion.pages.update(
            page_id = page_id,
            archived = True
        )
    except Exception as e:
        print(f"Error deleting page: {e}")
    finally:
        print(f"Deleted page for {thingsTask.get('title')}")

async def deletePagesFromThingsTasks(thingsTasks):
    tasks = [deletePageFromThingsTask(task) for task in thingsTasks]
    await asyncio.gather(*tasks)

async def updateChecklistRelationForTask(taskPageId, subTaskPageIds):
    try:
        await notion.pages.update(
            page_id = taskPageId,
            properties = {
                'Checklist': {'relation': [{'id': subTaskPageId} for subTaskPageId in subTaskPageIds]}
            }
        )
    except Exception as e:
        print(f"Error updating checklist relation: {e}")
    finally:
        print(f"Updated checklist relation for {uuid}")

async def updateChecklistRelationsForTasks(checklists):
    tasks = [updateChecklistRelationForTask(uuid, checklistUuids) for uuid, checklistUuids in checklists.items()]
    await asyncio.gather(*tasks)