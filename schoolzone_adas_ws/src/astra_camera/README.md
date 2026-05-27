# Astra Camera Packages

Keep Astra-related packages in this single directory.

Current packages:

- `astra_camera`
- `astra_camera_msgs`
- `astra_mini_calibration`

The ADAS package expects these topics:

```text
/camera/color/image_raw
/camera/depth/image_raw
/camera/color/camera_info
/camera/depth/points
```

Keep the ADAS logic in `../schoolzone_adas/`; keep Astra camera integration here.

Typical launch:

```bash
ros2 launch astra_camera astra_mini.launch.py
```

Full project launch:

```bash
ros2 launch schoolzone_adas schoolzone_adas_with_astra.launch.py
```
