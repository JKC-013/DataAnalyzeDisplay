from flask import Flask, render_template, request, jsonify
import os
import nbformat
import nbconvert

app = Flask(__name__)
NOTEBOOKS_DIR = "notebooks"

# Ensure the notebooks directory exists
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

@app.route("/")
def index():
    """Serve the main HTML page."""
    notebooks = [f for f in os.listdir(NOTEBOOKS_DIR) if f.endswith(".ipynb")]
    return render_template("index.html", notebooks=notebooks)

@app.route("/notebooks", methods=["GET"])
def list_notebooks():
    """Return a list of stored notebooks."""
    notebooks = [f for f in os.listdir(NOTEBOOKS_DIR) if f.endswith(".ipynb")]
    return jsonify({"notebooks": notebooks})

@app.route("/notebooks/<filename>", methods=["GET"])
def get_notebook(filename):
    """Convert and return the notebook as HTML."""
    file_path = os.path.join(NOTEBOOKS_DIR, filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Notebook not found"}), 404

    with open(file_path, "r", encoding="utf-8") as f:
        notebook_data = nbformat.read(f, as_version=4)

    # Convert notebook to HTML
    html_exporter = nbconvert.HTMLExporter()
    html_exporter.exclude_input = False  # Keep code cells
    html_output, _ = html_exporter.from_notebook_node(notebook_data)
    
    # Process headings for formatting
    html_output = html_output.replace("¶", "")  # Remove last character in each heading
    
    # Ensure tables are properly rendered
    html_output = html_output.replace("<table>", "<table class='table'>")
    
    return jsonify({"html": html_output})

@app.route("/upload", methods=["POST"])
def upload_notebook():
    """Handle notebook file upload."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".ipynb"):
        return jsonify({"error": "Only .ipynb files are allowed"}), 400

    file_path = os.path.join(NOTEBOOKS_DIR, file.filename)
    file.save(file_path)

    return jsonify({"message": "Notebook uploaded successfully!", "new_notebook": file.filename}), 200

if __name__ == "__main__":
    app.run(debug=True)