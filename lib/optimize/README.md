# Python 3D Data Optimization Project

This is a Python project used for the generation of optimized data from uncompressed `.obj` files. The project includes several scripts for data processing and user interface.

## Table of Contents
- [Requirements](#requirements)
- [Main Scripts](#main-scripts)
- [How to Run with Interface](#how-to-run-with-interface)
- [How to Run With Command](#how-to-run-with-command)

## Requirements

The project requires Python 3.8.10 and several Python packages. All requirements are listed in the `requirements.txt` file. You can install them using pip:

```
    $ pip install -r requirements.txt
```

## Main Scripts

There are four main scripts in the project: `main.py`, `objsplit.py`, `interface/interface.py`, and `interface/style.py`.

- `main.py` : The main entry point of the project. It uses command line arguments to specify the paths for uncompressed, split, and optimized files. It calls the function `generateOptimizedData` from `objsplit.py` to generate optimized data.

- `objsplit.py` : This script is used to generate optimized data from uncompressed `.obj` files. It performs several operations such as object separation, optimization, and data generation related to teeth, IPR, movements, landmarks, and so on. The generated data is saved in a JSON file.

- `interface/interface.py` : This script is used to create and manage the user interface of the application. The interface is designed using Python's Tkinter library and includes several features for easy manipulation and visualization of the data.

- `interface/style.py` : This script is used to create custom widgets for the user interface such as buttons, labels, and text fields with custom styles, rounded shapes, and specified colors.


## How to Run with Interface

The `interface/interface.py` script provides a graphical user interface (GUI) for the application, making it easier to interact with the data.

1. Ensure you have Python 3.8.10 installed on your machine.

2. Install the required packages:

    ```
    pip install -r requirements.txt
    ```

3. Run the `interface/interface.py` script:

    ```
    python interface/interface.py
    ```

    This will launch the GUI where you can select files, decompress them, and view details within the application. This interface serves as an alternative way to interact with the application without having to use command line arguments.

### Interface Options Configuration

The `interface/interface.py` script relies on a configuration file named `interface/options.txt` to specify various options for running the application with the interface.

The `options.txt` file has the following structure [example]:

```
SERVER_FILES_PATH=../../Aligneur_server_V2/files/
EXTRACT_FILES_TO=../input_data/
SPLITTED_DATA_DIR=../splitted_data/
PYTHON_OPTIMIZING_FILE=../main.py
OPTIMIZED_DATA_DIR=../optimized_data/
```


Each line in the `options.txt` file defines the path to a specific directory or file that is used by the application:

- `SERVER_FILES_PATH` : Path to the server files.
- `EXTRACT_FILES_TO` : Path where the files will be extracted to.
- `SPLITTED_DATA_DIR` : Path to the directory where the split data is stored.
- `PYTHON_OPTIMIZING_FILE` : Path to the `main.py` Python script.
- `OPTIMIZED_DATA_DIR` : Path to the directory where the optimized data is stored.

When running the `interface/interface.py` script, it reads these options and uses them to decompress the provided setup to a custom path. This allows the possibility of launching multiple simultaneous optimization processes. 

The interface provides the following functionalities:

- **Patient therapies visualization**: Allows viewing of different patient therapies from the server.
- **Therapy history details**: Provides a detailed history of each therapy.
- **Missing setup identification**: Identifies any missing setups within the patient's data.
- **Add patient folder**: Allows the addition of a new patient folder to the server.
- **Add setup**: Allows the addition of a new setup for a particular patient.
- **Client chat response**: Enables the user to respond to client chat for each setup.


## How to Run With Command 

1. Ensure you have Python 3.10.6 installed on your machine.

2. Install the required packages:

    ```
    pip install -r requirements.txt
    ```

3. Run the `main.py` script with the necessary command line arguments:

    ```
    python main.py <uncompressed_files_dir> <splitted_files_dir> <optimized_files_dir>
    ```

    Replace `<uncompressed_files_dir>`, `<splitted_files_dir>`, and `<optimized_files_dir>` with your own directory paths.

## Interface Functionality

The interface for this application is created using the `interface/interface.py` script. The interface allows users to interact with the application in a more user-friendly way than using the command line. Here is an overview of how the interface works based on the provided code.

### Initialization

When the `interface/interface.py` script is run, it first checks if an instance of itself is already running. If so, the script exits with an error message to prevent multiple instances of the interface.

The script then reads the `options.txt` file to get the path to the server files. If the path is not found in the `options.txt` file, the script will exit with an error message.

Once the server files path is known, the script gets a list of all directories in the server files path. These directories are assumed to be the patient folders.

### Creating the Interface

The interface is created using the `tkinter` library. A new window is created with a title of "Interface". This window is then filled with various widgets to allow the user to interact with the application.

The main widget is a canvas, which is used to display a list of buttons, one for each patient folder. Each button is labeled with the name of the patient folder it represents. If the patient folder is missing any required files, the button will have a small circle on it to indicate this.

Above the canvas is a frame containing a search bar and a "New Patient" button. The search bar allows the user to search for specific patient folders by name. The "New Patient" button allows the user to create a new patient folder.

When a patient folder button is clicked, a new window is opened to display the details of that patient folder. This includes a history of all changes made to the folder.

### Multithreading

The script uses multithreading to allow multiple tasks to be performed simultaneously. This includes running the optimization process, updating the interface, and responding to user input. The script checks if an optimization process is currently running before starting a new one to avoid conflicts.

### Error Handling

The script includes error handling to handle common issues that may occur. This includes checking if required files are missing, handling invalid user input, and more.

This is a broad overview of the interface functionality. More specific details will be added as the remaining code is reviewed.


