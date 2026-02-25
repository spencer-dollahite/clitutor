# Shell Scripting Basics

Shell scripts let you automate sequences of commands. Instead of typing the
same commands repeatedly, you write them into a file and execute it. This is
the foundation of automation, DevOps, and system administration.

## Your First Script

A shell script is just a text file containing commands. The first line should
be a **shebang** that tells the system which interpreter to use:

```bash
#!/bin/bash
# This is a comment
echo "Hello from a script!"
```

To run it:
```bash
chmod +x myscript.sh    # make it executable
./myscript.sh            # run it
```

Or without making it executable:
```bash
bash myscript.sh
```

<!-- exercise
id: ex01
title: Create and run a script
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: Hello from my script
hints:
  - "Create a script file with a shebang, add an echo command, make it executable, and run it."
  - "Use printf or echo with redirection to write the script, then chmod +x and ./script."
  - "Type: `printf '#!/bin/bash\\necho \"Hello from my script\"\\n' > hello.sh && chmod +x hello.sh && ./hello.sh`"
-->
### Exercise 1: Create and run a script
Create a script called `hello.sh` that prints `Hello from my script`, make it executable, and run it.

---

## Variables

Variables store values. No spaces around the `=` sign. Use `$VAR` or `${VAR}`
to reference a variable:

```bash
NAME="Alice"
echo "Hello, $NAME"
echo "Your home is ${HOME}"
```

**Special variables:**

| Variable | Meaning |
|----------|---------|
| `$0` | Script name |
| `$1`, `$2`, ... | Positional arguments |
| `$#` | Number of arguments |
| `$@` | All arguments (as separate words) |
| `$?` | Exit status of last command (0 = success) |
| `$$` | Process ID of the current script |

<!-- exercise
id: ex02
title: Script with variables
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "user is"
hints:
  - "Create a script that assigns a variable and prints it."
  - "Use VAR=value (no spaces around =), then echo $VAR."
  - "Type: `printf '#!/bin/bash\\nMYNAME=\"learner\"\\necho \"user is $MYNAME\"\\n' > vars.sh && bash vars.sh`"
-->
### Exercise 2: Script with variables
Create and run a script called `vars.sh` that sets a variable `MYNAME` and prints `user is <value>`.

---

## Conditionals -- `if` / `then` / `else`

```bash
if [[ condition ]]; then
    # commands if true
elif [[ other_condition ]]; then
    # commands if other is true
else
    # commands if nothing matched
fi
```

**Common test operators:**

| Operator | Meaning |
|----------|---------|
| `-f file` | True if file exists and is a regular file |
| `-d dir` | True if directory exists |
| `-z "$var"` | True if variable is empty |
| `-n "$var"` | True if variable is not empty |
| `"$a" == "$b"` | String equality |
| `"$a" != "$b"` | String inequality |
| `$a -eq $b` | Numeric equality |
| `$a -lt $b` | Numeric less than |
| `$a -gt $b` | Numeric greater than |

<!-- exercise
id: ex03
title: Conditional script
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: exists
hints:
  - "Write a script that checks if a file exists using the -f test."
  - "Use if [[ -f filename ]]; then echo exists; fi."
  - "Type: `printf '#!/bin/bash\\ntouch testfile\\nif [[ -f testfile ]]; then\\n  echo \"exists\"\\nelse\\n  echo \"missing\"\\nfi\\n' > check.sh && bash check.sh`"
-->
### Exercise 3: Conditional script
Write and run a script that creates a file called `testfile`, then checks if it exists and prints `exists` or `missing`.

---

## Loops -- `for` and `while`

### For loops

```bash
# Iterate over a list
for item in apple banana cherry; do
    echo "Fruit: $item"
done

# Iterate over files
for f in *.txt; do
    echo "Processing $f"
done

# C-style loop
for ((i=1; i<=5; i++)); do
    echo "Number $i"
done
```

### While loops

```bash
count=1
while [[ $count -le 5 ]]; do
    echo "Count: $count"
    ((count++))
done
```

