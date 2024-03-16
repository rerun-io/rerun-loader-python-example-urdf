#include <iostream>
#include <rerun.hpp>

int main() {
    const auto rec = rerun::RecordingStream("urdf_from_cpp");
    rec.spawn().exit_on_failure();

    rec.set_time_seconds("testtime", 1.0);
    rec.set_time_sequence("seq", 1);

    rec.log_file_from_path("./example.urdf", "my_urdf/urdf");

    rec.set_time_seconds("testtime", 2.0);
    rec.set_time_sequence("seq", 2);

    rec.log_file_from_path("./example.urdf", "my_urdf/urdf");

    rec.set_time_seconds("testtime", 5.0);
    rec.set_time_sequence("seq", 5);

    rec.log_file_from_path("./example.urdf", "my_urdf/urdf");

    return 0;
}
