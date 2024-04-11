# URDF -> Rerun plugin
This is an example data-loader plugin that lets you view URDF files in the [Rerun](https://github.com/rerun-io/rerun/) Viewer.
It uses the [external data loader mechanism](https://www.rerun.io/docs/howto/open-any-file#external-dataloaders) to add this capability to the viewer without modifying the viewer itself.

https://github.com/rerun-io/rerun-loader-python-example-urdf/assets/9785832/51659bee-330d-4058-980d-414d2e4e63bb

External data loaders are executables that are available to the Rerun Viewer via the `PATH` variable, with a name that starts with `rerun-loader-`.

This example is written in Python, and uses [urdf_parser_py](https://github.com/ros/urdf_parser_py/tree/ros2) to read the files. ROS package-relative paths support both ROS 1 and ROS 2-based resolving.

## Installing the Rerun Viewer
The simplest option is just (*this example currently requires a prerelease*):
```bash
pip install --pre -f https://build.rerun.io/commit/1dad7c8/wheels --upgrade rerun-sdk
```
Read [this guide](https://www.rerun.io/docs/getting-started/installing-viewer) for more options.

## Installing the plugin

### Installing pipx

The most robust way to install the plugin to your `PATH` is using [pipx](https://pipx.pypa.io/stable/).

If you don't have `pipx` installed on your system, you can follow the official instructions [here](https://pipx.pypa.io/stable/installation/).

### Installing the plugin with pipx
Now you can install the plugin to your `PATH` using

```bash
pipx install git+https://github.com/rerun-io/rerun-loader-python-example-urdf.git
pipx ensurepath
```
Note: you can use the `--python` argument to specify the Python interpreter to use with pipx.
On unix-like systems `--python $(which python)` will use the currently active Python.

Make sure it's installed by running it from your terminal, which should output an error and usage description:
```bash
rerun-loader-urdf
usage: rerun-loader-urdf [-h] [--recording-id RECORDING_ID] filepath
rerun-loader-urdf: error: the following arguments are required: filepath
```

## Try it out
### Download an example URDF file
```bash
curl -OL https://github.com/rerun-io/rerun-loader-python-example-urdf/raw/main/example.urdf
```

### Open in the Rerun Viewer
You can either first open the viewer, and then open the file from there using drag-and-drop or the menu>open… dialog,
or you can open it directly from the terminal like:
```bash
rerun example.urdf
```
