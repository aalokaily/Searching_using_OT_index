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
                        setattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST", current_visited_node.index_of_leaf_in_ST )
                    elif current_visited_node.index_of_leaf_in_ST < current_visited_node.parent.index_of_leftmost_leaf_in_ST:
                        current_visited_node.parent.index_of_leftmost_leaf_in_ST = current_visited_node.index_of_leaf_in_ST 
                    if not hasattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST", current_visited_node.index_of_leaf_in_ST )
                    elif current_visited_node.index_of_leaf_in_ST > current_visited_node.parent.index_of_rightmost_leaf_in_ST:
                        current_visited_node.parent.index_of_rightmost_leaf_in_ST = current_visited_node.index_of_leaf_in_ST 
                    
                    # computing leaf_node_to_use_in_upward_walk
                    parent_node = current_visited_node.parent
                    if not hasattr(parent_node, "leaf_node_to_use_in_upward_walk"):
                        setattr(parent_node, "leaf_node_to_use_in_upward_walk", current_visited_node)
                    elif current_visited_node.idx > parent_node.leaf_node_to_use_in_upward_walk.idx: #which means shorter edge 
                        parent_node.leaf_node_to_use_in_upward_walk = current_visited_node
                else:
                    tree.number_internal_nodes += 1
                    tree.internal_niodes_list.append(current_visited_node)
                    setattr(current_visited_node, "List_of_base_suffixes_derived_from_reference_leaf_nodes", []) # to be used in latter phases
                    setattr(current_visited_node, "List_of_base_suffixes_derived_from_reference_internal_nodes", []) # to be used in latter phases
                    
                    # build List_of_nodes_suffix_linked_to_me
                    if current_visited_node._suffix_link is not None and current_visited_node != tree.root:
                        temp = current_visited_node._suffix_link
                        if not hasattr(temp, "List_of_nodes_suffix_linked_to_me"):
                            setattr(temp, "List_of_nodes_suffix_linked_to_me", [])
                        temp.List_of_nodes_suffix_linked_to_me.append(current_visited_node)
                    
                    # build List_of_reference_internal_nodes
                    top_node = current_visited_node.parent._suffix_link 
                    bottom_node = current_visited_node._suffix_link.parent
                    if bottom_node != top_node:
                        temp = bottom_node
                        while temp  != top_node: 
                            if not hasattr(temp, "List_of_reference_internal_nodes"):
                                setattr(temp, "List_of_reference_internal_nodes", [])
                            temp.List_of_reference_internal_nodes.append(current_visited_node)
                            temp = temp.parent
                            
                    # build index_of_leftmost_leaf_in_ST and index_of_rightmost_leaf_in_ST variables
                    if not hasattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_leftmost_leaf_in_ST", current_visited_node.index_of_leftmost_leaf_in_ST)
                    elif current_visited_node.index_of_leftmost_leaf_in_ST < current_visited_node.parent.index_of_leftmost_leaf_in_ST:
                        current_visited_node.parent.index_of_leftmost_leaf_in_ST = current_visited_node.index_of_leftmost_leaf_in_ST
                    if not hasattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST"):
                        setattr(current_visited_node.parent, "index_of_rightmost_leaf_in_ST", current_visited_node.index_of_rightmost_leaf_in_ST)
                    elif current_visited_node.index_of_rightmost_leaf_in_ST > current_visited_node.parent.index_of_rightmost_leaf_in_ST:
                        current_visited_node.parent.index_of_rightmost_leaf_in_ST = current_visited_node.index_of_rightmost_leaf_in_ST
                
                    
                    # computing leaf_node_to_use_in_upward_walk
                    parent_node = current_visited_node.parent
                    if not hasattr(parent_node, "leaf_node_to_use_in_upward_walk"):
                        setattr(parent_node, "leaf_node_to_use_in_upward_walk", current_visited_node)
                    elif parent_node.leaf_node_to_use_in_upward_walk.parent != parent_node: # this to priotrize direct leaf nodes than leaf nodes under child internal nodes as they are direct leaf nodes are better to be used
                        if current_visited_node.idx > parent_node.leaf_node_to_use_in_upward_walk.idx: #which means shorter edge 
                            parent_node.leaf_node_to_use_in_upward_walk = current_visited_node
                        
                        
                #iterative processing 
                nodes_stack.pop()
                children_stack.pop()
                
        print ("Number of leaf nodes is", "{:,}".format(tree.number_leaf_nodes))
        print ("Number of internal nodes is", "{:,}".format(tree.number_internal_nodes))
        print ("Number of alphabets in the input data", len(tree.root.transition_links) - 1)
        print ("Leftmost and rightmost keys of leaf nodes in ST of root node", (tree.root.index_of_leftmost_leaf_in_ST, "{:,}".format(tree.root.index_of_rightmost_leaf_in_ST)))
            
    start = time.time()
    nodes_stack = []
    key_stack = []
    children_stack = []
    
    preprocessing(tree)
    print ("Processing leaf and internal nodes finished in ", round((time.time() - start), 5), "seconds\n")
    
   
    
