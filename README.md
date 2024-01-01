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
### 2. Create 
```bash
simple_migrator create {MIGRATION_NAME} 
```
### 3. Apply 
i. There are two ways to apply the migration. One way is to apply all the latest pending migrations.
```bash
simple_migrator up  
```
ii. Another way to do this is to give the files name to the up command. 
> Note that this method will rerun the given migrations file.
```bash
simple_migrator up --files 1703509439.048595_temp
```

### 3. Rollback 
i. Similar to "up" migration there are two ways to do this 
```bash
simple_migrator down 
```
ii. Another way to do this is to give the files name to the up command. 
> Note that this method will rollback every migration no matter if they were applied or not.
```bash
simple_migrator down --files 1703509439.048595_temp
```
### 4. List
i. List All
This will list all the migrations present.
```bash
simple_migrator list all
```
ii. List All Applied
This will list all the migrations present.
```bash
simple_migrator list applied 
```
iii. List All Applied
This will list the last applied migrations. 
```bash
simple_migrator list last-applied 
```
iv. List Pending 
This will list the all the pending migrations. 
```bash
simple_migrator list pending 
```
---

# Visit:
1. [Github](https://github.com/h-tiwari-dev/Simple-Migrator)
2. [PyPi](https://pypi.org/project/simple_migrator/)


# TDOD:
* [x] Make it so that the project does not reset when the setup is called twice.(There must be a better way).
* [x] Add tests to ensure that it works.
* [x] Add tests with other databases to ensure that it works.
* [x] Add a decorator so that we can check if setup is correctly done and exists gracefully.
* [ ] Make sql errors more visible.
* [ ] Exist gracefully when database name is suppied properly.
