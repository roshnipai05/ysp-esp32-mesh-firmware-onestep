# _Mesh_-quarading Surveillance in the Information Age

Welcome to the workshop offered by the Makerspace! You are going to spend the next 4 days trying to build and break down secure communication channels on a mesh network in your classroom. This guide will help you get started with the codebase setup, and navigate through the tasks for the workshop. Please follow these instructions carefully.

Watch this space for hints and instructions over the next 4 days...

## Reading List and Presentation Instructions

[This gist has a short reading list based on some of the topics we discussed in the introductory session and the Prompts for your Final Presentation](https://gist.github.com/DeeprajPandey/0f64af8549fac86fecf5dda6f979f825)

## First Time Setup

### Step 0: Install Python and Everything Everywhere All At Once
That you will need for the next 4 days.

[❗️Download this Setup Checklist PDF File for Step 0 Instructions](https://raw.githubusercontent.com/Makerspace-Ashoka/ysp-esp32-mesh-firmware/main/makerspace_checklist_final.pdf)


### Step 1: Clone the Repository

If you are familiar with Git, clone the repository. If not, download the zip file from the repository URL, and extract it on your machine.

<img src="./assets/repo-zip.png" alt="Step-wise instructions through a screenshot of the download zip button for this repository" width="70%"/>

### Step 2: Navigate to the Project

Here's how you can navigate to the project directory:

- **On macOS:**

  Go to where you have downloaded the zip file (usually `~/Downloads/`) and extract all of its contents.
  Now, open a Terminal window (`Cmd + Space` to open spotlight and type `terminal` to search for the terminal app and press Enter) and follow the instructions below.
  ```
  mv [path to]/ysp-esp32-mesh-firmware-main/
  cd ..
  mv ysp-esp32-mesh-firmware-main/ ysp-esp32-mesh-firmware/
  cd ysp-esp32-mesh-firmware/python-interface/src/
  code .
  ```
- **On Windows:**

  Go to where you have downloaded the zip file and extract all of its contents.
  Now open `Powershell` from Start Menu and follow the instructions below. It renames the directory and opens the python-interface source directory on VS Code.
  ```
  cd [path to]\ysp-esp32-mesh-firmware-main\
  cd ..
  MOVE ysp-esp32-mesh-firmware-main\ ysp-esp32-mesh-firmware\
  cd ysp-esp32-mesh-firmware\python-interface\src\
  code .
  ```
  You can open this folder in VS-Code or any other IDE of your choice. But make sure you use a terminal to follow the rest of the instructions.

### Step 3: Create a Virtual Environment

- **On macOS:**
  ```
  python3 -m venv .venv
  ```
- **On Windows:**

Run this next command ONLY once:
  ```
  Set-ExecutionPolicy Unrestricted -Scope Process
  ```
Now, create a virtual environment
  ```
  python -m venv .venv
  ```

### Step 4: Activate Virtual Environment and Install Dependencies
- **On macOS:**
  ```
  source .venv/bin/activate
  ```
- **On Windows:**
  ```
  .venv\Scripts\activate
  ```

  If the previous command succeeds, you will notice that your terminal prompt updates. It will now start with `(.venv)`.

  This means that everything you do now will be restricted to the python binary and the packages installed within this virtual environment.

  We can now install our project dependencies:
  ```
  pip install -r requirements.txt
  ```

### Step 5: Deactivate Virtual Environment

When you are done working on the project, make sure you deactivate the virtual environment. Otherwise any other python binaries you try to install elsewhere during this
terminal session will end up in this directory.

  ```
  deactivate
  ```

After setting up, proceed to the section below to start working on your project tasks.

## Returning to the Workshop (Day 2 and Beyond)

If you're returning to continue the workshop, follow these steps to get set up:

1. **Navigate to the Project:**

   Usually in `~/Downloads` on MacOS or `C:\users\[your username]\Downloads\` on Windows.
   ```
   cd [path to]/ysp-esp32-mesh-firmware/python-interface/src  (adjust path as needed for macOS or Windows)
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

   - This acts like your development board's screen where you can monitor command output.
   - Every command you enter after step 5. below will have its output show up on this terminal windows.
   - This is also where the messages you receive from other nodes on the network will show up. Make sure you are keeping an eye on this terminal.

   ```
   python lib/main_controller.py
   ```
4. **Open a New Terminal Window:**
   - **On macOS:** Press `Cmd + T` to open a new Terminal tab.
   - **On Windows:** Press `Ctrl + Shift + T` to open a new Powershell tab.

   Make sure you have resized and set up both the terminal windows next to each other for ease of access.

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

✅ You're all set to start working on your team's objective! Congratulations!

❗️ P.S: All your tasks as part of the Blue and Red teams will be in the file `src/workspace.py`.

*Make sure to read the comments and follow the instructions within that file carefully.*

---
**Troubleshooting:** If your codebase starts breaking, we'll help you make a local backup of the `workspace.py` file, then you can delete the entire project and set it up again from scratch using the instructions above.

We're excited to see what you'll create and discover during this workshop! If you encounter any issues, don't hesitate to ask for help.
