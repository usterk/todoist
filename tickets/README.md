# Markdown-based Ticket Management System

A ticket management system that utilizes directory structure and Markdown files (.md) as the primary data storage format. The system is designed to work with GitHub Copilot, allowing it to automatically track and update task status.

## Directory Structure

```
tickets/
├── backlog/        # Tasks waiting to be implemented
├── in_progress/    # Tasks currently in progress
└── done/           # Completed tasks
```

## Ticket File Format

Each ticket is represented as a single Markdown file with a defined structure:

```markdown
# [Task Title]

## Metadata
* **Ticket ID:** [TICKET-XXX]
* **Status:** [backlog|in_progress|done]
* **Priority:** [low|medium|high|critical]
* **Assigned to:** [user|copilot]
* **Created on:** [YYYY-MM-DD]
* **Changed on:** [YYYY-MM-DD]

## Description
Detailed description of the task to be completed...

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Task 1
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2
  - [ ] Subtask 2.1
- [ ] Write tests
- [ ] Update documentation
- [ ] Update project changelog

## Changelog
```

## Workflow

### 1. Creating a new task

1. Create a new Markdown file in the `tickets/backlog/` directory
2. Fill in the template with the appropriate information
3. Default status: `backlog`
4. Default assignment: `copilot`
5. Ensure every task includes required final subtasks: writing tests, updating documentation, and updating changelog

### 2. Starting work on a task

1. Move the file from the `backlog/` directory to `in_progress/`
2. Update the `Status` field to `in_progress`
3. Change the `Assigned to` field to `user`
4. User must fill in the `Implementation Details` section
5. Add an entry in the `Changelog` section with information about starting work:
   ```
   ### [YYYY-MM-DD HH:MM] - Work started
   Task assigned to user. Implementation details added.
   ```

### 3. Tracking progress

1. After each significant change, add a new entry in the `Changelog` section:
   ```
   ### [YYYY-MM-DD HH:MM] - [Update title]
   [Description of changes made, progress, or encountered issues]
   ```
2. Update the task list (mark completed items with `[x]`)

### 4. Reassigning to Copilot

1. When ready for Copilot to continue work, change the `Assigned to` field to `copilot`
2. Add an entry in the `Changelog` section:
   ```
   ### [YYYY-MM-DD HH:MM] - Reassigned to Copilot
   Task reassigned to Copilot for implementation.
   ```
3. Copilot can now work on the task based on the provided implementation details

### 5. Completing a task

1. Add a final entry in the `Changelog` section summarizing the work done
2. Change the status in the file to `done`
3. Move the file to the `done/` directory

## Interaction with GitHub Copilot

GitHub Copilot can automatically:

1. Read task files from the `backlog/` directory and begin initial analysis
2. Work on tasks only when they are explicitly assigned to `copilot`
3. Update task statuses and add entries to the `Changelog` section
4. Track progress and update the subtask list
5. After completing the work, move files to the `done/` directory

## Example Scenario

1. User creates a new file `tickets/backlog/ticket_123.md` (initially assigned to `copilot`)
2. When ready to start work:
   - File is moved to `tickets/in_progress/ticket_123.md`
   - Status is changed to `in_progress`
   - Assignment is changed to `user`
   - User adds implementation details
3. When implementation details are ready:
   - User changes assignment back to `copilot`
   - Copilot starts working on the task
   - Copilot updates the file by adding new entries to the Changelog
4. After completing the work:
   - Copilot adds a final entry to the Changelog
   - Changes the status to `done`
   - Moves the file to `tickets/done/ticket_123.md`

## System Advantages

1. **Simplicity** - uses only the file system and Markdown text files
2. **Transparency** - clear structure and tracking changes over time
3. **Git Integration** - easy tracking of change history
4. **Compatibility with Markdown tools** - easy visualization
5. **Independence from external systems** - works locally without additional dependencies

## Extensions

The system can be extended with:

1. **Tags and categories** - additional metadata for better task organization
2. **Advanced filters** - scripts for searching tasks based on criteria
3. **Automatic reporting** - generating progress summaries
4. **GitHub Issues integration** - synchronization with external ticket system

This system provides a simple but effective way of managing tasks in a format that is easily accessible for GitHub Copilot to analyze and modify.