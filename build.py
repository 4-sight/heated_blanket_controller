import python_minifier
import glob

exclude = ["build.py", "display.py", "inputs.py"]
output_dir = "./build/"

files = filter(lambda file: file not in exclude, glob.glob("*.py"))

for filename in files:
    with open(filename) as f:
        minified = python_minifier.minify(f.read())
        dest = open(output_dir + filename, "w")
        dest.write(minified)
        dest.close()
        f.close()
