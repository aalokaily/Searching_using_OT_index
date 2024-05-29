from suffix_trees import STree
from collections import defaultdict
import time
import math 
import sys
import bisect
 
def process_leaf_and_internal_nodes(tree):    
      
    setattr(tree, "number_leaf_nodes", 0)
    setattr(tree, "number_internal_nodes", 0)
    setattr(tree, "List_of_left_to_right_suffix_indexes", []) # List S in the paper with minor modification
    setattr(tree, "List_of_leaf_suffix_index_to_leaf_memory", []) # List M in the paper
        
    def preprocessing(tree):
        
        tree.List_of_leaf_suffix_index_to_leaf_memory = [-1] * len(tree.word)
        
        #iterative processing
        nodes_stack.append(tree.root)
        children_stack.append((list(tree.root.transition_links[x] for x in sorted(tree.root.transition_links.keys(), reverse=True))))
        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]                  
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                #iterative processing
                nodes_stack.append(last_node_under_top_node_in_stack)   # append it to process later with the required order (postorder) and remove it from OSHR[current_visited_node.key]
                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))
                                          
            else:
                setattr(current_visited_node, "OT_indexes", [])
                # alongside processing
                if current_visited_node.is_leaf():
                    # Assigning leaf nodes unique keys
                    current_visited_node.index_of_leaf_in_ST = tree.number_leaf_nodes                     
                    tree.number_leaf_nodes += 1
                    
                    # creating auxiliary lists 
                    tree.List_of_leaf_suffix_index_to_leaf_memory[current_visited_node.idx] = current_visited_node
                    tree.List_of_left_to_right_suffix_indexes.append(current_visited_node.idx)
                    
                    if not hasattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST", current_visited_node.index_of_leaf_in_ST)
                    elif current_visited_node.index_of_leaf_in_ST < current_visited_node.parent.index_of_leftmost_leaf_in_ST:
                        current_visited_node.parent.index_of_leftmost_leaf_in_ST = current_visited_node.index_of_leaf_in_ST
                    if not hasattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST", current_visited_node.index_of_leaf_in_ST)
                    elif current_visited_node.index_of_leaf_in_ST > current_visited_node.parent.index_of_rightmost_leaf_in_ST:
                        current_visited_node.parent.index_of_rightmost_leaf_in_ST = current_visited_node.index_of_leaf_in_ST
                        
                        
                else:
                    tree.number_internal_nodes += 1
                    tree.internal_niodes_list.append(current_visited_node)
                    if not hasattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST", current_visited_node.index_of_leftmost_leaf_in_ST)
                    elif current_visited_node.index_of_leftmost_leaf_in_ST < current_visited_node.parent.index_of_leftmost_leaf_in_ST:
                        current_visited_node.parent.index_of_leftmost_leaf_in_ST = current_visited_node.index_of_leftmost_leaf_in_ST
                    if not hasattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST", current_visited_node.index_of_rightmost_leaf_in_ST)
                    elif current_visited_node.index_of_rightmost_leaf_in_ST > current_visited_node.parent.index_of_rightmost_leaf_in_ST:
                        current_visited_node.parent.index_of_rightmost_leaf_in_ST = current_visited_node.index_of_rightmost_leaf_in_ST
                
                #iterative processing 
                nodes_stack.pop()
                children_stack.pop()
                
        print ("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
        print ("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
        print ("Number of alphabets in the input data", len(tree.root.transition_links) - 1)
    
    start = time.time()

    nodes_stack = []
    key_stack = []
    children_stack = []
    
    preprocessing(tree)
    print ("Processing leaf and internal nodes finished in ", round((time.time() - start), 5), "seconds")
    
  
######################################################################################## Searching code ##############################################################################################################
   
def find_end_node_of_exact_path_of_string_starting_from_a_node(tree, string, starting_node, suffix_end_node):          
    current_visited_node = starting_node
    end_node = starting_node
    i = 0
    l = len(string)
    d = starting_node.depth
    f = True
    
    while f:
        if i <= l - 1:
            if string[i] in current_visited_node.transition_links:
                end_node = current_visited_node.transition_links[string[i]]
                if end_node.is_leaf():
                    suffix_number_under_node = tree.List_of_leaf_suffix_index_to_leaf_memory[end_node.idx + starting_node.depth]
                    if suffix_end_node.index_of_leftmost_leaf_in_ST <= suffix_number_under_node.index_of_leaf_in_ST <= suffix_number_under_node.index_of_leaf_in_ST <= suffix_end_node.index_of_rightmost_leaf_in_ST:
                            return end_node
                    else:
                        return end_node.parent
                            
                else:
                    if end_node.depth - current_visited_node.depth == 1:
                        current_visited_node = end_node
                        i += 1
                    else:
                        if end_node.depth >= d + l:
                            edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + l + d]
                        else:
                            edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + end_node.depth]
                        
                        current_visited_node = end_node
                        for char in edge_label:
                            if string[i] == char:
                                i += 1
                            else:
                                f = False
                                break
            else:
                f = False
                break
        else:
            f = False
            break
            
    
    if i == l:
        return end_node
    else:#i must be then less than l
        if end_node.depth - starting_node.depth == i:     
            return end_node
        else:
            return end_node.parent
    
    
