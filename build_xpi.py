import json
import os
import zipfile

def build_xpi():
    xpi_name = "hunspell-tr.xpi"
    print(f"Building Firefox spelling dictionary extension: {xpi_name}...")

    # Define the manifest structure
    manifest = {
        "manifest_version": 2,
        "name": "Türkçe Yazım Denetimi Sözlüğü (Turkish Spelling Dictionary)",
        "version": "2.1.0",
        "description": "Turkish spelling dictionary for Firefox, including corrected â/î circumflex spelling entries.",
        "author": "Selim",
        "homepage_url": "https://github.com/selimsum/hunspell-tr",
        "dictionaries": {
            "tr": "dictionaries/tr_TR.dic",
            "tr-TR": "dictionaries/tr_TR.dic"
        },
        "browser_specific_settings": {
            "gecko": {
                "id": "tr-spelling-dictionary-selimsum@addons.mozilla.org",
                "strict_min_version": "61.0"
            }
        }
    }

    # Files to include in the package
    files_to_pack = {
        "tr_TR.dic": "dictionaries/tr_TR.dic",
        "tr_TR.aff": "dictionaries/tr_TR.aff",
        "LICENSE": "LICENSE"
    }

    # Open the zip file
    with zipfile.ZipFile(xpi_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Write manifest.json directly into zip
        manifest_data = json.dumps(manifest, indent=2, ensure_ascii=False)
        zip_file.writestr("manifest.json", manifest_data)
        print("Added manifest.json to XPI")

        # Write each source file into its designated path in the zip
        for src, dest in files_to_pack.items():
            if os.path.exists(src):
                zip_file.write(src, dest)
                print(f"Added {src} -> {dest}")
            else:
                print(f"Warning: Source file {src} not found! Skipping...")

    print(f"\nSuccessfully built {xpi_name}!")
    print("You can now install this dictionary in Firefox by going to 'about:debugging' -> 'This Firefox' -> 'Load Temporary Add-on' and selecting the 'manifest.json' (or the '.xpi' file directly after signing, or temporarily).")

if __name__ == "__main__":
    build_xpi()
