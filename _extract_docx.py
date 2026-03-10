import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract(path: str):
    with zipfile.ZipFile(path) as zf:
        # Some .docx exports use non-standard names (e.g., document2.xml), so grab the first match.
        target = next(
            (n for n in zf.namelist() if n.startswith("word/document")),
            None,
        )
        if not target:
            raise RuntimeError("No document XML found in docx")
        data = zf.read(target)
    root = ET.fromstring(data)
    for para in root.iter(NS + "p"):
        text = "".join((t.text or "") for t in para.iter(NS + "t")).strip()
        if text:
            yield text


def main(paths):
    for p in paths:
        print(f"--- {p} ---")
        for line in extract(p):
            print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