def find_end_node_of_exact_match_starting_from_root_node(tree, string):          
    current_visited_node = tree.root
    end_node = tree.root
    i = 0
    l = len(string)
    f = True
    
    while f:
        if i <= l - 1:
            if string[i] in current_visited_node.transition_links:
                end_node = current_visited_node.transition_links[string[i]]
                if end_node.depth >= l:
                    edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + l]
                else:
                    edge_label = tree.word[end_node.idx + current_visited_node.depth:end_node.idx + end_node.depth]
                
                current_visited_node = end_node
                for char in edge_label:
                    if string[i] == char:
                        i += 1
                    else:
                        f = False
                        break
            else:
                f = False
                break
        else:
            f = False
            break
            
    
    if i == l:
        return end_node
    else:#i must be then less than l
        if end_node.depth == i:     
            return end_node
        else:
            return end_node.parent
            
 


def start():
    start = time.time()
    
    input_file = sys.argv[1]    
    pattern = sys.argv[2]

    pattern_length = len(pattern)
    print ("Length of pattern -------- ", pattern_length)
    
    text = ""
    with open(input_file) as file_in:        
        for line in file_in:
            if line[0] != ">":
                text += line.strip()
                
    
    print ("Reading input data took", round((time.time() - start), 5), "seconds")   
    
    print ("------------------------------------------------------------------------------------------")
    start = time.time()     
    tree = STree.STree(text)
    
    length_of_alphabet = len(tree.root.transition_links) - 1
    length_threshold = 0
    print ("Length_threshold -------- ", length_threshold)
    
    
    sentinel_character  = tree.word[-1]
    print ("Building Suffix Tree took", round((time.time() - start), 5), "seconds")
    
    start = time.time()
   
    print ("------------------------------------------------------------------------------------------")
    setattr(tree, "internal_niodes_list", [])
    process_leaf_and_internal_nodes(tree)
    
    tree.word = tree.word[:-1]# this will removed the added sentinel_character from the text (word) so that it will not be included in the comparison and results finding
    
    print ("------------------------------------------------------------------------------------------")    
    print ("Testing index")
    
    nodes_by_depth_dict = defaultdict(list)
    for node in tree.internal_niodes_list:
        if node != tree.root:
            nodes_by_depth_dict[node.depth].append(node)
    
    patterns_dict = defaultdict(list)
    total_number_of_patterns_of_all_lengths = 0
    for pattern_length in [7, 10, 12, 15, 20, 25, 30, 35, 40, 50]:
        number_of_patterns = 0
        i = 0
        while True:
            i += 10
            nn = i * pattern_length
            if nn + pattern_length >= tree.number_leaf_nodes:
                break
            else:
                t = tree.word[nn:nn + pattern_length]
                end_node_of_pattern_from_root = find_end_node_of_exact_match_starting_from_root_node(tree, t)
                if end_node_of_pattern_from_root.is_leaf():
                    continue
                else:
                    patterns_dict[pattern_length].append((t, end_node_of_pattern_from_root))
                    total_number_of_patterns_of_all_lengths += 1
                    number_of_patterns += 1
                    if number_of_patterns == 100:
                        break
            
    for depth in range(1, 1001):
        start_time_for_searching_all_patterns_of_all_lengths = time.time()
        list_of_starting_nodes = nodes_by_depth_dict[depth][-1000:]
        Number_of_starting_nodes = len(list_of_starting_nodes)
        
        # compute complexity under all starting_nodes 
        number_of_child_internal_nodes_under_starting_nodes = 0
        number_of_child_leaf_nodes_under_starting_nodes = 0
        for starting_node in list_of_starting_nodes: 
            for node in starting_node.transition_links.values():
                if node.is_leaf():
                    number_of_child_leaf_nodes_under_starting_nodes += 1
                else:
                    number_of_child_internal_nodes_under_starting_nodes += 1
                    
        for pattern_length in sorted(patterns_dict.keys()):
            patterns = patterns_dict[pattern_length]
            start = time.time()
            for dat in patterns:
                pattern = dat[0]
                end_node_of_pattern_from_root = dat[1]
                
                for starting_node in list_of_starting_nodes: 
                    # check if the matching node is a direct child node of starting_node
                    matching_node_is_found = 0
                    if pattern[0] in starting_node.transition_links:
                        node = starting_node.transition_links[pattern[0]]
                        if node.depth >= pattern_length + starting_node.depth:
                            if node.is_leaf():
                                suffix_number_under_node = tree.List_of_leaf_suffix_index_to_leaf_memory[node.idx + starting_node.depth]
                                if suffix_number_under_node.index_of_leaf_in_ST  >= end_node_of_pattern_from_root.index_of_leftmost_leaf_in_ST and suffix_number_under_node.index_of_leaf_in_ST <= end_node_of_pattern_from_root.index_of_rightmost_leaf_in_ST:
                                    matching_node = node
                                    matching_node_is_found = 1
                            else:
                                tt = tree.List_of_left_to_right_suffix_indexes[node.index_of_leftmost_leaf_in_ST]
                                any_suffix_under_starting_node = tree.List_of_leaf_suffix_index_to_leaf_memory[tt + starting_node.depth]
                                if any_suffix_under_starting_node.index_of_leaf_in_ST  >= end_node_of_pattern_from_root.index_of_leftmost_leaf_in_ST and any_suffix_under_starting_node.index_of_leaf_in_ST <= end_node_of_pattern_from_root.index_of_rightmost_leaf_in_ST:
                                    matching_node = node
                                    matching_node_is_found = 1
                                    
                    
                                
                        
                    if matching_node_is_found == 0:
                        matching_node = find_end_node_of_exact_path_of_string_starting_from_a_node(tree, pattern, starting_node, end_node_of_pattern_from_root)
                        if matching_node.depth >= starting_node.depth + pattern_length:
                            matching_node_is_found = 1
         

                    if matching_node_is_found == 0:
                        print ("No matching node found") #print ("No matching node found", "for", pattern, "under node", starting_node)
                    else:
                        print ("Found matching node", matching_node) #print ("Found matching node", matching_node, "for", pattern, "under node", starting_node)
                               

             
            print ("Total time for searching for", len(patterns), "patterns of length", pattern_length, "starting from", Number_of_starting_nodes, "nodes out of ", len(nodes_by_depth_dict[depth]), "nodes at depth", depth, "with complexity of number_of_child_internal_nodes_under_starting_nodes", number_of_child_internal_nodes_under_starting_nodes, "and number_of_child_leaf_nodes_under_starting_nodes", number_of_child_leaf_nodes_under_starting_nodes, "is", round((time.time() - start), 5), "seconds") 
                
            
        print ("Total time for searching for", total_number_of_patterns_of_all_lengths, "of all lengths starting from", Number_of_starting_nodes, "nodes out of ", len(nodes_by_depth_dict[depth]), "nodes at depth", depth, "with complexity of number_of_child_internal_nodes_under_starting_nodes", number_of_child_internal_nodes_under_starting_nodes, "and number_of_child_leaf_nodes_under_starting_nodes", number_of_child_leaf_nodes_under_starting_nodes, "is", round(time.time() - start_time_for_searching_all_patterns_of_all_lengths, 5), "seconds")
        print ()
           
start()
