# Slicing and Dicing

The real power of the command line comes from processing text. Linux treats
almost everything as a text stream, and a rich set of tools lets you slice,
filter, sort, and transform that data. This lesson covers the essential text
processing commands.

## The Pipe -- `|`

The **pipe** operator `|` sends the output (stdout) of one command as the input
(stdin) of the next. Chaining commands together like this is one of the most
powerful concepts in the shell.

```bash
cat access.log | grep "404" | wc -l
```

This reads a log file, filters for lines containing "404", and counts them.

---

## `head` and `tail`

These commands show the beginning or end of a file:

```bash
head -n 5 file.txt    # first 5 lines
tail -n 5 file.txt    # last 5 lines
tail -f /var/log/syslog  # follow a log in real time (Ctrl+C to stop)
```

<!-- exercise
id: ex01
title: View the first 3 lines
xp: 10
difficulty: 1
sandbox_setup:
  - "printf 'alpha\nbeta\ngamma\ndelta\nepsilon\n' > words.txt"
validation_type: output_contains
expected: gamma
hints:
  - "Use the command that shows the beginning of a file."
  - "head with -n to specify number of lines."
  - "Type: `head -n 3 words.txt`"
-->
### Exercise 1: View the first 3 lines
Display only the first 3 lines of `words.txt`.

---

## `grep` -- Search for Patterns

`grep` searches for lines matching a pattern. It is one of the most frequently
used commands in the entire Linux ecosystem.

```bash
grep "error" logfile.txt          # lines containing 'error'
grep -i "error" logfile.txt       # case-insensitive
grep -c "error" logfile.txt       # count matching lines
grep -n "error" logfile.txt       # show line numbers
grep -v "error" logfile.txt       # invert: lines NOT matching
grep -r "TODO" src/               # recursive search in a directory
```

<!-- exercise
id: ex02
title: Grep for 404 errors
xp: 15
difficulty: 2
sandbox_setup:
  - "printf '200 OK\\n404 Not Found\\n200 OK\\n500 Error\\n404 Not Found\\n301 Redirect\\n' > status.log"
validation_type: output_contains
expected: 404 Not Found
hints:
  - "Use grep to search for a pattern in the file."
  - "The pattern you are looking for is '404'."
  - "Type: `grep '404' status.log`"
-->
### Exercise 2: Grep for 404 errors
Search `status.log` for all lines containing `404`.

---

## `sort` and `uniq`

`sort` arranges lines alphabetically (or numerically with `-n`). `uniq` removes
**adjacent** duplicate lines, which is why you almost always sort first.

```bash
sort names.txt                    # alphabetical sort
sort -n numbers.txt               # numeric sort
sort -r names.txt                 # reverse sort
sort names.txt | uniq             # remove duplicates
sort names.txt | uniq -c          # count occurrences
sort names.txt | uniq -c | sort -rn  # rank by frequency
```

<!-- exercise
id: ex03
title: Count unique fruits
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'apple\\nbanana\\napple\\ncherry\\nbanana\\napple\\ndate\\n' > fruits.txt"
validation_type: output_contains
expected: "3 apple"
hints:
  - "You need to sort the file, remove duplicates, and count them."
  - "Pipe sort into uniq -c to count occurrences."
  - "Type: `sort fruits.txt | uniq -c`"
-->
### Exercise 3: Count unique fruits
Sort `fruits.txt` and count how many times each fruit appears.

---

## `cut` -- Extract Columns

`cut` pulls out specific fields from structured text.

```bash
cut -d',' -f1 data.csv           # first field, comma-delimited
cut -d':' -f1,3 /etc/passwd      # fields 1 and 3, colon-delimited
cut -c1-10 file.txt              # characters 1 through 10
```

<!-- exercise
id: ex04
title: Extract usernames from passwd format
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'root:x:0:0:root:/root:/bin/bash\\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\\n' > users.txt"
validation_type: output_contains
expected: www-data
hints:
  - "Use cut to extract a specific field from a delimited file."
  - "The delimiter is a colon and you want the first field."
  - "Type: `cut -d':' -f1 users.txt`"
-->
### Exercise 4: Extract usernames
Extract just the usernames (first field) from the colon-delimited `users.txt`.

