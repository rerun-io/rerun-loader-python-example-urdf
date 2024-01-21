#!/usr/bin/env python3
"""Example of an executable data-loader plugin for the Rerun Viewer for URDF files."""
from __future__ import annotations

import argparse
import os
import tempfile

import numpy as np
import rerun as rr  # pip install rerun-sdk
import scipy.spatial.transform as st
import trimesh
from urdf_parser_py import urdf as urdf_parser


class URDFLogger:
    """Class to log a URDF to Rerun."""

    def __init__(self, filepath: str) -> None:
        self.urdf = urdf_parser.URDF.from_xml_file(filepath)
        self.mat_name_to_mat = {mat.name: mat for mat in self.urdf.materials}

    def link_entity_path(self, link: urdf_parser.Link) -> str:
        """Return the entity path for the URDF link."""
        root_name = self.urdf.get_root()
        link_names = self.urdf.get_chain(root_name, link.name)[0::2]  # skip the joints
        return "/".join(link_names)

    def joint_entity_path(self, joint: urdf_parser.Joint) -> str:
        """Return the entity path for the URDF joint."""
        root_name = self.urdf.get_root()
        link_names = self.urdf.get_chain(root_name, joint.child)[0::2]  # skip the joints
        return "/".join(link_names)

    def log(self) -> None:
        """Log a URDF file to Rerun."""
        rr.log("", rr.ViewCoordinates.RIGHT_HAND_Z_UP, timeless=True)  # default ROS convention

        for link in self.urdf.links:
            entity_path = self.link_entity_path(link)
            self.log_link(entity_path, link)

        for joint in self.urdf.joints:
            entity_path = self.joint_entity_path(joint)
            self.log_joint(entity_path, joint)

    def log_link(self, entity_path: str, link: urdf_parser.Link) -> None:
        # create one mesh out of all visuals
        for i, visual in enumerate(link.visuals):
            self.log_visual(entity_path + f"/visual_{i}", visual)

    def log_joint(self, entity_path: str, joint: urdf_parser.Joint) -> None:
        translation = rotation = None

        if joint.origin is not None and joint.origin.xyz is not None:
            translation = joint.origin.xyz

        if joint.origin is not None and joint.origin.rpy is not None:
            rotation = st.Rotation.from_euler("xyz", joint.origin.rpy).as_matrix()

        rr.log(entity_path, rr.Transform3D(translation=translation, mat3x3=rotation))

    def log_visual(self, entity_path: str, visual: urdf_parser.Visual) -> None:
        material = None
        if visual.material is not None:
            if visual.material.color is None and visual.material.texture is None:
                # use globally defined material
                material = self.mat_name_to_mat[visual.material.name]
            else:
                material = visual.material

        transform = np.eye(4)
        if visual.origin is not None and visual.origin.xyz is not None:
            transform[:3, 3] = visual.origin.xyz
        if visual.origin is not None and visual.origin.rpy is not None:
            transform[:3, :3] = st.Rotation.from_euler("xyz", visual.origin.rpy).as_matrix()

        mesh = mesh_path = None
        if isinstance(visual.geometry, urdf_parser.Mesh):
            tmp_dir = tempfile.mkdtemp()
            tmp_mesh = trimesh.load_mesh(visual.geometry.filename)
            tmp_mesh.export(os.path.join(tmp_dir, "mesh.glb"))
            mesh_path = os.path.join(tmp_dir, "mesh.glb")
        elif isinstance(visual.geometry, urdf_parser.Box):
            mesh = trimesh.creation.box(extents=visual.geometry.size, transform=transform)
        elif isinstance(visual.geometry, urdf_parser.Cylinder):
            mesh = trimesh.creation.cylinder(
                radius=visual.geometry.radius,
                height=visual.geometry.length,
                transform=transform,
            )
        elif isinstance(visual.geometry, urdf_parser.Sphere):
            mesh = trimesh.creation.icosphere(
                radius=visual.geometry.radius,
                transform=transform,
            )
        else:
            rr.log(
                "",
                rr.TextLog("Unsupported geometry type: " + str(type(visual.geometry))),
            )
            mesh = trimesh.Trimesh()


        if mesh is not None:
            mesh.visual = trimesh.visual.ColorVisuals()
            if material is not None and material.color is not None and mesh.visual is not None:
                mesh.visual.vertex_colors = material.color.rgba

            # TODO support material with texture

            rr.log(
                entity_path,
                rr.Mesh3D(
                    vertex_positions=mesh.vertices,
                    indices=mesh.faces,
                    vertex_normals=mesh.vertex_normals,
                    vertex_colors=mesh.visual.vertex_colors,
                ),
                timeless=True,
            )
        else:
            rr.log(
                entity_path,
                rr.Asset3D(
                    path=mesh_path,
                    transform=rr.TranslationAndMat3x3(translation=transform[:3, 3], mat3x3=transform[:3, :3]),
                ),
                timeless=True,
            )


# The Rerun Viewer will always pass these two pieces of information:
# 1. The path to be loaded, as a positional arg.
# 2. A shared recording ID, via the `--recording-id` flag.
#
# It is up to you whether you make use of that shared recording ID or not.
# If you use it, the data will end up in the same recording as all other plugins interested in
# that file, otherwise you can just create a dedicated recording for it. Or both.
parser = argparse.ArgumentParser(
    description="""
This is an example executable data-loader plugin for the Rerun Viewer.
Any executable on your `$PATH` with a name that starts with `rerun-loader-` will be
treated as an external data-loader.

This example will load URDF files, logs them to Rerun,
and returns a special exit code to indicate that it doesn't support anything else.

To try it out, copy it in your $PATH as `rerun-loader-python-example-urdf`,
then open a URDF file with Rerun (`rerun example.urdf`).
    """
)
parser.add_argument("filepath", type=str)
parser.add_argument("--recording-id", type=str)
args = parser.parse_args()


def main() -> None:
    is_file = os.path.isfile(args.filepath)
    is_urdf_file = ".urdf" in args.filepath

    # Inform the Rerun Viewer that we do not support that kind of file.
    if not is_file or not is_urdf_file:
        exit(rr.EXTERNAL_DATA_LOADER_INCOMPATIBLE_EXIT_CODE)

    rr.init("rerun_example_external_data_loader_urdf", recording_id=args.recording_id)
    # The most important part of this: log to standard output so the Rerun Viewer can ingest it!
    rr.stdout()

    urdf_logger = URDFLogger(args.filepath)
    urdf_logger.log()


if __name__ == "__main__":
    main()