def Build_OT_index(tree):
   
    def phase_1_for_OT_indexing_of_base_paths  (tree):
        # find base suffixes
        nodes_stack.append(tree.root)
        children_stack.append((list(tree.root.transition_links[x] for x in sorted(tree.root.transition_links.keys(), reverse=True))))       
        cost = 0
        number_of_base_suffixes_derived_from_reference_leaf_node = 0
        number_of_base_suffixes_derived_from_reference_internal_node = 0
                        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]                  
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                nodes_stack.append(last_node_under_top_node_in_stack)  

                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))                                          
            else:
                nodes_stack.pop()
                children_stack.pop()

                # alongside processing
                if current_visited_node.is_leaf():
                    if current_visited_node.idx + 1 < tree.number_leaf_nodes:
                        # this code computes base suffixes derved from reference leaf nodes if any. We did not create reference leaf nodes explicity as they will be not used often (unlike reference_internal_nodes). 
                        leaf_node_of_next_suffix_index = tree.List_of_leaf_suffix_index_to_leaf_memory[current_visited_node.idx + 1]                                    
                        if leaf_node_of_next_suffix_index.parent != current_visited_node.parent._suffix_link:
                            temp = leaf_node_of_next_suffix_index.parent
                            end_node = current_visited_node.parent._suffix_link
                            while True:
                                if temp == end_node:
                                    if current_visited_node.parent == tree.root: # if so, then we must add this suffix as a base suffix to end_node unlike other cases (end_node must be tree.root)
                                        temp.List_of_base_suffixes_derived_from_reference_leaf_nodes.append(leaf_node_of_next_suffix_index.idx + temp.depth) 
                                        number_of_base_suffixes_derived_from_reference_leaf_node += 1 
                                    break
                                        
                                else:
                                    temp.List_of_base_suffixes_derived_from_reference_leaf_nodes.append(leaf_node_of_next_suffix_index.idx + temp.depth)
                                    number_of_base_suffixes_derived_from_reference_leaf_node += 1
                                
                                    # record Hanadi and Srivastava nodes to be colleted linearly from left to right in next phase
                                    if hasattr(temp, "List_of_nodes_suffix_linked_to_me"):
                                        if not hasattr(current_visited_node, "List_of_Hanadi_nodes"):    
                                            setattr(current_visited_node, "List_of_Hanadi_nodes", [])
                                        current_visited_node.List_of_Hanadi_nodes.append(temp)
                                    else:
                                        if hasattr(temp, "List_of_reference_internal_nodes"): # this means the node will have unempty List_of_base_suffixes_derived_from_reference_internal_nodes (this list by now however has not been computed)
                                            if not hasattr(current_visited_node, "List_of_Srivastava_nodes"): 
                                                setattr(current_visited_node, "List_of_Srivastava_nodes", [])
                                            current_visited_node.List_of_Srivastava_nodes.append(temp)
                                    
                                    temp = temp.parent

                                            
                else:
                    #collect base suffixes derived from reference internal nodes if any
                    if hasattr(current_visited_node, "List_of_reference_internal_nodes"):
                        for reference_internal_node in current_visited_node.List_of_reference_internal_nodes:
                            for leaf_node_index in tree.List_of_left_to_right_suffix_indexes[reference_internal_node.index_of_leftmost_leaf_in_ST:reference_internal_node.index_of_rightmost_leaf_in_ST + 1]:
                                current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes.append(leaf_node_index + 1 + current_visited_node.depth)
                                number_of_base_suffixes_derived_from_reference_internal_node += 1
                                cost += 1
                                

        # compute the case for suffix 0 as there is no previous index for index 0 
        temp = tree.List_of_leaf_suffix_index_to_leaf_memory[0]                                     
        while temp != tree.root:
            temp = temp.parent
            temp.List_of_base_suffixes_derived_from_reference_leaf_nodes.append(0 + temp.depth)
            number_of_base_suffixes_derived_from_reference_leaf_node += 1
            cost += 1
                
        # this a special cases and for the root only. The suffix-link of child internal node of a root usually link to the root. In case not, 
        # then the node that the child internal node link to must be bottom-node for the root node.
        current_visited_node = tree.root
        for node in current_visited_node.transition_links.values():
            if node.is_leaf():
                if node.idx + 1 < tree.number_leaf_nodes:
                    leaf_node_of_next_suffix_index = tree.List_of_leaf_suffix_index_to_leaf_memory[node.idx + 1]
                    if leaf_node_of_next_suffix_index.parent == tree.root:
                        current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes.append(leaf_node_of_next_suffix_index.idx)
                        cost += 1
            else:
                if node._suffix_link != tree.root:
                    for leaf_node_index in tree.List_of_left_to_right_suffix_indexes[node.index_of_leftmost_leaf_in_ST:node.index_of_rightmost_leaf_in_ST + 1]:
                        current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes.append(leaf_node_index + 1)
                        cost += 1           
        
        print ("Finding base suffixes took time of", "{:,}".format(cost))
        print ("Number_of_base_suffixes_derived_from_reference_leaf_node", "{:,}".format(number_of_base_suffixes_derived_from_reference_leaf_node))
        print ("Number_of_base_suffixes_derived_from_reference_internal_node", "{:,}".format(number_of_base_suffixes_derived_from_reference_internal_node))
        print ("Total number of base suffixes (except root node)", "{:,}".format(number_of_base_suffixes_derived_from_reference_leaf_node + number_of_base_suffixes_derived_from_reference_internal_node))

        

    nodes_stack = []
    children_stack = []
    start = time.time()
    phase_1_for_OT_indexing_of_base_paths(tree)
    print ("***** Phase 1 finished in", round((time.time() - start), 5), "seconds\n")


    def phase_2_for_OT_indexing_of_base_paths(tree):
        #index OSHR nodes under ST internal nodes and index inbetween top base nodes
        setattr(tree, "List_of_OSHR_leaf_nodes_from_left_to_right", []) 
        setattr(tree, "List_of_reference_nodes_for_Hanadi_nodes_from_left_to_right", [])
        setattr(tree, "List_of_reference_nodes_for_Srivastava_nodes_from_left_to_right", [])
        

        OSHR_leaf_nodes_key_counter = 0
        OSHR_internal_nodes_key_counter = 0
        reference_nodes_for_Hanadi_nodes_key_counter = 0
        reference_nodes_for_Srivastava_nodes_key_counter = 0
        
        min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes = 1
        max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes = 0
        total_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes = 0
        
        min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes = 1
        max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes = 0
        total_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes = 0
        
        sum_of_unique_inbetween_nodes_between_internal_nodes = 0
        sum_of_non_unique_inbetween_nodes_between_internal_nodes = 0
        min_length_of_List_of_reference_internal_nodess = 10000000000
        max_length_of_List_of_reference_internal_nodess = 0
        
        a1, a2, a3, a4, b1, b2, b3, b4 = 0, 0, 0, 0, 0, 0, 0, 0 
        
        #iterative processing
        nodes_stack.append(tree.root)
        OSHR_leaf_nodes_counter_stack.append(0)
        reference_nodes_for_Hanadi_nodes_counter_stack.append(0)
        reference_nodes_for_Srivastava_nodes_counter_stack.append(0)
        
        children_stack.append((list(tree.root.transition_links[x] for x in sorted(tree.root.transition_links.keys(), reverse=True))))
        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]                
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                #iterative processing
                nodes_stack.append(last_node_under_top_node_in_stack)     # append it to process later with the required order (postorder) and remove it from OSHR[current_visited_node.key]
                OSHR_leaf_nodes_counter_stack.append(OSHR_leaf_nodes_key_counter)
                reference_nodes_for_Hanadi_nodes_counter_stack.append(reference_nodes_for_Hanadi_nodes_key_counter)
                reference_nodes_for_Srivastava_nodes_counter_stack.append(reference_nodes_for_Srivastava_nodes_key_counter)
                
                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))
            else:
                # alongside processing
                #find and mark inbetween top base node and assign the reference nodes for this node (which are as coded below)
                if current_visited_node.is_leaf():
                    if hasattr(current_visited_node, "List_of_Hanadi_nodes"):
                        tree.List_of_reference_nodes_for_Hanadi_nodes_from_left_to_right.append(current_visited_node)
                        reference_nodes_for_Hanadi_nodes_key_counter += 1
                        
                    if hasattr(current_visited_node, "List_of_Srivastava_nodes"):
                        tree.List_of_reference_nodes_for_Srivastava_nodes_from_left_to_right.append(current_visited_node)
                        reference_nodes_for_Srivastava_nodes_key_counter += 1
                            
                else:
                    # index OSHR leaf and OSHR internal nodes under ST internal nodes    
                    setattr(current_visited_node, "index_of_leftmost_OSHR_leaf", OSHR_leaf_nodes_counter_stack[-1])
                    setattr(current_visited_node, "index_of_rightmost_OSHR_leaf", OSHR_leaf_nodes_key_counter - 1)
                
                    setattr(current_visited_node, "index_of_leftmost_reference_nodes_for_Hanadi_nodes", reference_nodes_for_Hanadi_nodes_counter_stack[-1])
                    setattr(current_visited_node, "index_of_rightmost_reference_nodes_for_Hanadi_nodes", reference_nodes_for_Hanadi_nodes_key_counter - 1)
                    
                    setattr(current_visited_node, "index_of_leftmost_reference_nodes_for_Srivastava_nodes", reference_nodes_for_Srivastava_nodes_counter_stack[-1])
                    setattr(current_visited_node, "index_of_rightmost_reference_nodes_for_Srivastava_nodes", reference_nodes_for_Srivastava_nodes_key_counter - 1)
                    
                    if hasattr(current_visited_node, "List_of_nodes_suffix_linked_to_me"):
                        OSHR_internal_nodes_key_counter += 1
                    else:
                        tree.List_of_OSHR_leaf_nodes_from_left_to_right.append(current_visited_node)
                        OSHR_leaf_nodes_key_counter += 1
                    
                    # stat
                    if len(current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes) > 0:
                        s = len(current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes)
                        if s < min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes:
                            min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes = s
                        if s > max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes:
                            max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes = s
                        total_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes += s
                        
                     
                        
                    if len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes) > 0:
                        s = len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes)
                        if s < min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes:
                            min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes = s
                        if s > max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes:
                            max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes = s
                        total_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes += s
                       
                    if hasattr(current_visited_node, "List_of_reference_internal_nodes"):
                        s = len(current_visited_node.List_of_reference_internal_nodes)
                        if s < min_length_of_List_of_reference_internal_nodess:
                            min_length_of_List_of_reference_internal_nodess = s
                        if s > max_length_of_List_of_reference_internal_nodess:
                            max_length_of_List_of_reference_internal_nodess = s
                            
                    if hasattr(current_visited_node, "List_of_nodes_suffix_linked_to_me"):
                        if len(current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes) == 0:
                            if len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes) == 0:
                                a1 += 1
                            else:
                                a2 += 1
                        else:
                            if len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes) == 0:
                                a3 += 1
                            else:
                                a4 += 1
                    else:   
                        if len(current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes) == 0:
                            if len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes) == 0:
                                b1 += 1
                            else:
                                b2 += 1
                        else:
                            if len(current_visited_node.List_of_base_suffixes_derived_from_reference_internal_nodes) == 0:
                                b3 += 1
                            else:
                                b4 += 1
                                
                
                # The follwing new list will be needed in next phase
                if hasattr(current_visited_node, "List_of_nodes_suffix_linked_to_me"):
                    setattr(current_visited_node, "List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST", [])
                    for node in current_visited_node.List_of_nodes_suffix_linked_to_me:
                        current_visited_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST.append((node.index_of_leftmost_leaf_in_ST, node.index_of_rightmost_leaf_in_ST, node))
                    current_visited_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST.sort(key=lambda element: (element[0], element[1]))
                    
                if hasattr(current_visited_node, "List_of_reference_internal_nodes"):
                    setattr(current_visited_node, "List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST", [])
                    for node in current_visited_node.List_of_reference_internal_nodes:
                        current_visited_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST.append((node.index_of_leftmost_leaf_in_ST, node.index_of_rightmost_leaf_in_ST, node))
                    current_visited_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST.sort(key=lambda element: (element[0], element[1]))
        
                #iterative processing
                OSHR_leaf_nodes_counter_stack.pop()
                reference_nodes_for_Hanadi_nodes_counter_stack.pop()
                reference_nodes_for_Srivastava_nodes_counter_stack.pop()
                nodes_stack.pop()
                children_stack.pop()
    
        print ("Number of OSHR leaf_nodes is", "{:,}".format(OSHR_leaf_nodes_key_counter))
        print ("Number of OSHR internal nodes is", "{:,}".format(OSHR_internal_nodes_key_counter))
        print ("Number of base nodes for Hanadi nodes", "{:,}".format(reference_nodes_for_Hanadi_nodes_key_counter))
        print ("Number of base nodes for Srivastava nodes", "{:,}".format(reference_nodes_for_Srivastava_nodes_key_counter))
        
        print ()
        print ("min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes", "{:,}".format(min_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes))
        print ("max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes", "{:,}".format(max_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes))
        print ("total_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes", "{:,}".format(total_size_of_List_of_base_suffixes_derived_from_reference_leaf_nodes))
        print ()
        print ("min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes", "{:,}".format(min_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes))
        print ("max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes", "{:,}".format(max_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes))
        print ("total_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes", "{:,}".format(total_size_of_List_of_base_suffixes_derived_from_reference_internal_nodes))
        print ()
        print ("sum_of_unique_inbetween_nodes_between_internal_nodes", "{:,}".format(sum_of_unique_inbetween_nodes_between_internal_nodes))
        print ("min_length_of_List_of_reference_internal_nodess", "{:,}".format(min_length_of_List_of_reference_internal_nodess))
        print ("max_length_of_List_of_reference_internal_nodess", "{:,}".format(max_length_of_List_of_reference_internal_nodess))
        print ()
        print ("Number of OSHR internal nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (must be covered earlier by one of the three indexes)", "{:,}".format(a1))
        print ("Number of OSHR internal nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (covered by indexing the label between the refrence-internal-node (of this node) and the parent of the reference node)", "{:,}".format(a2))
        print ("Number of OSHR internal nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (Hanadi node)", "{:,}".format(a3))
        print ("Number of OSHR internal nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (Hanadi node)", "{:,}".format(a4))
        print ()
        print ("Number of OSHR leaf nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (bottom_base_node of base path)", "{:,}".format(b1))
        print ("Number of OSHR leaf nodes with empty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (covered by indexing the label between the refrence-internal-node (of this node) and the parent of the reference node)", "{:,}".format(b2))
        print ("Number of OSHR leaf nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and empty List_of_base_suffixes_derived_from_reference_internal_nodes (bottom_base_node of base path)", "{:,}".format(b3))
        print ("Number of OSHR leaf nodes with unempty List_of_base_suffixes_derived_from_reference_leaf_nodes and unempty List_of_base_suffixes_derived_from_reference_internal_nodes (Srivastava node)", "{:,}".format(b4))
        
        
        
    nodes_stack = []
    OSHR_leaf_nodes_counter_stack = []
    reference_nodes_for_Hanadi_nodes_counter_stack = []
    reference_nodes_for_Srivastava_nodes_counter_stack = []
    
    children_stack = []
    start = time.time()
    phase_2_for_OT_indexing_of_base_paths(tree)
    print ("***** Phase 2 finished in", round((time.time() - start), 5), "seconds\n")

    def phase_3_for_OT_indexing_of_base_paths(tree):
        #Traverse OSHR tree and: find base paths, record base and bottom nodes, create OT index.  
        nodes_stack.append(tree.root)
        children_stack.append((list(tree.root.List_of_nodes_suffix_linked_to_me)))
        key_stack_for_base_paths.append(-1)
        
        
        setattr(tree, "OT_indexes_of_merged_three_indexes_temp_dict", defaultdict(list))
        
        OT_index_counter_for_base_paths = 0
        Time_cost_for_collecting_base_paths = 0
        Number_of_collected_base_paths = 0
        Time_cost_for_collecting_paths_using_for_Hanadi_nodes = 0
        Number_of_collected_paths_using_Hanadi_nodes = 0
        Time_cost_for_collecting_paths_using_for_Srivatava_nodes = 0
        Number_of_collected_paths_using_Srivastava_nodes = 0
        
        nodes_key_counter = 0
        a1, a2, b1, b2 = 0, 0, 0, 0
               
        Hanadi_and_Srivastava_nodes_pairing = defaultdict()
        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]
            
            #check if OSHR[current_visited_node.key] is empty, then remove it from nodes_stack
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                nodes_stack.append(last_node_under_top_node_in_stack)     
                children_stack[-1].pop()
                if hasattr(last_node_under_top_node_in_stack, "List_of_nodes_suffix_linked_to_me"):
                    children_stack.append((list(last_node_under_top_node_in_stack.List_of_nodes_suffix_linked_to_me)))
                else:
                    children_stack.append([])
                key_stack_for_base_paths.append(OT_index_counter_for_base_paths) 
            else:
                # create key for nodes in OSHR tree and index them
                OT_index_counter_for_base_paths += 1     # this increment is to make right_OT_index not equal left_OT_index in case no OT indexing at all perfomed under a node
                
                inbetween_bottom_base_node_dict = defaultdict()  # this dict will be used to distinct nodes under tow difference reference nodes that are linking to the same node under current_visited_node                   

                # the following 6 lines cover a special case and for the root only. The suffix-link of child internal node of a root usually link to the root. In case not, 
                # then the node that the child internal node link to must be bottom-node for the root node.
                bottom_base_nodes_that_need_to_be_indexed = []
                if current_visited_node != tree.root:
                    
                    ##################### indexing Hanadi nodes
                    for reference_node_for_Hanadi_node in tree.List_of_reference_nodes_for_Hanadi_nodes_from_left_to_right[current_visited_node.index_of_leftmost_reference_nodes_for_Hanadi_nodes:current_visited_node.index_of_rightmost_reference_nodes_for_Hanadi_nodes + 1]:
                        Time_cost_for_collecting_paths_using_for_Hanadi_nodes += 1
                        suffix_starting_from_current_visited_node = reference_node_for_Hanadi_node.idx + current_visited_node.depth
                        index_key_of_suffix_starting_from_current_visited_node_in_ST = tree.List_of_leaf_suffix_index_to_leaf_memory[suffix_starting_from_current_visited_node].index_of_leaf_in_ST 
                            
                        for Hanadi_node in reference_node_for_Hanadi_node.List_of_Hanadi_nodes:
                            Time_cost_for_collecting_paths_using_for_Hanadi_nodes += 1
                            #tree.OT_indexes_of_merged_three_indexes_temp_dict[Hanadi_node.depth - current_visited_node._suffix_link.depth].append((index_key_of_suffix_starting_from_current_visited_node_in_ST, current_visited_node, reference_node_for_Hanadi_node.idx, "Hanadi nodes index", Hanadi_node))
                            Number_of_collected_paths_using_Hanadi_nodes += 1
                            if not str(current_visited_node._suffix_link) + "-" + str(Hanadi_node) in Hanadi_and_Srivastava_nodes_pairing:
                                Hanadi_and_Srivastava_nodes_pairing[str(current_visited_node._suffix_link) + "-" +str(Hanadi_node)] = []
                                
                            Hanadi_and_Srivastava_nodes_pairing[str(current_visited_node._suffix_link) + "-" + str(Hanadi_node)].append((Hanadi_node.depth - current_visited_node._suffix_link.depth, index_key_of_suffix_starting_from_current_visited_node_in_ST, current_visited_node, reference_node_for_Hanadi_node.idx, "Hanadi nodes index", Hanadi_node))
                                
                    ##################### indexing Srivastava nodes
                    for reference_node_for_Srivastava_node in tree.List_of_reference_nodes_for_Srivastava_nodes_from_left_to_right[current_visited_node.index_of_leftmost_reference_nodes_for_Srivastava_nodes:current_visited_node.index_of_rightmost_reference_nodes_for_Srivastava_nodes + 1]:
                        Time_cost_for_collecting_paths_using_for_Srivatava_nodes += 1
                        suffix_starting_from_current_visited_node = reference_node_for_Srivastava_node.idx + current_visited_node.depth
                        index_key_of_suffix_starting_from_current_visited_node_in_ST = tree.List_of_leaf_suffix_index_to_leaf_memory[suffix_starting_from_current_visited_node].index_of_leaf_in_ST 
                            
                        for Srivastava_node in reference_node_for_Srivastava_node.List_of_Srivastava_nodes:
                            Time_cost_for_collecting_paths_using_for_Srivatava_nodes += 1
                            #tree.OT_indexes_of_merged_three_indexes_temp_dict[Srivastava_node.depth - current_visited_node._suffix_link.depth].append((index_key_of_suffix_starting_from_current_visited_node_in_ST, current_visited_node, reference_node_for_Srivastava_node.idx, "Srivastava nodes index", Srivastava_node))
                            Number_of_collected_paths_using_Srivastava_nodes += 1
                            if not str(current_visited_node._suffix_link) + "-" + str(Srivastava_node) in Hanadi_and_Srivastava_nodes_pairing:
                                Hanadi_and_Srivastava_nodes_pairing[str(current_visited_node._suffix_link) + "-" + str(Srivastava_node)] = []

                            Hanadi_and_Srivastava_nodes_pairing[str(current_visited_node._suffix_link) + "-" + str(Srivastava_node)].append((Srivastava_node.depth - current_visited_node._suffix_link.depth, index_key_of_suffix_starting_from_current_visited_node_in_ST, current_visited_node, reference_node_for_Srivastava_node.idx, "Srivastava nodes index", Srivastava_node))
                                
                
                    #################### Indexing base paths
                    if hasattr(current_visited_node, "List_of_nodes_suffix_linked_to_me"):
                        # collect and find base paths based on OSHR leaf nodes
                        for bottom_base_node in tree.List_of_OSHR_leaf_nodes_from_left_to_right[current_visited_node.index_of_leftmost_OSHR_leaf:current_visited_node.index_of_rightmost_OSHR_leaf + 1]:
                            a1 += 1
                            Time_cost_for_collecting_base_paths += 1
                            if hasattr(bottom_base_node, "List_of_reference_internal_nodes"):
                                f = 0
                                for node_with_suffix_linked_to_current_visited_node in current_visited_node.List_of_nodes_suffix_linked_to_me:
                                    Time_cost_for_collecting_base_paths += 1
                                    right_pos = bisect.bisect(bottom_base_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST, (node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST, node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                                    if right_pos != 0:
                                        right_pos = right_pos - 1
                                    reference_internal_node_for_bottom_base_node = bottom_base_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST[right_pos][2]
                                    if node_with_suffix_linked_to_current_visited_node.index_of_leftmost_leaf_in_ST <= reference_internal_node_for_bottom_base_node.index_of_leftmost_leaf_in_ST <= reference_internal_node_for_bottom_base_node.index_of_rightmost_leaf_in_ST <= node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST:
                                        f = 1 # then it's already covered by previous indexing of the labele between this reference node and its parent node
                                        break
                                        
                                if f == 0:
                                    Time_cost_for_collecting_base_paths += 1
                                    bottom_base_nodes_that_need_to_be_indexed.append(bottom_base_node)        
                            else:
                                bottom_base_nodes_that_need_to_be_indexed.append(bottom_base_node)
                        
                        
                        # collect bottom-base nodes from reference nodes if current_visited_node is List_of_reference_internal_nodes 
                        if hasattr(current_visited_node, "List_of_reference_internal_nodes"):
                            for reference_node in current_visited_node.List_of_reference_internal_nodes:
                                inbetween_bottom_base_node_dict[reference_node._suffix_link] = reference_node._suffix_link
                                for node in get_internal_nodes(tree, reference_node):
                                    inbetween_bottom_base_node_dict[node._suffix_link] = node._suffix_link
                        
                        for bottom_base_node in list(inbetween_bottom_base_node_dict.values()):
                            Time_cost_for_collecting_base_paths += 1
                            f = 0
                            for node_with_suffix_linked_to_current_visited_node in current_visited_node.List_of_nodes_suffix_linked_to_me:
                                Time_cost_for_collecting_base_paths += 1
                                right_pos = bisect.bisect(bottom_base_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST, (node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST, node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                                if right_pos != 0:
                                    right_pos = right_pos - 1
                                node_with_suffix_linked_to_bottom_base_node = bottom_base_node.List_of_nodes_suffix_linked_to_me_sorted_by_leaf_index_under_ST[right_pos][2]
                                if node_with_suffix_linked_to_current_visited_node.index_of_leftmost_leaf_in_ST <= node_with_suffix_linked_to_bottom_base_node.index_of_leftmost_leaf_in_ST <= node_with_suffix_linked_to_bottom_base_node.index_of_rightmost_leaf_in_ST <= node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST:
                                    f = 1 # then it's already covered by previous base path
                                    break
                                            
                            if f == 0:
                                a2 += 1
                                if hasattr(bottom_base_node, "List_of_reference_internal_nodes"):
                                    f = 0
                                    for node_with_suffix_linked_to_current_visited_node in current_visited_node.List_of_nodes_suffix_linked_to_me:
                                        Time_cost_for_collecting_base_paths += 1
                                        right_pos = bisect.bisect(bottom_base_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST, (node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST, node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                                        if right_pos != 0:
                                            right_pos = right_pos - 1
                                        reference_internal_node_for_bottom_base_node = bottom_base_node.List_of_reference_internal_nodes_sorted_by_leaf_index_under_ST[right_pos][2]
                                        if node_with_suffix_linked_to_current_visited_node.index_of_leftmost_leaf_in_ST <= reference_internal_node_for_bottom_base_node.index_of_leftmost_leaf_in_ST <= reference_internal_node_for_bottom_base_node.index_of_rightmost_leaf_in_ST <= node_with_suffix_linked_to_current_visited_node.index_of_rightmost_leaf_in_ST:
                                            f = 1 # then it's already covered by previous indexing the labele between this reference node and its parent node
                                            break
                                            
                                    if f == 0:
                                        Time_cost_for_collecting_base_paths += 1
                                        bottom_base_nodes_that_need_to_be_indexed.append(bottom_base_node)  
                                else:
                                    bottom_base_nodes_that_need_to_be_indexed.append(bottom_base_node)
                                    
                    else:
                        for bottom_base_node in get_internal_nodes(tree, current_visited_node):
                            Time_cost_for_collecting_base_paths += 1
                            bottom_base_nodes_that_need_to_be_indexed.append(bottom_base_node)
                            
                            if hasattr(bottom_base_node, "List_of_nodes_suffix_linked_to_me"):
                                b2 += 1
                            else:
                                b1 += 1
                        
                        
                    for bottom_base_node in bottom_base_nodes_that_need_to_be_indexed:
                        if str(current_visited_node) + "-" + str(bottom_base_node) not in Hanadi_and_Srivastava_nodes_pairing:
                            Number_of_collected_base_paths += 1
                            suffix_starting_from_current_visited_node = tree.List_of_left_to_right_suffix_indexes[bottom_base_node.index_of_leftmost_leaf_in_ST] + current_visited_node.depth
                            index_key_of_suffix_starting_from_current_visited_node_in_ST = tree.List_of_leaf_suffix_index_to_leaf_memory[suffix_starting_from_current_visited_node].index_of_leaf_in_ST 
                            tree.OT_indexes_of_merged_three_indexes_temp_dict[bottom_base_node.depth - current_visited_node.depth].append((index_key_of_suffix_starting_from_current_visited_node_in_ST, current_visited_node, bottom_base_node.leaf_node_to_use_in_upward_walk.idx, "Base paths index", bottom_base_node))
                            OT_index_counter_for_base_paths += 1
                        
                    
                
                
                if not hasattr(current_visited_node, "left_OT_index"):
                    setattr(current_visited_node, "left_OT_index", int)
                    setattr(current_visited_node, "right_OT_index", int)
                
                current_visited_node.left_OT_index = key_stack_for_base_paths[-1]
                current_visited_node.right_OT_index = OT_index_counter_for_base_paths 
                OT_index_counter_for_base_paths += 1
                key_stack_for_base_paths.pop() 
                
                # to be used in searching
                if hasattr(current_visited_node, "List_of_nodes_suffix_linked_to_me"):
                    setattr(current_visited_node, "List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree", [])
                    for node in current_visited_node.List_of_nodes_suffix_linked_to_me:
                        current_visited_node.List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree.append((node.left_OT_index, node.right_OT_index, node))
                    current_visited_node.List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree.sort(key=lambda element: (element[0], element[1]))
                    
                if hasattr(current_visited_node, "List_of_base_suffixes_derived_from_reference_leaf_nodes"):
                    setattr(current_visited_node, "List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST", [])
                    for base_suffix in current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes:
                        leaf_node_of_previous_node = node = tree.List_of_leaf_suffix_index_to_leaf_memory[base_suffix - current_visited_node.depth - 1]
                        current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST.append((leaf_node_of_previous_node.index_of_leaf_in_ST, leaf_node_of_previous_node.index_of_leaf_in_ST, leaf_node_of_previous_node))
                    current_visited_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST.sort(key=lambda element: (element[0], element[1]))
                    
                nodes_stack.pop()
                children_stack.pop()
         
        for pair_nodes in Hanadi_and_Srivastava_nodes_pairing:
            for dat in Hanadi_and_Srivastava_nodes_pairing[pair_nodes]:
                tree.OT_indexes_of_merged_three_indexes_temp_dict[dat[0]].append((dat[1], dat[2], dat[3], dat[4], dat[5]))

        Hanadi_and_Srivastava_nodes_pairing.clear()
        
        for key in sorted(tree.OT_indexes_of_merged_three_indexes_temp_dict):
            tree.OT_indexes_of_merged_three_indexes_temp_dict[key].sort(reverse=True, key=lambda element: (element[0]))
            
            
        print ("Number of OSHR leaf bottom base nodes for OSHR internal top base nodes", "{:,}".format(a1))
        print ("Number of OSHR internal bottom base nodes for OSHR internal top base nodes", "{:,}".format(a2))
        print ("Number of OSHR leaf bottom base nodes for OSHR leaf top base nodes", "{:,}".format(b1))
        print ("Number of OSHR internal bottom base nodes for OSHR leaf top base nodes", "{:,}".format(b2))
        print ()
        print ("Left and right OT index of root for OSHR nodes",  tree.root.left_OT_index + 1, "{:,}".format(tree.root.right_OT_index))
        print ("Time_cost_for_collecting_base_paths", "{:,}".format(Time_cost_for_collecting_base_paths))
        print ("Number_of_collected_base_paths", "{:,}".format(Number_of_collected_base_paths))
        print ("Time_cost_for_collecting_paths_using_for_Hanadi_nodes", "{:,}".format(Time_cost_for_collecting_paths_using_for_Hanadi_nodes))
        print ("Number_of_collected_paths_using_Hanadi_nodes", "{:,}".format(Number_of_collected_paths_using_Hanadi_nodes))
        print ("Time_cost_for_collecting_paths_using_for_Srivatava_nodes", "{:,}".format(Time_cost_for_collecting_paths_using_for_Srivatava_nodes))
        print ("Number_of_collected_paths_using_Srivastava_nodes", "{:,}".format(Number_of_collected_paths_using_Srivastava_nodes))
        
        
    nodes_stack = []
    children_stack = []
    key_stack_for_base_paths = []

        
    start = time.time()
    phase_3_for_OT_indexing_of_base_paths(tree)
    print ("***** Phase 3 finished in", round((time.time() - start), 5), "seconds\n")


    
    def phase_4_for_OT_indexing_of_base_paths(tree):
        #map base paths base nodes for Hanadi and Srivastava node to same path starting from root of ST
        #iterative processing
        nodes_stack.append(tree.root)
        children_stack.append((list(tree.root.transition_links[x] for x in sorted(tree.root.transition_links.keys(), reverse=True))))
        
        sum_of_base_paths_indexes = 0
        sum_of_Hanadi_nodes_indexes = 0
        sum_of_Srivastava_nodes_indexes = 0

        while nodes_stack:
            current_visited_node = nodes_stack[-1]                
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                #iterative processing
                nodes_stack.append(last_node_under_top_node_in_stack)     # append it to process later with the required order (postorder) and remove it from OSHR[current_visited_node.index_of_leaf_in_ST ]
                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))
            else:
                # alongside processing
                if not current_visited_node.is_leaf():
                    if current_visited_node.depth in tree.OT_indexes_of_merged_three_indexes_temp_dict:
                        for i in range(len(tree.OT_indexes_of_merged_three_indexes_temp_dict[current_visited_node.depth])-1, -1, -1):
                            temp = tree.OT_indexes_of_merged_three_indexes_temp_dict[current_visited_node.depth][i]
                            key_of_suffix_idx = temp[0]
                            
                            if current_visited_node.index_of_leftmost_leaf_in_ST <= key_of_suffix_idx <= current_visited_node.index_of_rightmost_leaf_in_ST:
                                top_node = temp[1]
                                guiding_suffix_index = temp[2] # to be useed in searching 
                                index_type = temp[3]
                                bottom_node = temp[4]
                                if index_type == "Base paths index":
                                    temp = current_visited_node
                                    required_depth = bottom_node.parent.depth - top_node.depth
                                    while temp.depth > required_depth: 
                                        if not hasattr(temp, "OT_indexes_of_merged_three_indexes"):
                                            setattr(temp, "OT_indexes_of_merged_three_indexes", [])
                                        temp.OT_indexes_of_merged_three_indexes.append((top_node.left_OT_index, top_node.right_OT_index, top_node, guiding_suffix_index, index_type, bottom_node))
                                        temp = temp.parent
                                        sum_of_base_paths_indexes += 1
                                        
                                            
                                elif index_type == "Hanadi nodes index":
                                    Hanadi_node = temp[4]
                                    temp = current_visited_node
                                    required_depth = Hanadi_node.parent.depth - top_node._suffix_link.depth
                                    while temp.depth > required_depth: 
                                        if not hasattr(temp, "OT_indexes_of_merged_three_indexes"):
                                            setattr(temp, "OT_indexes_of_merged_three_indexes", [])
                                        temp.OT_indexes_of_merged_three_indexes.append((top_node.left_OT_index, top_node.right_OT_index, top_node, guiding_suffix_index, index_type))
                                        temp = temp.parent
                                        sum_of_Hanadi_nodes_indexes += 1
                                        
                                            
                                elif index_type == "Srivastava nodes index":  # this only for the deepest_reference_nodes index
                                    Srivastava_node = temp[4]
                                    temp = current_visited_node
                                    required_depth = Srivastava_node.parent.depth - top_node._suffix_link.depth
                                    while temp.depth > required_depth: 
                                        if not hasattr(temp, "OT_indexes_of_merged_three_indexes"):
                                            setattr(temp, "OT_indexes_of_merged_three_indexes", [])
                                        temp.OT_indexes_of_merged_three_indexes.append((top_node.left_OT_index, top_node.right_OT_index, top_node, guiding_suffix_index, index_type))
                                        temp = temp.parent
                                        sum_of_Srivastava_nodes_indexes += 1
                                
                                tree.OT_indexes_of_merged_three_indexes_temp_dict[current_visited_node.depth].pop()
                                
                            else:
                                break
                    
                    
                    
                #iterative processing 
                nodes_stack.pop()
                children_stack.pop()
    
        print ("Sum_of_base_paths_indexes", "{:,}".format(sum_of_base_paths_indexes ))
        print ("Sum_of_Hanadi_nodes_indexes", "{:,}".format(sum_of_Hanadi_nodes_indexes))
        print ("Sum_of_Srivastava_nodes_indexes", "{:,}".format(sum_of_Srivastava_nodes_indexes))
        print ("*** Total sum of mapping OT indexes of all three indexes to the last extent path (the one starting from root node)", "{:,}".format(sum_of_base_paths_indexes + sum_of_Hanadi_nodes_indexes + sum_of_Srivastava_nodes_indexes))
        
    nodes_stack = []
    children_stack = []
    start = time.time()
    phase_4_for_OT_indexing_of_base_paths(tree)
    print ("***** Phase 4 finished in", round((time.time() - start), 5), "seconds\n")  

    def phase_5_for_OT_indexing_of_base_paths(tree):
        #sort OT inex lists at each node 
        #iterative processing
        nodes_stack.append(tree.root)
        children_stack.append((list(tree.root.transition_links[x] for x in sorted(tree.root.transition_links.keys(), reverse=True))))
        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]                
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                #iterative processing
                nodes_stack.append(last_node_under_top_node_in_stack)     # append it to process later with the required order (postorder) and remove it from OSHR[current_visited_node.index_of_leaf_in_ST ]
                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))
            else:
                # alongside processing
                if not current_visited_node.is_leaf():
                    if hasattr(current_visited_node, "OT_indexes_of_merged_three_indexes"):
                        current_visited_node.OT_indexes_of_merged_three_indexes.sort(key=lambda element: (element[0], element[1]))
                        
                #iterative processing 
                nodes_stack.pop()
                children_stack.pop()
        
        
    nodes_stack = []
    children_stack = []
    start = time.time()
    phase_5_for_OT_indexing_of_base_paths(tree)
    print ("***** Phase 5 finished in", round((time.time() - start), 5), "seconds\n")  



def get_internal_nodes(tree, node):
    
    nodes_stack = []
    children_stack = []
    
    def preprocessing(tree):
        
        #iterative processing
        nodes_stack.append(node)
        children_stack.append((list(node.transition_links[x] for x in sorted(node.transition_links.keys(), reverse=True))))
        
        while nodes_stack:
            current_visited_node = nodes_stack[-1]                  
            if len(children_stack[-1]) > 0:
                last_node_under_top_node_in_stack = children_stack[-1][-1]
                #iterative processing
                nodes_stack.append(last_node_under_top_node_in_stack)   # append it to process later with the required order (postorder) and remove it from OSHR[current_visited_node.index_of_leaf_in_ST]
                children_stack[-1].pop()                    
                children_stack.append((list(last_node_under_top_node_in_stack.transition_links[x] for x in sorted(last_node_under_top_node_in_stack.transition_links.keys(), reverse=True))))
                                          
            else:
                # alongside processing
                if not current_visited_node.is_leaf():
                    results.append(current_visited_node)
                
                    
                #iterative processing 
                nodes_stack.pop()
                children_stack.pop()
                
    
    results = []
    preprocessing(tree)
    return results[:-1]
    
######################################################################################## Searching code ##############################################################################################################
    
def Run_Mandoiu_algorithm(tree, top_node, bottom_node, starting_node):  
    #check bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes as follows in log\Sigma 
    
    result_node = None
    if len(top_node.List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree) > 0:
        right_pos = bisect.bisect(top_node.List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree, (starting_node.right_OT_index, starting_node.right_OT_index)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
        if right_pos != 0:
            right_pos = right_pos - 1
        inter = top_node.List_of_nodes_suffix_linked_to_me_sorted_by_OT_index_under_OSHR_tree[right_pos]
        left_OT_index = inter[0]
        right_OT_index = inter[1]
        if left_OT_index <= starting_node.left_OT_index <= starting_node.right_OT_index <= right_OT_index:
            nn = inter[2]   #node_link_to_top_node_and_is_OSHR_parent_to_starting_node
            s = len(bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST)
            if s > 0:
                right_pos = bisect.bisect_left(bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST, (nn.index_of_rightmost_leaf_in_ST, nn.index_of_rightmost_leaf_in_ST)) # right_pos bcus we want to find node satisfies the condition starting_node.left_OT_index >= node.left_OT_index and starting_node.right_OT_index <= node.right_OT_index
                if right_pos == s:
                    right_pos = right_pos - 1
                    
                index_of_leaf_in_ST = bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST[right_pos][0]
                leaf_node = bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST[right_pos][2]                
                if right_pos != 0 and not (nn.index_of_leftmost_leaf_in_ST <= index_of_leaf_in_ST <= nn.index_of_rightmost_leaf_in_ST):
                    right_pos = right_pos - 1
                    index_of_leaf_in_ST = bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST[right_pos][0]
                    leaf_node = bottom_node.List_of_base_suffixes_derived_from_reference_leaf_nodes_sorted_by_leaf_index_under_ST[right_pos][2]
                    
                if nn.index_of_leftmost_leaf_in_ST <= index_of_leaf_in_ST <= nn.index_of_rightmost_leaf_in_ST:
                    result_node = tree.List_of_leaf_suffix_index_to_leaf_memory[leaf_node.idx - (starting_node.depth - top_node.depth) + 1]
                
    return result_node            


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
    
    print ("------------------------------------------------------------------------------------------")    
    start = time.time()
    Build_OT_index(tree)
    print ("Building OT index using base paths took", round((time.time() - start), 5), "seconds")
    
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
            print ("nn", nn)
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
                
                for starting_node in list_of_starting_nodes: # the last node is the root node so it was excluded
                    # check first if the matching node is a direct child node of starting_node
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
                        if hasattr(end_node_of_pattern_from_root, "OT_indexes_of_merged_three_indexes"):
                            right_pos = bisect.bisect(end_node_of_pattern_from_root.OT_indexes_of_merged_three_indexes, (starting_node.right_OT_index, starting_node.right_OT_index))
                            if right_pos != 0:
                                right_pos = right_pos - 1
                                
                            index = end_node_of_pattern_from_root.OT_indexes_of_merged_three_indexes[right_pos]
                            #left_OT_index = index[0] and right_OT_index = index[1]
                            
                            if starting_node.left_OT_index <= index[0] <= index[1] <= starting_node.right_OT_index:  # then depth of found top base node is larger or equal the depth of starting_node
                                leaf_node = tree.List_of_leaf_suffix_index_to_leaf_memory[index[3] + (index[2].depth - starting_node.depth)] # top_node = index[2] and guiding_suffix_index = index[3]
                                required_depth = starting_node.depth + end_node_of_pattern_from_root.depth
                                while leaf_node.parent.depth >= required_depth: # as matching_node may not be a leaf node
                                    leaf_node = leaf_node.parent 
                                
                                matching_node = leaf_node
                                matching_node_is_found = 1
                                    
                            elif index[0] <= starting_node.left_OT_index <= starting_node.right_OT_index <= index[1]:  # then depth of found top base node is smaller than the depth of starting_node
                                if index[4] == "Base paths index": #index_type = index[4]
                                    leaf_node = Run_Mandoiu_algorithm(tree, index[2], index[5], starting_node) #top_node = index[2]; bottom_node = index[5]; bottom node is then a base node based on base path index format
                                    if leaf_node != None and starting_node.index_of_leftmost_leaf_in_ST <= leaf_node.index_of_leaf_in_ST <= starting_node.index_of_rightmost_leaf_in_ST:
                                        matching_node = leaf_node
                                        matching_node_is_found = 1
                                        
                                else:#if index_type == "Hanadi nodes index" or index_type == "Srivastava nodes index": 
                                    leaf_node = tree.List_of_leaf_suffix_index_to_leaf_memory[index[3] - (starting_node.depth - index[2].depth)] #top_node = index[2]; guiding_suffix_index = index[3]
                                    if starting_node.index_of_leftmost_leaf_in_ST <= leaf_node.index_of_leaf_in_ST <= starting_node.index_of_rightmost_leaf_in_ST:
                                        matching_node = leaf_node  
                                        matching_node_is_found = 1
                                        
                        else:
                            # then check end_node_of_pattern_from_root.List_of_base_suffixes_derived_from_reference_leaf_nodes by eunning Manoiu algorithm
                            leaf_node = Run_Mandoiu_algorithm(tree, tree.root, end_node_of_pattern_from_root, starting_node)
                            if leaf_node != None and starting_node.index_of_leftmost_leaf_in_ST <= leaf_node.index_of_leaf_in_ST <= starting_node.index_of_rightmost_leaf_in_ST:
                                matching_node = leaf_node
                                matching_node_is_found = 1
         

                    if matching_node_is_found == 0:
                        print ("No matching node found") #print ("No matching node found", "for", pattern, "under node", starting_node)
                    else:
                        print ("Found matching node", matching_node) #print ("Found matching node", matching_node, "for", pattern, "under node", starting_node)
                            

            print ("Total time for searching for", len(patterns), "patterns of length", pattern_length, "starting from", Number_of_starting_nodes, "nodes out of ", len(nodes_by_depth_dict[depth]), "nodes at depth", depth, "with complexity of number_of_child_internal_nodes_under_starting_nodes", number_of_child_internal_nodes_under_starting_nodes, "and number_of_child_leaf_nodes_under_starting_nodes", number_of_child_leaf_nodes_under_starting_nodes, "is", round((time.time() - start), 5), "seconds") 
                
            
        print ("Total time for searching for", total_number_of_patterns_of_all_lengths, "of all lengths starting from", Number_of_starting_nodes, "nodes out of ", len(nodes_by_depth_dict[depth]), "nodes at depth", depth, "with complexity of number_of_child_internal_nodes_under_starting_nodes", number_of_child_internal_nodes_under_starting_nodes, "and number_of_child_leaf_nodes_under_starting_nodes", number_of_child_leaf_nodes_under_starting_nodes, "is", round(time.time() - start_time_for_searching_all_patterns_of_all_lengths, 5), "seconds")
        print ()
           
start()
