import numpy as np
import sys
# this test will treat the cube as a flat plain with 6 faces, each face is a 2D array of size 3x3
# the colours are represented as integers, for example: 0 = white, 1 = red, 2 = blue, 3 = orange, 4 = green, 5 = yellow
# define the cube as a 3D array of shape (6, 3, 3)

num_to_colour_in = {
    0: "W",
    1: "R",
    2: "B",
    3: "O",
    4: "G",
    5: "Y"
    }

def create_cube():
    shape = (6, 3, 3)
    cube = np.empty(shape=shape, dtype="<U10")
    



    # sides
    for i in range(6):
        counter = 1
        char = num_to_colour_in.get(i)
        # rows
        for r in range(3):

            # columns
            for c in range(3):
                sticker = f"{char}{counter}"
                cube[i][r][c] = sticker
                counter += 1
    return cube



# 0 = white, 1 = red, 2 = blue, 3 = orange, 4 = green, 5 = yellow
# this dictionary will define how the faces and strips are rotated when the whole cube is rotated in a certain direction
CUBE_ROTATIONS = {
    # direction: (face_map, rotation_map)
    8: (
        {0: 2, 1: 1, 2: 5, 3: 3, 4: 0, 5: 4},   # face_map: new_face_index -> old_face_index
        {1: 1, 3: -1, 4: 2},   # rotation_map: new_face_index -> number of 90-degree rotations to apply to that face (1 = clockwise, -1 = counterclockwise, 2 = 180 degrees)
    ),
    2: (
        {0: 4, 1: 1, 2: 0, 3: 3, 4: 5, 5: 2},
        {0: 2, 1: -1, 3: 1, 4: 2},
    ),
    4: (
        {0: 0, 1: 2, 2: 3, 3: 4, 4: 1, 5: 5},
        {0: -1, 3: 2, 4: 2, 5: 1},
    ),
    6: (
        {0: 0, 1: 4, 2: 1, 3: 2, 4: 3, 5: 5},
        {0: 1, 1: 2, 4: 2, 5: -1},
    ),
}

# this dictionary will define how the faces and strips are rotated when the front face is rotated in a certain direction
FACE_ROTATIONS = {
    # direction: (face, turn, cycle)
    # face: the index of the face to rotate (0 to 5)
    # turn: the direction to rotate the face (-1 = clockwise, 1 = counterclockwise)
    # cycle: a list of tuples defining the strips to rotate (face, kind, index, reverse)

    # clockwise
    2: {
        "face": 2,    # the face to rotate (front face)
        "turn": -1,    # the direction to rotate the face (-1 = clockwise, 1 = counterclockwise)
        # the cycle of strips to rotate (face, kind, index, reverse)
        "cycle": [    
            (0, "row", 2, False),
            (1, "col", 2, False),
            (5, "row", 0, True),
            (3, "col", 0, True),
        ],
    },
    # counterclockwise
    1: {
        "face": 2,
        "turn": 1,
        "cycle": [
            (0, "row", 2, False),
            (3, "col", 0, False),
            (5, "row", 0, True),
            (1, "col", 2, True),
        ],
    },
}


def get_strip(cube, face, kind, index, reverse):
    """
    This function gets a strip of the cube based on the face, kind, index, and reverse parameters.
    args:
        cube: a 3D array representing the cube
        face: the index of the face to get the strip from
        kind: the type of strip to get ("row" or "col")
        index: the index of the row or column to get
        reverse: whether to reverse the strip or not
    returns:
        a 1D array representing the strip of the cube
    """
    # get the strip from the cube based on the kind of strip (row or column) and reverse it if needed
    strip = cube[face, index, :].copy() if kind == "row" else cube[face, :, index].copy()
    return strip[::-1] if reverse else strip


def set_strip(cube, face, kind, index, values, reverse):
    """
    This function sets a strip of the cube based on the face, kind, index, values, and reverse parameters.
    args:
        cube: a 3D array representing the cube
        face: the index of the face to set the strip on
        kind: the type of strip to set ("row" or "col")
        index: the index of the row or column to set
        values: a 1D array representing the values to set on the strip
        reverse: whether to reverse the values before setting them or not
    returns:
        None
    """
    # reverse the values if needed before setting them on the cube
    values = values[::-1] if reverse else values
    # set the values on the cube based on the kind of strip (row or column)
    if kind == "row":
        cube[face, index, :] = values
    else:
        cube[face, :, index] = values


