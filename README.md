### README for Document Tracker Application

This **Document Tracker** is a Python application that analyzes and processes user interactions with documents from a JSON dataset. It allows for detailed insights through both command-line interface (CLI) and graphical user interface (GUI) interactions. You can generate histograms, analyze reading times, and recommend similar documents based on user activity. The tool also offers export capabilities for various formats like PNG, PDF, PS, and DOT files.

---

### Table of Contents
- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
  - [Command-Line Interface](#command-line-interface)
  - [Graphical User Interface](#graphical-user-interface)
- [Examples](#examples)
  - [Histogram Generation](#histogram-generation)
  - [Reading Time Analysis](#reading-time-analysis)
  - [Document Recommendation](#document-recommendation)
  - [Exporting Graphs](#exporting-graphs)
- [Development](#development)

---

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/oscaroguledo/document-tracker.git
   cd document-tracker
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Required Libraries**:
   - `argparse`
   - `matplotlib`
   - `pandas`
   - `graphviz`
   - `user_agents`
   - `pycountry_convert`
   - `shutil`
   - `glob`

Make sure Graphviz is installed on your system. You can install it via:
- **Ubuntu/Debian**: 
   ```bash
   sudo apt-get install graphviz
   ```
- **macOS**:
   ```bash
   brew install graphviz
   ```

---

### Features

- **Histogram Visualization**: Generate histograms based on document views by countries, continents, or browser types.
- **Reading Time Analysis**: Analyze the top readers based on the amount of time spent on specific documents.
- **Document Recommendation**: Generate recommendations for documents that users also viewed based on the current document.
- **File Conversion**: Convert DOT files to PNG, PDF, and PS formats.
- **CLI/GUI**: Operate the program either from the command line or via a GUI.

---

### Usage

#### Command-Line Interface

To use the CLI, run the `main.py` script with appropriate arguments.

**General Usage**:
```bash
python main.py [options]
```

#### Available Options

- `-f, --file_name`: Specify the JSON file to analyze (e.g., `sample_tiny.json`).
- `-hs, --histogram`: Generate a histogram (true/false).
- `-hc, --hist_cat`: Specify the histogram category (`country`, `continent`, `browser`).
- `-x, --x_label`: Label for the X-axis of the histogram.
- `-y, --y_label`: Label for the Y-axis of the histogram.
- `-a, --title`: Title of the histogram.
- `-t, --reading_time`: Analyze the reading time (true/false).
- `-ld, --also_like_documents`: Find similar documents (true/false).
- `-lg, --also_like_graph`: Export similar document graph (true/false).
- `-dpng, --dot_to_png`: Convert a DOT file to PNG.
- `-dpdf, --dot_to_pdf`: Convert a DOT file to PDF.
- `-dps, --dot_to_ps`: Convert a DOT file to PS.

#### Graphical User Interface

Simply run the application without any arguments to launch the GUI:

```bash
python main.py
```

The GUI allows you to load JSON data, select analysis options, and visualize the results directly.

---

### Examples

#### Histogram Generation

To generate a histogram showing the number of views by country for a specific document:

```bash
python main.py -f sample_tiny.json -hs True -hc country -x "Countries" -y "Frequency" -a "Countries of Viewers"
```

#### Reading Time Analysis

To get the top 10 readers by total reading time:

```bash
python main.py -f sample_tiny.json -t True -l 10
```

#### Document Recommendation

To generate a "similar documents" graph based on a specific document and visitor:

```bash
python main.py -f sample_tiny.json -ld True -lg True -d <document_uuid> -v <visitor_uuid>
```

#### Exporting Graphs

To convert a DOT file to PNG format:

```bash
python main.py -dpng True -src sample_tiny.dot -dest sample_tiny.png
```

---

### Development

This project utilizes object-oriented design, with the `DataGetter` class handling core data functionalities such as reading JSON files, generating histograms, calculating reading times, and providing document recommendations. The GUI is managed by `run_gui_app` and the CLI by `run_cli_app`.

Feel free to extend this project to accommodate new features like different visualizations, more sophisticated recommendation algorithms, or integrations with external data sources.

---

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

### Contributors

- [Oscar Oguledo](https://github.com/oscaroguledo)

---

This README serves as a quick-start guide for users of the Document Tracker tool, outlining key features, installation steps, usage, and examples for analyzing document data.

