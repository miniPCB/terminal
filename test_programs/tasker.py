# Nolan Manteufel
# Tasker

import json
import os
from datetime import datetime

# Define the path for both task and tasker JSON files
tasker_json_file = 'tasker.json'
tasks_json_file = 'tasks.json'

# Template structure for tasker.json
tasker_template = {
    "assignees": [],
    "unique_titles": [],
    "completion_counts": {},
    "duration_counters": {}
}

# Task structure
tasks_template = []

def load_json_data(file, template):
    """Load JSON data or create it if not present."""
    if not os.path.exists(file):
        return template
    with open(file, 'r') as f:
        return json.load(f)

def save_json_data(file, data):
    """Save data to JSON file."""
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def load_tasker_data():
    """Load tasker.json data."""
    return load_json_data(tasker_json_file, tasker_template)

def load_tasks_data():
    """Load tasks.json data."""
    return load_json_data(tasks_json_file, tasks_template)

def save_tasker_data(data):
    """Save data to tasker.json."""
    save_json_data(tasker_json_file, data)

def save_tasks_data(data):
    """Save tasks data to tasks.json."""
    save_json_data(tasks_json_file, data)

def add_assignee(assignee):
    """Add a new assignee to tasker.json if they don't exist."""
    data = load_tasker_data()
    
    if assignee not in data['assignees']:
        data['assignees'].append(assignee)
        data['completion_counts'][assignee] = {}
        print(f"Added new assignee: {assignee}")
    
    save_tasker_data(data)

def add_unique_title(title):
    """Add a unique title to tasker.json if it doesn't exist."""
    data = load_tasker_data()
    
    if title not in data['unique_titles']:
        data['unique_titles'].append(title)
        data['duration_counters'][title] = {}
        print(f"Added new task title: {title}")
    
    save_tasker_data(data)

def update_completion_count(assignee, title):
    """Update the completion count for an assignee and task title."""
    data = load_tasker_data()
    
    if assignee not in data['completion_counts']:
        add_assignee(assignee)
    
    if title not in data['completion_counts'][assignee]:
        data['completion_counts'][assignee][title] = 0
    
    data['completion_counts'][assignee][title] += 1
    print(f"Updated completion count: {assignee} completed '{title}' {data['completion_counts'][assignee][title]} times")
    
    save_tasker_data(data)

def add_duration(assignee, title, duration):
    """Add a task duration for a specific assignee and task title."""
    data = load_tasker_data()

    if title not in data['duration_counters']:
        add_unique_title(title)

    if assignee not in data['duration_counters'][title]:
        data['duration_counters'][title][assignee] = []
    
    data['duration_counters'][title][assignee].append(duration)
    print(f"Added duration of {duration} hours for {assignee} on '{title}'")
    
    save_tasker_data(data)

def add_task():
    """Add a new task to tasks.json."""
    tasks = load_tasks_data()
    
    task_id = len(tasks) + 1
    title = input("Enter task title: ").strip()
    description = input("Enter task description: ").strip()
    originator = input("Enter originator name: ").strip()
    assignees = input("Enter assignees (comma-separated): ").strip().split(",")
    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    task = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "originator": originator,
        "assignees": [assignee.strip() for assignee in assignees],
        "created_date": created_date,
        "completed_date": ""
    }
    
    tasks.append(task)
    save_tasks_data(tasks)
    
    # Ensure the title and assignees are tracked in tasker.json
    for assignee in task["assignees"]:
        add_assignee(assignee)
    add_unique_title(title)
    
    print("\nTask added successfully!")

def display_task(task):
    """Display a single task."""
    print(f"\nTask ID: {task['task_id']}")
    print(f"Title: {task['title']}")
    print(f"Description: {task['description']}")
    print(f"Originator: {task['originator']}")
    print(f"Assignees: {', '.join(task['assignees'])}")
    print(f"Created Date: {task['created_date']}")
    print(f"Completed Date: {task['completed_date']}")
    print()

