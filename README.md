# SEARCH_FILES_WINDOWS

Fast, simple Windows file search GUI.

A lightweight desktop utility (built with Python + ttkbootstrap) to quickly find files and folders on Windows. The easiest way to run it is to download the packaged .exe from the `search` folder and run it.

## Quick overview

- Search by filename (substring match).
- Filter results by common file types (Documents, Images, Videos, Audio, Code, Archives) or choose "All Files" or "Folders Only".
- Toggle case-sensitive matching.
- Option to search subfolders or only the top folder.
- Limit maximum results (default 500).
- Double-click a result to open it; right-click for context actions (Open, Open Folder Location, Copy Path, Copy Name).
- Uses a fast, batched search approach that updates the UI as results are found and supports cancelling.

## Simple installation (recommended)

1. Open this repository in your browser: https://github.com/UNKN0WN4O4/SEARCH_FILES_WINDOWS
2. Go to the `search` folder (in the repo) and download the available `.exe` file.
3. Run the downloaded `.exe` (no installation required).

Note: Only run executables from sources you trust.

## Running from source (optional)

If you prefer to run the app from source, you can:

1. Install Python 3.8+ for Windows.
2. Clone the repo:
   git clone https://github.com/UNKN0WN4O4/SEARCH_FILES_WINDOWS.git
3. (Recommended) Create and activate a virtual environment:
   python -m venv env
   env\Scripts\activate
4. Install dependencies (if a requirements.txt is present) or at minimum:
   pip install ttkbootstrap
5. Run:
   python Search.py

## Usage

- Enter a search term in the "Search" box and press Enter or click "Search".
- Choose the "Search in" folder using Browse or quick buttons (Home / Desktop / Downloads).
- Use the Filter dropdown to restrict results by type (Documents, Images, etc.) or set "Folders Only".
- Check "Match Case" to make the search case-sensitive.
- Toggle "Subfolders" to include or exclude recursion into subdirectories.
- Use the "Max" spinner to set a maximum number of results.
- Click "Cancel" while searching to stop early.
- Double-click a result to open it with the default application.
- Right-click a result to open the file, open its containing folder (Explorer), or copy path/name to clipboard.

## Implementation notes (from Search.py)

- Built with ttkbootstrap for a modern themed Tkinter UI.
- Uses pathlib for fast file iteration and globbing.
- Searches are done on a background thread and results are batched (every 25 results) to avoid UI freezes.
- Hidden files/folders (names starting with `.`) are skipped.
- Permission errors and other OS errors are handled/skipped for individual files.
- File sizes and last-modified times are shown in the UI; directories are marked `<DIR>`.
- The code uses Windows-specific calls (e.g., `os.startfile` and `explorer`), so the packaged executable and the app are intended for Windows.

## Limitations & Safety

- Windows-only (opening files / explorer integration rely on Windows APIs).
- Hidden files/folders are skipped intentionally for speed.
- The simple packaged installation (download .exe) means you should only run executables from trusted sources.
- The GUI skips files/folders which raise permission errors; those items will not appear in results.

## Troubleshooting

- If double-click/open doesn't work, ensure you are running on Windows and the `.exe` wasn't blocked by antivirus.
- If Search.py fails from source, confirm `ttkbootstrap` is installed and you are on a supported Python version.
- If the search seems slow, increase the Max results or narrow filters to reduce file traversal.

## Contributing

- Feel free to submit issues or PRs. For adding features or packaging improvements, include a short description of what and why.
