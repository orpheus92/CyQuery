import queue

def check_fit(*args, **kwargs):
    """
    arg: threshold

    kwargs:
        "check_attr": attr to check, if none passed, will compute parent similarity
        
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

    if "func" in kwargs:
        func = kwargs["func"]
    else: 
        func = None

    
    # Get attribute to check 
    if "check_attr" in kwargs:
        check = kwargs["check_attr"]
    else:
        # default partent fitness
        if "reg_data" in kwargs and "raw_data" in kwargs:
            reg_data, raw_data = kwargs["reg_data"], kwargs["raw_data"]
            check = None
        else:
            print("Need data and rawdata")
            return 
        

    if "node" in kwargs:
        node = kwargs["node"]
            # We agree that we could only count on the partitions with higher persistence. 
            # We want to go from root to leaves and stop at a leaf when the parent_fitness with that node is low
        return  find_partitions(node,threshold,check, compare, func)
        # return p2sample
    
    elif "tree" in kwargs:
        node = getattr(kwargs["tree"],"root")
        if node:
            return find_partitions(node, threshold, check, compare, func)

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
            return find_partitions(partitions[0], threshold,check,compare, func)

    else:
        print("Invalid Inputs! ")
        return

def find_partitions(node, threshold, check, compare,func=None):
    # Given a node, find leaf nodes that should be resampled
    outp = []
    nodes_ = queue.Queue()
    nodes_.put(node)
    while not nodes_.empty():
        cur_node = nodes_.get()
        for node in cur_node.children:
            # check partent fitness of this node, if greater than thres, put in queue, else, put in output
            if node: # Not sure whether None will exists, put here to make sure
                if not check:
                    node_val = check_sim(node, reg_data, raw_data) 
                elif func is None:
                    node_val = getattr(node, check)
                else:
                    node_val = func(getattr(node,check))
                if compare(node_val, threshold):
                    outp.append(node)
                else:
                    nodes_.put(node)
                    
    return outp

def check_sim(node, data, rawdata, attr='id'):
    # Only checks parent for now 
    if hasattr(node, attr) and hasattr(node,'parent') and hasattr(node.parent,attr):
        cid, pid = getattr(node, attr), getattr(node.parent, attr)
        if cid >=0 and pid>=0:
            cind, pind = get_pts(data.partitions[cid],data.pts_loc), get_pts(data.partitions[pid],data.pts_loc)
            if isinstance(rawdata, pd.DataFrame):
                cdata, pdata = rawdata.loc[cind,:].values, rawdata.loc[pind,:].values
            else:
                cdata, pdata = rawdata[cind,:], rawdata[pind,:]
            
            # Linear coeff for both and similarity 
            creg, preg = LinearRegression().fit(cdata[:,:-1], cdata[:,-1]), \
                        LinearRegression().fit(pdata[:,:-1], pdata[:,-1])
            
            # fitness
            cscore, pscore = creg.score(cdata[:,:-1], cdata[:,-1]), preg.score(pdata[:,:-1], pdata[:,-1])
            # sensitivity
            ccoef, pcoef = creg.coef_, preg.coef_
            # intercept
            cint, pint = creg.intercept_, preg.intercept_
            # print('cid = ',cid, " pid = ", pid, " cos = ", cosine_similarity(ccoef.reshape(1, -1), pcoef.reshape(1, -1)))
            return cosine_similarity(ccoef.reshape(1, -1), pcoef.reshape(1, -1))[0][0]
    return -1  