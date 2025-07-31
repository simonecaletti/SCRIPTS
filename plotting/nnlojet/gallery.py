#!/usr/bin/env python3

from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description="Generate an interactive PDF plot gallery")
parser.add_argument("--output", default="gallery.html", help="Output HTML file path")
parser.add_argument("--input", nargs="+", required=True, help="List of folders with PDFs")
parser.add_argument("--runcard-path", default="", help="Folder containing .run files")
args = parser.parse_args()

# List of folders to include
folders = [str(folder) for folder in args.input]
output_html_path = args.output

# Build map of .run files by stem
runcard_map = {}
runcard_folder = Path(args.runcard_path)
if not runcard_folder.is_dir():
    raise ValueError(f"Provided --runcard-path {runcard_folder} is not a directory")

for runfile in runcard_folder.glob("*.run"):
    runcard_map[runfile.stem] = runfile

page_title = "PDF Gallery: " + ", ".join(runcard_map.keys())
#print(page_title)

html = f"""
<html>
<head>
    <title>{page_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        summary {{
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }}
        .controls {{ margin-bottom: 20px; }}
        .plot-grid {{
            display: grid;
            grid-gap: 20px;
            margin-top: 10px;
        }}
        .plot-container {{
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 10px;
            position: relative;
        }}
        embed {{
            border: 1px solid #aaa;
            width: 100%;
            height: 400px;
        }}
        h3 {{ margin-top: 0; }}
        .clickable-title {{
            color: #007BFF;
            cursor: pointer;
            text-decoration: underline;
        }}
        .clickable-title:hover {{
            color: #0056b3;
        }}
        input[type="text"], select {{
            padding: 10px;
            font-size: 16px;
            margin-right: 20px;
        }}
    </style>
    <script>
        function filterPlots() {{
            const input = document.getElementById("searchInput").value.toLowerCase();
            const plots = document.getElementsByClassName("plot-container");
            for (let i = 0; i < plots.length; i++) {{
                const name = plots[i].getAttribute("data-name").toLowerCase();
                plots[i].style.display = name.includes(input) ? "" : "none";
            }}
        }}

        function updateGrid() {{
            const columns = document.getElementById("columnsSelect").value;
            const grids = document.getElementsByClassName("plot-grid");
            for (let i = 0; i < grids.length; i++) {{
                grids[i].style.gridTemplateColumns = "repeat(" + columns + ", 1fr)";
            }}
        }}

        function toggleFullscreen(id) {{
            const el = document.getElementById(id);
            if (!document.fullscreenElement) {{
                el.requestFullscreen().catch(err => alert(`Error: ${{err.message}}`));
            }} else {{
                document.exitFullscreen();
            }}
        }}
    </script>
</head>
<body>
<h1>{page_title}</h1>

<div class="controls">
    <input type="text" id="searchInput" onkeyup="filterPlots()" placeholder="Search plots by filename...">
    <label for="columnsSelect">Plots per row:</label>
    <select id="columnsSelect" onchange="updateGrid()">
        <option value="1">1</option>
        <option value="2" selected>2</option>
        <option value="3">3</option>
        <option value="4">4</option>
    </select>
</div>
"""

# Folder loop
for folder in folders:
    folder_path = Path(folder)
    if not folder_path.is_dir():
        print(f"Warning: folder '{folder}' not found. Skipping.")
        continue

    html += f"<details open><summary>{folder}</summary>\n"
    html += '<div class="plot-grid" style="grid-template-columns: repeat(2, 1fr);">\n'

    for i, pdf_file in enumerate(sorted(folder_path.glob("*.pdf"))):
        relative_path = f"{folder}/{pdf_file.name}"
        base_name = pdf_file.stem
        embed_id = f"embed_{folder.replace('/', '_')}_{i}"
        runcard = runcard_map.get(base_name)

        if runcard:
            title_html = f'<a href="{runcard}" target="_blank" class="clickable-title">{runcard.name}</a>'
        else:
            title_html = f'<span class="clickable-title">{pdf_file.name}</span>'

        html += f"""
        <div class="plot-container" data-name="{pdf_file.name}">
            <h3 onclick="toggleFullscreen('{embed_id}')">{title_html}</h3>
            <embed id="{embed_id}" src="{relative_path}" type="application/pdf">
        </div>
        """

    html += "</div></details>\n"

html += """
</body>
</html>
"""

# Write to file
with open(output_html_path, "w") as f:
    f.write(html)

print(f"Gallery saved to: {output_html_path}")
