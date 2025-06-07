# Codebase Collector

**codebase_collector** is a Python tool designed to collect and organize code snippets from a specified directory, respecting .gitignore rules. It generates a structured output of the codebase, allowing for optional inclusion or exclusion of specific file extensions and directories. The resulting structure is written to an output markdown file, making it easy to visualize the code organization and content.

An example result is given in examples/codebase_collector.md. Such a result can than be used as context for a prompt.

## Directory Structure

```
codebase_collector/
    .gitignore
    collector.py
    requirements.txt
```

### Files

- **.gitignore**: Lists directories to be ignored, such as `venv` and `codebases`.
  
- **collector.py**: A script that collects and generates a directory tree structure from the given root directory, excluding paths specified in `.gitignore` files.

- **requirements.txt**: Defines the Python dependencies required for the project.

## Usage

### Collector Script

To generate a directory structure:

```bash
python collector.py <root_directory> [output_file] --ext <extensions> --exclude <dirs> --exclude_files <files>
```

- `<root_directory>`: The root directory of the codebase.
- `[output_file]`: Optional output file name (defaults to `<root_directory>.md`).
- `--ext <extensions>`: Include only files with specified extensions.
- `--exclude <dirs>`: Exclude specific directories.
- `--exclude_files <files>`: Exclude specific files.

#### Example

Clone this repo, install the requirements and get everything into a single file
```bash
git clone https://github.com/hueper/codebase_collector
cd codebase_collector
pip install -r requirements
python collector.py ../codebase_collector
```

## Installation

Ensure you have the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.