---

## `wc` -- Word Count

`wc` counts lines, words, and characters:

```bash
wc file.txt            # lines, words, characters
wc -l file.txt         # lines only
wc -w file.txt         # words only
cat a.log b.log | wc -l   # count combined lines from two files
```

<!-- exercise
id: ex05
title: Count lines in a file
xp: 10
difficulty: 1
sandbox_setup:
  - "printf 'line1\\nline2\\nline3\\nline4\\nline5\\nline6\\nline7\\n' > data.txt"
validation_type: output_contains
expected: "7"
hints:
  - "Use the wc command with a flag that limits output to line count."
  - "The flag for lines only is -l."
  - "Type: `wc -l data.txt`"
-->
### Exercise 5: Count lines
Count the number of lines in `data.txt`.

---

## `sed` -- Stream Editor

`sed` performs text transformations. The most common operation is
search-and-replace:

```bash
sed 's/old/new/' file.txt         # replace first occurrence per line
sed 's/old/new/g' file.txt        # replace ALL occurrences (global)
sed -i 's/old/new/g' file.txt     # edit the file in-place
sed '3d' file.txt                 # delete line 3
sed -n '2,4p' file.txt            # print only lines 2-4
```

<!-- exercise
id: ex06
title: Replace text with sed
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'Hello World\\nHello Linux\\nHello CLI\\n' > greetings.txt"
validation_type: output_contains
expected: Hi CLI
hints:
  - "Use sed to substitute one string for another."
  - "The syntax is sed 's/pattern/replacement/g'."
  - "Type: `sed 's/Hello/Hi/g' greetings.txt`"
-->
### Exercise 6: Replace text with sed
Replace every occurrence of `Hello` with `Hi` in `greetings.txt` (output to stdout).

---

## `diff` -- Compare Files

`diff` shows the differences between two files line by line.

```bash
diff file1.txt file2.txt          # show differences
diff -u file1.txt file2.txt       # unified format (like git diff)
diff -y file1.txt file2.txt       # side-by-side comparison
```

<!-- exercise
id: ex07
title: Find the difference
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'red\\ngreen\\nblue\\n' > colors1.txt"
  - "printf 'red\\nyellow\\nblue\\n' > colors2.txt"
validation_type: output_contains
expected: green
hints:
  - "Use the command that compares two files."
  - "diff shows what changed between two files."
  - "Type: `diff colors1.txt colors2.txt`"
-->
### Exercise 7: Find the difference
Compare `colors1.txt` and `colors2.txt` to find what changed.

---

## Putting It All Together -- Pipelines

The beauty of these tools is chaining them into pipelines. Here is a real-world
example analyzing a web server log:

```bash
cat access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -n 5
```

This extracts IP addresses (field 1), counts unique ones, and shows the top 5
most frequent visitors.

<!-- exercise
id: ex08
title: Top IP address from a log
xp: 25
difficulty: 3
sandbox_setup:
  - "printf '192.168.1.1 GET /index.html 200\\n10.0.0.5 GET /about.html 200\\n192.168.1.1 GET /style.css 200\\n10.0.0.5 GET /contact.html 200\\n192.168.1.1 GET /api/data 200\\n172.16.0.1 GET /index.html 200\\n' > access.log"
validation_type: output_contains
expected: 192.168.1.1
hints:
  - "Extract the first field (IP address), sort, count unique values, and sort numerically."
  - "Use cut -d' ' -f1 to get IPs, then sort | uniq -c | sort -rn."
  - "Type: `cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head -n 1`"
-->
### Exercise 8: Top IP address from a log
Find the most frequently occurring IP address in `access.log` by building a pipeline.

---

## What You Learned

- **`head`** / **`tail`** -- view the start or end of files
- **`grep`** -- search for patterns in text
- **`sort`** / **`uniq`** -- sort lines and remove or count duplicates
- **`cut`** -- extract specific fields or columns
- **`wc`** -- count lines, words, and characters
- **`sed`** -- stream editing and search-and-replace
- **`diff`** -- compare files
- **`|`** (pipe) -- chain commands into powerful pipelines

These are the bread and butter of log analysis, data processing, and quick text
manipulation from the command line.
