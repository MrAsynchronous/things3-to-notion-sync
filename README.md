# Things3 to Notion Sync

## Thesis
* I love Things
* I love Notion
* I want interop between them

## Features
* Using Things as a source of truth, tasks are synced into a notion Database. All data is preserved.
* Smart sync:
    * Tasks that exist in Things and not in Notion are created
    * Tasks that exist in both, with a newer `modified` property in Things are marked as "stale" and updated
    * Tasks that exist in Notion but not in Things are archived

## Setup
1) Ensure .env has `NOTION_TOKEN` and `NOTION_DATABASE_ID`
2) Ensure path to Things3 database is correct in `main.py`
3) Run `main.py`


## Usage
1) Run the `build.sh` script
2) Run each command in the `install.sh` in `sudo`