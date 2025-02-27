## Convert CYZ Files to JSON

### Overview
This repository provides tools to convert `.cyz` files into `.json` format using a combination of .NET and Python programs. The process involves:
1. Setting up a .NET environment and modifying a specific C# file.
2. Using Python scripts to extract relevant metadata and images.

## Installation and Setup

### Step 1: Install .NET (Windows Only)
To install .NET on Windows, run the following commands in the terminal:

```sh
winget install Microsoft.DotNet.SDK.8
winget install Microsoft.DotNet.DesktopRuntime.8
winget install Microsoft.DotNet.AspNetCore.8
```

After installation, restart your computer to complete the setup.

### Step 2: Install `cyz2json` Program
The `cyz2json` program is required for conversion and can be found at [OBAMANEXT/cyz2json](https://github.com/OBAMANEXT/cyz2json/tree/main).

1. Clone the repository to any location:

   ```sh
   git clone https://github.com/OBAMANEXT/cyz2json.git
   ```

2. Navigate to the cloned repository:

   ```sh
   cd ~\YourOwnFolder\cyz2json\Cyz2Json
   ```

### Step 3: Install Required Packages
While inside the `Cyz2Json` folder, add the necessary dependencies:

```sh
dotnet add package OpenCvSharp4 --version 4.10.0.20240616
dotnet add package OpenCvSharp4.runtime.win --version 4.10.0.20240616
```

### Step 4: Replace `Program.cs`
The `Program.cs` file must be updated. The modified version is available in this repository under `cyz2json_DOTNET_program`. Replace the existing `Program.cs` file in `Cyz2Json` with this updated version.

### Step 5: Build the .NET Program
Run the following command to build the program:

```sh
dotnet build -o bin
```

Once completed, copy the path to the built program and add it to the `config.txt` file in the `cyz2json_python` folder.

---

## Python Scripts (`cyz2json_python`)
This folder contains Python scripts for processing `.cyz` files after converting them to `.json`.

### Scripts Overview

| Script | Description |
|--------|-------------|
| `conversion_json.py` | Converts `.cyz` files to `.json` in bulk. |
| `extraction_image.py` | Extracts images from the generated JSON files. |
| `automated_directories.py` | Updates the configuration file automatically for bulk processing. |

### Processing Options
#### Single File Processing
1. Open the `config.txt` file.
2. Paste the path of the `.cyz` file directory.
3. Run `conversion_json.py` to generate a `.json` file with metadata.

#### Batch Processing
For multiple files, use `automated_directories.py`:
1. Run the script and provide paths to directories containing `.cyz` files.
2. The script updates `config.txt` automatically.
3. Run `conversion_json.py` and `extraction_image.py` to process files in a loop.

---

## Additional Information
The CYZ data extraction program is adapted from [OBAMANEXT/cyz2json](https://github.com/OBAMANEXT/cyz2json) and enhanced by VLIZ to extract additional metadata. The updated program is provided with this deliverable.

To get started, open your Python IDE and use `conversion_json.py` to extract metadata from `.cyz` files. The output will be structured `.json` files containing relevant metadata and extracted images.

---

This README provides all the necessary steps for setup and usage. If you encounter issues, please check dependencies and verify the installation steps.
