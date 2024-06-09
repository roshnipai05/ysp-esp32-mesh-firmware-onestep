# *Mesh*-quarading Surveillance in the Information Age

Welcome to the workshop offered by the Makerspace! You are going to spend the next 4 days trying to build and break down secure communication channels on a mesh network in your classroom. This guide will help you get started with the codebase setup, and navigate through the tasks for the workshop. Please follow these instructions carefully.

Watch this space for hints and instructions over the next 4 days...

## First Time Setup

If this is your first time at the workshop or if you're setting up the project for the first time, please follow these steps:

### Step 1: Clone the Repository
If you are familiar with Git, clone the repository. If not, download the zip file from the repository URL, and extract it on your machine.

<img src="./assets/repo-zip.png" alt="Step-wise instructions through a screenshot of the download zip button for this repository" width="70%"/>

### Step 2: Navigate to the Project
Open a terminal window. Here's how you can navigate to the project directory:
- **On macOS:**
  ```
  cd path/to/ysp-esp32-mesh-firmware/python-interface/src
  ```
- **On Windows:**
  ```
  cd path\to\ysp-esp32-mesh-firmware\python-interface\src
  ```
You can open this folder in VS-Code or any other IDE of your choice. But make sure you use a terminal to follow the rest of the instructions.

### Step 3: Create and Activate a Virtual Environment
- **On macOS:**
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **On Windows:**
  ```
  python -m venv .venv
  .venv\Scripts\activate
  ```
  Once the virtual environment is activated, install the required packages:
  ```
  pip install -r requirements.txt
  ```

After setting up, proceed to the section below to start working on your project tasks.

## Returning to the Workshop (Day 2 and Beyond)

If you're returning to continue the workshop, follow these steps to get set up:

1. **Navigate to the Project:**
   ```
   cd path/to/ysp-esp32-mesh-firmware/python-interface/src  (adjust path as needed for macOS or Windows)
   ```
2. **Activate the Virtual Environment:**
   - **On macOS:**
     ```
     source .venv/bin/activate
     ```
   - **On Windows:**
     ```
     .venv\Scripts\activate
     ```
3. **Start the Main Controller:**
   - This acts like your development board's screen where you can monitor outputs.
   ```
   python lib/main_controller.py
   ```
4. **Open a New Terminal Window:**
   - **On macOS:** Press `Cmd+T` to open a new terminal tab.
   - **On Windows:** You might need to open a new terminal window from your start menu or taskbar.
5. **Start the Command Interface:**
   - This is where you'll type commands to interact with your development board.
   ```
   python lib/command_interface.py
   ```

   When you see the prompt:
   ```
   Enter a command
   >
   ```
   Type `help` to see all available commands and their formats.

## Working on Your Tasks

All your tasks as part of the Blue and Red teams will be in the file `src/workspace.py`. Make sure to read the comments and follow the instructions within that file carefully.

**Troubleshooting:** If your codebase starts breaking, we'll help you make a local backup of the `workspace.py` file, then you can delete the entire project and set it up again from scratch using the instructions above.

We're excited to see what you'll create and discover during this workshop! If you encounter any issues, don't hesitate to ask for help.