def apply_cube_rotation(cube, face_map, rotation_map):
    """
    This function applies a cube rotation based on the face_map and rotation_map parameters.
    args:
        cube: a 3D array representing the cube
        face_map: a dictionary mapping the new face indices to the old face indices
        rotation_map: a dictionary mapping the new face indices to the number of 90-degree rotations to apply to that face
    returns:
        None
    """
    # create a copy of the original cube to reference the original face positions and orientations
    original = [face.copy() for face in cube]

    # apply the cube rotation based on the face_map and rotation_map
    for new_face, old_face in face_map.items():
        rotated = np.rot90(original[old_face], rotation_map.get(new_face, 0))
        cube[new_face] = rotated


def apply_face_rotation(cube, move):
    """
    This function applies a face rotation based on the move parameters.
    args:
        cube: a 3D array representing the cube
        move: a dictionary containing the face to rotate, the direction to rotate, and the cycle of strips to rotate
    returns:
        None
    """
    # rotate the face itself
    cube[move["face"]] = np.rot90(cube[move["face"]], move["turn"])

    # get the strips to rotate based on the cycle defined in the move dictionary
    strips = [
        get_strip(cube, face, kind, index, reverse)
        for face, kind, index, reverse in move["cycle"]
    ]

    # shift the strips based on the direction to rotate (clockwise or counterclockwise)
    shifted = strips[-1:] + strips[:-1]

    # set the strips back to the cube based on the cycle defined in the move dictionary
    for spec, values in zip(move["cycle"], shifted):
        face, kind, index, reverse = spec
        set_strip(cube, face, kind, index, values, reverse)


def rotate_whole_cube(cube, direction):
    """
    This function rotates the whole cube based on user input.
    args:
        cube: a 3D array representing the cube
    returns:
        None
    """

    # if the user enters 0, we will skip the rotation and return
    if direction == 0:
        return

    # get the rotation from the CUBE_ROTATIONS dictionary based on the user input
    rotation = CUBE_ROTATIONS.get(direction)
    if rotation is None:
        print("Invalid input", "No rotation applied to the whole cube.")
        return

    # apply the cube rotation based on the face_map and rotation_map from the CUBE_ROTATIONS dictionary
    face_map, rotation_map = rotation
    apply_cube_rotation(cube, face_map, rotation_map)


def rotate_face(cube, move):
    """
    This function rotates the front face of the cube based on user input.
    args:
        cube: a 3D array representing the cube
    returns:
        None
    """
    # get the direction to rotate the front face from the user input


    # if the user enters 0, we will skip the rotation and return
    if move == 0:
        print("No rotation applied to the front face.")
        return

    # get the rotation from the FACE_ROTATIONS dictionary based on the user input
    rotation = FACE_ROTATIONS.get(move)
    if rotation is None:
        print("Invalid input", "No rotation applied to the front face.")
        return

    apply_face_rotation(cube, rotation)



def display_cube(cube):
    """
    This function displays the cube in a readable format.
    It takes a 3D array representing the cube and prints it in a human-readable format.
    args:
        cube: a 3D array of shape (6, 3, 3) representing the cube to be displayed
    returns:
        None
    """
    # this function will display the cube in a readable format
    # it will print it like this:
    #        0 0 0
    #        0 0 0
    #        0 0 0
    # 1 1 1  2 2 2  3 3 3
    # 1 1 1  2 2 2  3 3 3
    # 1 1 1  2 2 2  3 3 3
    #        5 5 5
    #        5 5 5
    #        5 5 5
    #        4 4 4
    #        4 4 4
    #        4 4 4
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(str(cube[0][i][j]) for j in range(3)))
    for i in range(3):
        print(" ".join(str(cube[1][i][j]) for j in range(3)), end="   ")
        print(" ".join(str(cube[2][i][j]) for j in range(3)), end="   ")
        print(" ".join(str(cube[3][i][j]) for j in range(3)))
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(str(cube[5][i][j]) for j in range(3)))
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(str(cube[4][i][j]) for j in range(3)))


