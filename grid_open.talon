tag: user.fine_grid_enabled
-
grid off:
    user.fine_grid_close()
<user.coordinate>:
    user.go_coordinate(coordinate)
	mouse_click(0)
move <user.coordinate>:
    user.go_coordinate(coordinate)
pick <user.coordinate>:
    user.go_coordinate(coordinate)
	mouse_click(0)
    user.fine_grid_close()
zoom <user.coordinate>:
    user.zoom(coordinate)
grid reset:
    user.fine_grid_reset()
