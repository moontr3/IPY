# IPYP Syntax

## Types
- `INT`: Integer value - `10`
- `FLOAT`: Floating point value - `10.5`
- `STRING`: Text string - `"Test"`
- `BOOL`: True or false. Can be written in uppercase or lowercase - `True`
- `KEYWORD`: Variable/function name. Basically a string without quotes used for system stuff - `var1`
- `NULL`: Null. All uppercase - `NULL`

## Window management

### `SETRES <xsize: INT> <ysize: INT>`
Sets the resolution of a window.

### `SETFPS <fps: INT>`
Sets the target FPS of a game. Pass `0` to disable FPS limit.

### `LOADSHEET <filename: STRING>`
Loads a spritesheet by filename.

### `FILL <r: INT> <g: INT> <b: INT>`
Fills the whole screen with the desired RGB color.

### `DRAWSPRITE <sprite: STRING> <x: INT|FLOAT> <y: INT|FLOAT>`
Draws a desired sprite at a designated position.

## Basic commands

### `LOG <text: STRING>`
Prints the text to the stdout.

### `BREAK`
Finishes execution of current block.

### `RETURN <value: ANY>`
Returns a value in a function.

### `POINT <name: KEYWORD>`
Creates a go-to point.

### `GOTO <pointname: KEYWORD>`
Goes to a go-to point created by `POINT`.

### `CALL <func: KEYWORD>`
Calls a function.

## Variables

### `ASSIGN <name: KEYWORD> <value: ANY>`
Assigns a variable.

### `NOT <var: BOOL>`
Inverts a boolean variable.

### `INVERT <var: INT|FLOAT>`
Inverts an integer or a float, so 10.5 becomes -10.5.

### `SPLIT <var: STRING> <arrayname: KEYWORD>`
Splits a string and puts each symbol in an array <arrayname>.

### `TOSTRING <var: ANY>`
Converts variable <var> into a string.

## Logic statements

### `IFEQUALS <var1: ANY> <var2: ANY>`
Runs the next line if the variables are equal.
If otherwise, skips the next line.

### `IFDIFF <var1: ANY> <var2: ANY>`
Runs the next line if the variables are NOT equal.
If otherwise, skips the next line.

### `IFGREATER <var1: INT|FLOAT> <var2: INT|FLOAT>`
Runs the next line if <var1> is greater than <var2>.
If otherwise, skips the next line.

### `IFSMALLER <var1: INT|FLOAT> <var2: INT|FLOAT>`
Runs the next line if <var1> is smaller than <var2>.
If otherwise, skips the next line.

## Math

### `ADD <var1: INT|FLOAT> <var2:INT|FLOAT>`
Adds <var2> to <var1>.

### `SUB <var1: INT|FLOAT> <var2: INT|FLOAT>`
Substracts <var2> from <var1>.

### `MUL <var1: INT|FLOAT> <var2: INT|FLOAT>`
Multiplies <var1> by <var2>.

### `DIV <var1: INT|FLOAT> <var2: INT|FLOAT>`
Divides <var1> by <var2>.

### `TOINT <var: INT|FLOAT>`
Converts <var> into an integer.

### `RNDINT <targetvar: KEYWORD> <min: INT> <max: INT>`
Puts a random integer from <min> to <max> (inclusive) to <targetvar>.

## Arrays

### `ARRAY <name: KEYWORD>`
Creates an array.

### `APPEND <arrayname: KEYWORD> <value: ANY>`
Appends a value to an array.

### `REMOVE <arrayname: KEYWORD> <index: INT>`
Removes a value at an index from an array.

### `LENGTH <arrayname: KEYWORD> <targetvar: KEYWORD>`
Puts the length of the array into a variable <targetvar>.

### `INDEX <arrayname: KEYWORD> <index: INT> <targetvar: KEYWORD>`
Puts the desired item from an array into a variable <targetvar>.