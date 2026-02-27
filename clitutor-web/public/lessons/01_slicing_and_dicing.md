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
cat auth.log | grep "failure" | wc -l
```

This reads a log file, filters for lines containing "failure", and counts them.

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
title: View the first 3 callsigns
xp: 10
difficulty: 1
sandbox_setup:
  - "printf 'BRAVO\nCHARLIE\nDELTA\nECHO\nFOXTROT\n' > callsigns.txt"
validation_type: output_contains
expected: DELTA
hints:
  - "Use the command that shows the beginning of a file."
  - "head with -n to specify number of lines."
  - "Type: `head -n 3 callsigns.txt`"
-->
### Exercise 1: View the first 3 callsigns
Display only the first 3 lines of `callsigns.txt`.

---

## `grep` -- Search for Patterns

`grep` searches for lines matching a pattern. It is one of the most frequently
used commands in the entire Linux ecosystem.

```bash
grep "DROP" firewall.log          # lines containing 'DROP'
grep -i "error" logfile.txt       # case-insensitive
grep -c "DROP" firewall.log       # count matching lines
grep -n "ACCEPT" firewall.log     # show line numbers
grep -v "ACCEPT" firewall.log     # invert: lines NOT matching
grep -r "TODO" src/               # recursive search in a directory
```

<!-- exercise
id: ex02
title: Grep for dropped packets
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'ACCEPT 192.168.1.10 TCP/443\\nDROP 203.0.113.45 TCP/22\\nACCEPT 10.0.0.5 TCP/80\\nDROP 198.51.100.77 TCP/23\\nACCEPT 172.16.0.1 TCP/443\\nACCEPT 192.168.1.10 TCP/8080\\n' > firewall.log"
validation_type: output_contains
expected: DROP
hints:
  - "Use grep to search for a pattern in the file."
  - "The pattern you are looking for is 'DROP'."
  - "Type: `grep 'DROP' firewall.log`"
-->
### Exercise 2: Grep for dropped packets
Search `firewall.log` for all lines where packets were dropped (`DROP`).

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
title: Count watch station assignments
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'bridge\nCIC\nengineering\nbridge\nCIC\nbridge\nmedical\n' > watch_stations.txt"
validation_type: output_contains
expected: "3 bridge"
hints:
  - "You need to sort the file, remove duplicates, and count them."
  - "Pipe sort into uniq -c to count occurrences."
  - "Type: `sort watch_stations.txt | uniq -c`"
-->
### Exercise 3: Count watch station assignments
Sort `watch_stations.txt` and count how many times each station appears.

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
title: Extract crew member usernames
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'root:x:0:0:root:/root:/bin/bash\\nlcdr_thompson:x:1001:1001:LCDR Thompson:/home/lcdr_thompson:/bin/bash\\nens_rodriguez:x:1002:1002:ENS Rodriguez:/home/ens_rodriguez:/bin/bash\\n' > crew.txt"
validation_type: output_contains
expected: lcdr_thompson
hints:
  - "Use cut to extract a specific field from a delimited file."
  - "The delimiter is a colon and you want the first field."
  - "Type: `cut -d':' -f1 crew.txt`"
-->
### Exercise 4: Extract crew member usernames
Extract just the usernames (first field) from the colon-delimited `crew.txt`.

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
title: Count incident log entries
xp: 10
difficulty: 1
sandbox_setup:
  - "printf '0800 Unauthorized access attempt detected\n0815 Port scan from 203.0.113.5\n0900 Firewall rule updated\n0930 VPN tunnel established\n1000 IDS alert: brute force\n1045 Patch applied to web server\n1100 Security audit completed\n' > incident_log.txt"
validation_type: output_contains
expected: "7"
hints:
  - "Use the wc command with a flag that limits output to line count."
  - "The flag for lines only is -l."
  - "Type: `wc -l incident_log.txt`"
-->
### Exercise 5: Count incident log entries
Count the number of entries in `incident_log.txt`.

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
title: Update server address in config
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'syslog_server=192.168.1.100\nalert_target=192.168.1.100\nbackup_log=192.168.1.100\n' > log_config.txt"
validation_type: output_contains
expected: 10.50.1.200
hints:
  - "Use sed to substitute one string for another."
  - "The syntax is sed 's/pattern/replacement/g'."
  - "Type: `sed 's/192.168.1.100/10.50.1.200/g' log_config.txt`"
-->
### Exercise 6: Update server address in config
The log server has moved. Replace the old IP `192.168.1.100` with `10.50.1.200` across all entries in `log_config.txt` (output to stdout).

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
title: Find the configuration change
xp: 15
difficulty: 2
sandbox_setup:
  - "printf 'ACCEPT TCP/443 0.0.0.0/0\nACCEPT TCP/80 0.0.0.0/0\nDROP TCP/22 0.0.0.0/0\n' > config_baseline.txt"
  - "printf 'ACCEPT TCP/443 0.0.0.0/0\nACCEPT TCP/8080 0.0.0.0/0\nDROP TCP/22 0.0.0.0/0\n' > config_current.txt"
validation_type: output_contains
expected: "TCP/80"
hints:
  - "Use the command that compares two files."
  - "diff shows what changed between two files."
  - "Type: `diff config_baseline.txt config_current.txt`"
-->
### Exercise 7: Find the configuration change
Compare `config_baseline.txt` and `config_current.txt` to find what firewall rule changed.

---

## Putting It All Together -- Pipelines

The beauty of these tools is chaining them into pipelines. Here is a real-world
example analyzing an authentication log:

```bash
cat auth.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -n 5
```

This extracts IP addresses (field 1), counts unique ones, and shows the top 5
most frequent sources of authentication attempts.

<!-- exercise
id: ex08
title: Top source IP from auth log
xp: 25
difficulty: 3
sandbox_setup:
  - "printf '192.168.1.1 sshd auth failure\n10.0.0.5 sshd auth success\n192.168.1.1 sshd auth failure\n10.0.0.5 sshd auth success\n192.168.1.1 sshd auth failure\n172.16.0.1 sshd auth success\n' > auth.log"
validation_type: output_contains
expected: 192.168.1.1
hints:
  - "Extract the first field (IP address), sort, count unique values, and sort numerically."
  - "Use cut -d' ' -f1 to get IPs, then sort | uniq -c | sort -rn."
  - "Type: `cut -d' ' -f1 auth.log | sort | uniq -c | sort -rn | head -n 1`"
-->
### Exercise 8: Top source IP from auth log
Find the most frequently occurring IP address in `auth.log` by building a pipeline.

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