def view_tasks():
    """View all tasks stored in tasks.json."""
    tasks = load_tasks_data()
    
    if not tasks:
        print("\nNo tasks available.")
        return
    
    for task in tasks:
        display_task(task)

def edit_task():
    """Edit an existing task."""
    tasks = load_tasks_data()

    task_id = int(input("Enter task ID to edit: "))
    task = next((t for t in tasks if t['task_id'] == task_id), None)

    if not task:
        print("\nTask not found.")
        return

    print("\nEditing Task:")
    display_task(task)

    print("Which field would you like to edit?")
    print("[1] Title")
    print("[2] Description")
    print("[3] Originator")
    print("[4] Assignees")
    print("[X] Cancel editing")
    choice = input("Enter your choice: ").strip().lower()

    if choice == '1':
        task['title'] = input("Enter new title: ").strip()
    elif choice == '2':
        task['description'] = input("Enter new description: ").strip()
    elif choice == '3':
        task['originator'] = input("Enter new originator: ").strip()
    elif choice == '4':
        task['assignees'] = input("Enter new assignees (comma-separated): ").strip().split(",")
    elif choice == 'x':
        print("Editing canceled.")
        return
    else:
        print("Invalid choice.")
        return

    # Save updated task
    save_tasks_data(tasks)
    print("\nTask updated successfully!")

def mark_task_complete():
    """Mark a task as completed and update tasker.json."""
    tasks = load_tasks_data()
    
    task_id = int(input("Enter task ID to mark as completed: "))
    task = next((t for t in tasks if t['task_id'] == task_id), None)
    
    if not task:
        print("\nTask not found.")
        return
    
    # Mark the task as completed
    task['completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_tasks_data(tasks)
    
    # Update completion count and duration
    duration = float(input(f"How many hours did it take to complete '{task['title']}'? ").strip())
    for assignee in task['assignees']:
        update_completion_count(assignee, task['title'])
        add_duration(assignee, task['title'], duration)
    
    print("\nTask marked as completed!")

def display_tasker_data():
    """Display the content of tasker.json in a readable format."""
    data = load_tasker_data()

    print("\n=== Tasker Data ===\n")

    # Display assignees
    print("Assignees:")
    if data['assignees']:
        for assignee in data['assignees']:
            print(f" - {assignee}")
    else:
        print(" No assignees found.")

    # Display unique titles
    print("\nUnique Task Titles:")
    if data['unique_titles']:
        for title in data['unique_titles']:
            print(f" - {title}")
    else:
        print(" No task titles found.")

    # Display completion counts
    print("\nCompletion Counts:")
    if data['completion_counts']:
        for assignee, tasks in data['completion_counts'].items():
            print(f"\nAssignee: {assignee}")
            for task, count in tasks.items():
                print(f"   {task}: {count} times")
    else:
        print(" No completion data available.")

    # Display duration counters
    print("\nTask Duration (in hours):")
    if data['duration_counters']:
        for title, assignees in data['duration_counters'].items():
            print(f"\nTask: {title}")
            for assignee, durations in assignees.items():
                duration_str = ', '.join(f"{d:.1f}" for d in durations)
                print(f"   {assignee}: {duration_str} hours")
    else:
        print(" No duration data available.")
    
    print("\n===================\n")

def main_menu():
    """Main menu for managing tasks and tasker.json."""
    while True:
        print("\nTasker Automation Menu:")
        print("[1] View tasker data")
        print("[2] View tasks")
        print("[3] Add task")
        print("[4] Edit task")
        print("[5] Mark task as completed")
        print("[6] Add assignee")
        print("[7] Add unique task title")
        print("[8] Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            display_tasker_data()
        elif choice == '2':
            view_tasks()
        elif choice == '3':
            add_task()
        elif choice == '4':
            edit_task()
        elif choice == '5':
            mark_task_complete()
        elif choice == '6':
            assignee = input("Enter assignee name: ").strip()
            add_assignee(assignee)
        elif choice == '7':
            title = input("Enter task title: ").strip()
            add_unique_title(title)
        elif choice == '8':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