<!-- exercise
id: ex04
title: For loop script
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: output_regex
expected: "(^|\\n)3\\s*(\\n|$)"
hints:
  - "Write a script with a for loop that iterates over numbers."
  - "Use: for i in 1 2 3; do echo $i; done."
  - "Type: `for i in 1 2 3; do echo $i; done`"
-->
### Exercise 4: For loop
Write a for loop that prints the numbers 1, 2, and 3 (each on its own line).

---

## Functions

Functions group related commands and can be called by name:

```bash
greet() {
    local name="$1"
    echo "Hello, $name!"
}

greet "Alice"
greet "Bob"
```

The `local` keyword limits a variable's scope to the function.

<!-- exercise
id: ex05
title: Write a function
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: "Hello, World"
hints:
  - "Define a function and call it."
  - "Use function_name() { commands; } syntax."
  - "Type: `greet() { echo \"Hello, $1\"; }; greet World`"
-->
### Exercise 5: Write a function
Define a function called `greet` that takes one argument and prints `Hello, <argument>`. Call it with `World`.

---

## Exit Codes

Every command returns an **exit code**: `0` means success, anything else means
failure. You can check it with `$?`:

```bash
ls /etc/passwd
echo $?    # 0 (success)

ls /nonexistent
echo $?    # 2 (failure)
```

Use `exit` in scripts to return a specific code:

```bash
if [[ ! -f required_file ]]; then
    echo "Error: required_file not found" >&2
    exit 1
fi
```

<!-- exercise
id: ex06
title: Check an exit code
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_equals
expected: "0"
hints:
  - "Run a successful command, then check the exit code."
  - "The special variable $? holds the exit code of the last command."
  - "Type: `true && echo $?`"
-->
### Exercise 6: Check an exit code
Run a command that succeeds (like `true`) and then print its exit code.

---

## Input -- `read`

The `read` command captures user input into a variable:

```bash
echo "What is your name?"
read name
echo "Hello, $name!"

# With a prompt
read -p "Enter your name: " name

# Silent input (for passwords)
read -sp "Password: " pass
```

<!-- exercise
id: ex07
title: Script with read using here-string
xp: 15
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: "You entered: test"
hints:
  - "Write a script that uses read and pipe input to it."
  - "Use echo to pipe input into a script that uses read."
  - "Type: `printf '#!/bin/bash\\nread val\\necho \"You entered: $val\"\\n' > reader.sh && echo test | bash reader.sh`"
-->
### Exercise 7: Script with read
Create a script that reads a value and prints `You entered: <value>`. Test it by piping `test` into it.

---

## Putting It Together -- A Real Script

Here is a practical example that combines multiple concepts:

```bash
#!/bin/bash
# backup.sh - Create a timestamped backup of a directory

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <directory>" >&2
    exit 1
fi

SOURCE="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP="${SOURCE}_backup_${TIMESTAMP}.tar.gz"

if [[ ! -d "$SOURCE" ]]; then
    echo "Error: '$SOURCE' is not a directory" >&2
    exit 1
fi

tar -czf "$BACKUP" "$SOURCE"
echo "Backup created: $BACKUP"
```

<!-- exercise
id: ex08
title: Write a counting script
xp: 25
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: "Total: 3"
hints:
  - "Create some files, then write a script that counts .txt files."
  - "Use a for loop with a counter variable, or use ls *.txt | wc -l."
  - "Type: `touch a.txt b.txt c.txt && printf '#!/bin/bash\\ncount=$(ls *.txt | wc -l)\\necho \"Total: $count\"\\n' > counter.sh && bash counter.sh`"
-->
### Exercise 8: Write a counting script
Create three `.txt` files, then write and run a script that counts them and prints `Total: <count>`.

---

## What You Learned

- **Shebang** (`#!/bin/bash`) -- tells the system which interpreter to use
- **Variables** -- assignment, special variables (`$1`, `$?`, `$#`, `$@`)
- **Conditionals** -- `if`/`elif`/`else`/`fi` with `[[ ]]` tests
- **Loops** -- `for` and `while` for iteration
- **Functions** -- define reusable blocks of commands
- **Exit codes** -- `$?` and `exit` for status reporting
- **`read`** -- capture input from the user
- **Combining concepts** -- building real automation scripts
