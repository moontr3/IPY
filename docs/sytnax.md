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

Anywhere between `FUNCTION` and `ENDFUNCTION` can be an `ARGS`..`ENDARGS` block. It it you describe all args on each line as follows `VARNAME TYPE`. You will be able to use `VARNAME` as a variable name. `TYPE` can be one of the following: `ANY`, `NULL`, `BOOL`, `INTEGER`, `FLOAT`, `STRING`.