def letter_display(cube):
    # this function will display the cube in a readable format with colors
    # it will print it like this:
    #        W W W
    #        W W W
    #        W W W
    # R R R  B B B  O O O
    # R R R  B B B  O O O
    # R R R  B B B  O O O
    #        Y Y Y
    #        Y Y Y
    #        Y Y Y
    #        G G G
    #        G G G
    #        G G G
    letter_map = {0: "W", 1: "R", 2: "B", 3: "O", 4: "G", 5: "Y"}   
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(letter_map[cube[0][i][j]] for j in range(3)))
    for i in range(3):
        print(" ".join(letter_map[cube[1][i][j]] for j in range(3)), end=" ")
        print(" ".join(letter_map[cube[2][i][j]] for j in range(3)), end=" ")
        print(" ".join(letter_map[cube[3][i][j]] for j in range(3)))
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(letter_map[cube[5][i][j]] for j in range(3)))
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(letter_map[cube[4][i][j]] for j in range(3)))


def colour_display(cube):
    """
    This function displays the cube in a readable format with colours.
    It takes a 3D array representing the cube and prints it in a human-readable format with colours (using ANSI).
    args:
        cube: a 3D array of shape (6, 3, 3) representing the cube to be displayed
    returns:
        None
    """

    def remove_last_char(s):
        if not isinstance(s, str):
            raise TypeError("Input must be a string")
        if len(s) == 0:
            return s
        return s[:-1]


    # this function will display the cube in a readable format with colours
    # we will use ANSI escape codes to print the colours in the terminal
    colour_map = {
        "W": "\033[97mW\033[0m",
        "R": "\033[91mR\033[0m",
        "B": "\033[94mB\033[0m",
        "O": "\033[93mO\033[0m",
        "G": "\033[92mG\033[0m",
        "Y": "\033[93mY\033[0m",
    }
    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(colour_map[remove_last_char(cube[0][i][j])] for j in range(3)))

    for i in range(3):
        print(" ".join(colour_map[remove_last_char(cube[1][i][j])] for j in range(3)), end=" ")
        print(" ".join(colour_map[remove_last_char(cube[2][i][j])] for j in range(3)), end=" ")
        print(" ".join(colour_map[remove_last_char(cube[3][i][j])] for j in range(3)))

    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(colour_map[remove_last_char(cube[5][i][j])] for j in range(3)))

    for i in range(3):
        print(" " * 6, end="")
        print(" ".join(colour_map[remove_last_char(cube[4][i][j])] for j in range(3)))


def game_loop():
    """
    This function is the main game loop. It initializes the cube and allows the user to rotate faces and the whole cube.
    It also keeps track of the number of moves made by the user and stops after a certain number of moves.
    args:
        None
    returns:
        None
    """
    moves = []
    try:
        cube = create_cube()
        display_cube(cube)
        colour_display(cube)
        move_count = 0
        while True:
            # display_cube(cube)
            # letter_display(cube)

            # get the direction to rotate the whole cube from the user input
            direction = int(
                input(
                    "Enter the direction to rotate the whole cube (8 = up, 2 = down, 4 = left, 6 = right, 0 = skips): "
                )
            )
            rotate_whole_cube(cube, direction)
            display_cube(cube)
            colour_display(cube)
            moves.append(direction)

            move = int(
                input(
                    "Enter the direction to rotate the front face (1 = clockwise, 2 = counterclockwise, 0 = skip): "
                )
            )
            rotate_face(cube, move)
            display_cube(cube)
            colour_display(cube)
            moves.append(move)


            move_count += 1
            if move_count >= 10:
                print("You have made 10 moves... Debug Stop")
                break

    except Exception as e: 
        with open("moves.txt", "w") as f:
            for m in moves:
                f.write(m)

        exc_type, exc_obj, exc_tb = sys.exc_info()

        print(exc_type, exc_obj, exc_tb)


if __name__ == "__main__":
    # cube = create_cube()
    # print("Initial cube:")
    # display_cube(cube)
    # colour_display(cube)

    # rotate_face(cube)
    # print("After rotating the front face clockwise:")
    # display_cube(cube)
    # colour_display(cube)

    game_loop()
