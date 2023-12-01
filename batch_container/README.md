When setting up virtual environment, first make sure you have deactivated any other venvs. Then, navigate to the `batch_container` directory and run:

```
python3 -m venv venv
. venv/bin/activate
pip install -r dev_requirements.txt
```

Then, edit the file `venv/bin/activate`. Add this line at the end of the file:

```
export PYTHONPATH="/absolute/path/to/collage/model/repo:$PYTHONPATH"
```

Replace `/absolute/path/to/collage/model/repo` with your own local collage repo destination. Note it must be an absolute path! ...Also install the correct requirements file from the local collage repo. TODO(auberon): Update when pyproject.toml is configured for model repo. The current approach manlges the PYTHONPATH even once the venv is deactivated.

Note that this will use a DIFFERENT venv than the one to be created in the `sam` directory of this same repo. This is by design. Make sure you are using the correct venv for testing the correct portion.