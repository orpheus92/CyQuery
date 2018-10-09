import queue

def check_fit(*args, **kwargs):
    """
    arg: threshold

    kwargs:
        "check_attr": attr to check, default, "parent_fitness"
        
        "greater": if true, partitions with attr greater than threshold will be returned 

        "node": node where the check will be started 

        "partitions": list of partitions that will be checked 
        "p_order": if true, check will follow the list order of the partition
                    otherwise, top to bottom

        "tree": tree that will be checked 

    
    """
    # No matter what, threshold is required to decide whether a partition needs to be resampled 
    threshold = args[0]

    # define comparator
    def compare(a,b):
        # by default, find nodes less than threshold 
        if "greater" in kwargs and kwargs["greater"] is True:
            return a>=b
        else:
            return a<b

    # Get attribute to check 
    if "check_attr" in kwargs:
        check = kwargs["check_attr"]
    else:
        # default partent fitness
        check = "parent_fitness"

    if "node" in kwargs:
        node = kwargs["node"]
            # We agree that we could only count on the partitions with higher persistence. 
            # We want to go from root to leaves and stop at a leaf when the parent_fitness with that node is low
        return  find_partitions(node,threshold,check, compare)
        # return p2sample
    
    elif "tree" in kwargs:
        node = getattr(kwargs["tree"],"root")
        if node:
            return find_partitions(node, threshold, check, compare)

        print("Can't find the root of the tree!!!")
        return 
    
    elif "partitions" in kwargs:
        partitions = kwargs["partitions"]
        p2sample = []
        if "p_order" in kwargs and kwargs["p_order"] is True: # if user required to follow order of partitions
            for p in partitions:
                if compare(getattr(p,check), threshold):
                    p2sample.append(p)
        else:
            # by default, assume first partition is the root
            return find_partitions(partitions[0], threshold,check,compare)

    else:
        print("Invalid Inputs! ")
        return

def find_partitions(node, threshold, check, compare):
    # Given a node, find leaf nodes that should be resampled
    outp = []
    nodes_ = queue.Queue()
    nodes_.put(node)
    while not nodes_.empty():
        cur_node = nodes_.get()
        for node in cur_node.children:
            # check partent fitness of this node, if greater than thres, put in queue, else, put in output
            if node: # Not sure whether None will exists, put here to make sure
                if compare(getattr(node, check), threshold):
                    outp.append(node)
                else:
                    nodes_.put(node)
                    
    return outp
        