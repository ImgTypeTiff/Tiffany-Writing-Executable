# Tiffany Writing Executable
A thing in python that has been done.

More specifically an awful writing exectuable for all your needs. It's was supposed to be like calmly writer, but this has a more tiffany theme. 

___

# **FEATURES**!

- Markdown support!

- GFM support!

- Markdown to html! (type in markdown, then press ctrl+shift+p)

- Code blocks! (-ish)

- Plugin system! Add what ever you want! (I'll make a wiki or something)

- COUPLE OF KNOWN ISSUES:
	* There are two view menus! (i probably already fixed and i didn't change this)

	* The text direction toggle doesn't work. Why? Too complicated.

___

# Compilation!
- DEPENDENCIES:
	* markdown
	* py-gfm
	* pyside 6


I use nuitka in order to create executables. In the same folder (with the dependenies) run
```bash

nuitka --follow-imports  --include-package=markdown --include-package=mdx_partial_gfm --macos-create-app-bundle --enable-plugin=pyside6 --macos-app-icon=tws.icns --output-filename="tiffany writing executable" --macos-app-name="tiffany writing executable" "tiffany writing executable.py"

```

If you're a windows user PLEASE compile a version and send it to me. I don't use windows so I can't provide an exe. 

___
Okay have fun
