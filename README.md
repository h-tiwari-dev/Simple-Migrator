# Simple Migrator

A simple tool written in python to run simple migrations.

# Basic Usage

### 0. Installation
> On Macos Install
```bash
brew install --cask mysql-connector-python
```
```bash
pip install simple_migrator
```

### 1. Setup
```bash
simple_migrator setup {DATABASE_URL}
```
> Result:-
```bash
File_path migrations/.config
Checking if migration table exists
Migration table not exists
Creating Table __migrations_table__
```

### 2. Create 
```bash
simple_migrator create {MIGRATION_NAME} 
```
> Result:-
```bash
Migration 1704095392331687000_migration_uoi.sql created at migrations/1704095392331687000_migration_uoi.sql
```
### 3. Apply 
i. There are two ways to apply the migration. One way is to apply all the latest pending migrations.
```bash
simple_migrator up  
```
> Result:-
```bash
Going to run the following migrations:
 1704096783004737000_migration_3.sql
Migraiton 1704096783004737000_migration_3.sql: COMPLETED
The following migration runned Successfully: ['1704096783004737000_migration_3.sql']
```
ii. Another way to do this is to give the files name to the up command. 
> Note that this method will rerun the given migrations file.
```bash
simple_migrator up --f 1703509439.048595_temp
```
> Result:-
```bash
Going to run the following migrations:
 1704097419937590000_migration_0.sql
Migraiton 1704097419937590000_migration_0.sql: COMPLETED
The following migration runned Successfully: ['1704097419937590000_migration_0.sql']
```

### 3. Rollback 
i. Similar to "up" migration there are two ways to do this 
```bash
simple_migrator down 
```
> Result:-
```bash
Going to run the following migrations:
 ['1704097461646876000_migration_1.sql']
Rollback Migraiton 1704097461646876000_migration_1.sql completed
All migration rollback successfully.
```
ii. Another way to do this is to give the files name to the up command. 
> Note that this method will rollback every migration no matter if they were applied or not.
```bash
simple_migrator down --files 1703509439.048595_temp
```
> Result:-
```sql
Going to run the following migrations:
 ['1704097419937590000_migration_0.sql']
Rollback Migraiton 1704097419937590000_migration_0.sql completed
All migration rollback successfully.
```
### 4. List
#### i.  List All
This will list all the migrations present.
```bash
simple_migrator list all
```
> Result:-

| Name                                   | Status                  | Applied At                   |
| -------------------------------------- | ----------------------- | ---------------------------- |
| 1704097419937590000_migration_0.sql    | MigrationStatus.PENDING | 2024-01-01 14:03:14.225402   |
| 1704097461646876000_migration_1.sql    | MigrationStatus.APPLIED | 2024-01-01 14:00:21.011784   |

#### ii. List All Applied
This will list all the migrations present.
```bash
simple_migrator list applied 
```

| Name                                   | Status                  | Applied At                   |
| -------------------------------------- | ----------------------- | ---------------------------- |
| 1704097461646876000_migration_1.sql    | MigrationStatus.APPLIED | 2024-01-01 14:00:21.011784   |

#### iii. List All Applied
This will list the last applied migrations. 
```bash
simple_migrator list last-applied 
```

| Name                                   | Status                  | Applied At                   |
| -------------------------------------- | ----------------------- | ---------------------------- |
| 1704097461646876000_migration_1.sql    | MigrationStatus.APPLIED | 2024-01-01 14:00:21.011784   |

#### iv. List Pending 
This will list the all the pending migrations. 
```bash
simple_migrator list pending 
```

| Name                                   | Status                  | Applied At                   |
| -------------------------------------- | ----------------------- | ---------------------------- |
| 1704097419937590000_migration_0.sql    | MigrationStatus.PENDING | 2024-01-01 14:03:14.225402   |

### 5. Update 
This command is used when you want to update the migration status of certain migrations. You can set different migrations status with --files file_name_1 --files file_name_2 and --status can be set to pending|applied|failed
> Result:-
```bash
Going to update the following migrations:['1704097461646876000_migration_1.sql'] to status pending
Migrations:['1704097461646876000_migration_1.sql'] updated to status pending
```
### 6. Scync 
When the database and the migration files are not in scynced. Use this command to scync it.
```sql
poetry run python simple_migrator/migrator.py scync --status applied
```
> Result:-
```bash
1704097461646876000_migration_1.sql
Scyncing completed
```

---

# Visit:
1. [Github](https://github.com/h-tiwari-dev/Simple-Migrator)
2. [PyPi](https://pypi.org/project/simple_migrator/)
3. [Website](https://h-tiwari-dev.github.io/Simple-Migrator/)


# TDOD:
* [x] Make it so that the project does not reset when the setup is called twice.(There must be a better way).
* [x] Add tests to ensure that it works.
* [x] Add tests with other databases to ensure that it works.
* [x] Add a decorator so that we can check if setup is correctly done and exists gracefully.
* [ ] Make sql errors more visible.
* [ ] Exist gracefully when database name is suppied properly.
