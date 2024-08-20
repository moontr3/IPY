# IPYP Syntax

### Basic writing style
Each command is executed in order. The commands should be separated by semicolons `;`, newlines are ignored.

To start a comment, use an equal sign `=`. Everyting after the `=` on the current line will be counted as a comment and therefore ignored by the compiler.

Indentation is entirely optional. Each command that requires an indentation has an ending command, usually the same command but with `END` at the beginning. For example, everyting between `FUNCTION TEST;` and `ENDFUNCTION;` will be counted as code of the function named `TEST` and will be run upon calling `CALL TEST;`.<br>
Any code cannot be indented twice with this kind of syntax. Because I want you to suffer alright. That's why I made this bullcrap.


### Syntax

Each command can take several arguments. The arguments are separated by spaces.
A string - list of characters (including spaces) inbetween quotes `"` - or a function call - a function name and arguments separated by spaces inbetween dollar signs `$` - are not split up into different arguments.<br>
For example, a string `NOOP;` is interpreted as a command `NOOP` with no arguments;<br>
a string `LOG X;` is interpreted as a command `LOG` with a single argument - in this case, a variable `X`;<br>
a string `CALL FUNC "YOUR STRING" $GETSUM X 10$;` is interpreted as a command `CALL` with 3 arguments - a function name `FUNC`, a string `YOUR STRING` and a function call `GETSUM X 10`, which calls a function `GETSUM` that in theory sums the variable `X` and a number `10`. But we don't know that. Maybe someone named a substraction function like that.

Strings, as briefly explained above, are lists of characters that cannot include newlines for some reason. Yeah I want you to suffer.

Function calls on the other hand are much more important - they call a custom function defined with the `FUNCTION` command and pass in the arguments. <i>Note that this doesn't include system commands, so you can't just write something like `$SUM X 10$` and go on with your day.</i>


### Functions

Custom functions are defined using the command `FUNCTION functionname;`. Everything inbetwen this command and a next `ENDFUNCTION;` is considered a body of the function and will be run when the function is called.

Anywhere between `FUNCTION` and `ENDFUNCTION` can be an `ARGS`..`ENDARGS` block. It it you describe all args on each line as follows `VARNAME TYPE`. You will be able to use `*VARNAME` as a variable name (Note that `*VARIABLE` is immutable, so you'd need to clone it to another variable like this `ASSIGN VARIABLE *VARIABLE`). `TYPE` can be one of the following: `ANY`, `NULL`, `BOOL`, `INTEGER`, `FLOAT`, `STRING`.

To call a function, you can use `CALL <FUNCTIONNAME>`, where `FUNCTIONNAME` is the name of your function.

If you want to use the return value of the function somewhere, you need to wrap the function name and all args separated by spaces in dollar signs, like this: `$GETSUM X 10$`


### Loop

To actually run your program, you need to have a `LOOP`..`ENDLOOP` block in your code. In this block you need to put code that will run X amount of times per second. To set this X value, you need to use a `SETFPS` command somewhere before the `LOOP`. Also you'll need to set window resolution using `SETRES x y`, or the code won't run.

To erase everything from the window, use `FILL r g b` with your desired RGB color.

More about window commands [here](docs/commands.md)


### Sprites

The only thing you can draw in this engine is predefined sprites that should be stored in a `.ipys` file.

First you'll need to create a palette via a `=PALETTE` command. It accepts 4 arguments separated by spaces - a symbol and 3 RGB values. You can also add a `=BLANK` command with 3 RGB values. This color will be used as transparent within the spritesheet.

After declaring your palette, you'll need to create the images themselves. This can be done with the `=IMAGE` command. It accepts 3 arguments - a name, width and height.

After the `=IMAGE` command you'll need to put your image line-by-line. Each symbol in a line will become a color defined by the `=PALETTE` command with the same symbol.

Here's an example file for a snake game I was making:

```
=PALETTE . 0 0 0
=PALETTE # 255 255 255
=PALETTE @ 128 128 128
=PALETTE % 255 0 0
=PALETTE * 50 50 0
=BLANK 0 0 0

=IMAGE HEAD 8 8
########
########
########
########
########
########
########
########

=IMAGE TAIL 8 8
........
.@@@@@@.
.@@@@@@.
.@@@@@@.
.@@@@@@.
.@@@@@@.
.@@@@@@.
........

=IMAGE FOOD 8 8
....*...
...*....
.%%**%%.
%@@%%%%%
%@%%%%%%
.%%%%%%.
.%%%%%%.
..%..%..
```


### Input

_Not yet implemented. Because the engine is shit._