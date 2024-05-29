# Searching for a pattern under any internal node in suffix trees

Pattern matching is a fundamental process in most scientific domains. The problem involves finding the starting positions of a given pattern (usually of short length) in a reference stream of data (of considerable length) as either exact or approximate (which allows for mismatches, insertions, or deletions) matching. For exact matching, several data structures built in linear time and space can be used in practice nowadays. The solutions proposed so far for approximate matching are non-linear, impractical, or heuristics. In this work, we propose an index that allows to find any pattern under any internal node in suffix trees in logn time. 

------------------------------------------------------------- Prerequisite ---------------------------------------------------------------
* Install bisect library from https://docs.python.org/3/library/bisect.html 

* Install the following library that will be used to build suffix trees:
https://github.com/ptrus/suffix-trees 

Then edit ./suffix_trees/STree.py as the followings:

- comment the following line, line 249, by inserting the character "#" at the beginning of the line. This will allow setting attributes to the suffix tree more freely.
```python
__slots__ = ['_suffix_link', 'transition_links', 'idx', 'depth', 'parent', 'generalized_idxs']
```

- In some procedures, we hashed internal nodes of suffix tree, to optimize this hashing we used only the combination of node index and node depth to identify uniquely an internal node instead of the original identification/naming of the nodes given by the library which is a bit long (shorter identification will use less space and speed up the lookup process for the hashed nodes). So replace the following two lines (which are line 264 and 265) 
```python
return ("SNode: idx:" + str(self.idx) + " depth:" + str(self.depth) +
                " transitons:" + str(list(self.transition_links.keys())))
```
with the line:
```python
return (str(self.idx) + "-" + str(self.depth))
```

------------------------------------------------------------- Preparation ----------------------------------------------------------------

Firstly, you need to convert the genome in fasta format to a one-line genome. This converting removes any non A, C, G, T, and N (case is sensitive) and headers from the FASTA file. This can be done using the script filter_DNA_file_to_4_bases_and_N.py by running the command:

```python
python3 convert_fasta_file_to_one_line_file $file.fasta > converted_fasta_file.oneline
```
----------------------------------------------------------- Running algorithms -----------------------------------------------------------

The input for the tools is the converted fasta file. These tools are applicable for Hamming distance and Wildcards matching. Edit distance to be implemented.  

Running command:
```python
python3 Finding_base_suffixes.py converted_fasta_file.oneline
```
