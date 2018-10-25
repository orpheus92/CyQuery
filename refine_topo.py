import queue
import pandas as pd


class Refine:
    def __init__(self, *args, **kwargs):
        # threshold should be the first positional argument
        self.threshold = args[0]

        if "node" in kwargs:
            self.node = kwargs["node"]
        elif "tree" in kwargs:
            node = getattr(kwargs["tree"],"root")
            self.node = node
        elif "nodes" in kwargs:
            self.nodes = kwargs["nodes"]
        else:
            print("Invalid Inputs! ")
            return
        
        if "extra_data" in kwargs:
            self.data = kwargs["extra_data"]

        if "traverse" in kwargs:
            self.traverse = kwargs["traverse"]
        
        # function to compute a measure for a node, take in a node and return a measure
        if "measure" in kwargs:
            self.measure = kwargs["measure"]
        else:
            self.measure = self.measure_

        if "return_attr" in kwargs:
            self.get_return_attr = kwargs["return_attr"]
        else: 
            self.get_return_attr = lambda x: x

        # comparator to find the node
        if "compare" in kwargs:
            compare = kwargs["compare"]
            if compare == "less":
                self.compare = lambda a, b: a < b
            elif compare == "greater":
                self.compare = lambda a, b: a > b
            elif compare == "between":
                self.compare = lambda a,b: (a >= b[0] and a <= b[1])
            elif compare == "outside":
                self.compare = lambda a,b: (a >= b[1] or a <= b[0])
            else:
                self.compare = compare
                    
    def search(self):
        out = []
        if hasattr(self, "nodes"):
            for i in self.nodes:
                if self.check_measure(i):
                    out.append(self.get_return_attr(i))
        elif hasattr(self, "node") and self.traverse == "BFS":

            nodes_ = queue.Queue()
            nodes_.put(self.node)

            while not nodes_.empty():
                cur_node = nodes_.get()
                for node in cur_node.children:
                    if node and self.check_measure(node):
                        out.append(self.get_return_attr(node))
                    else: 
                        nodes_.put(node)

            return out

        elif hasattr(self, "node") and self.traverse == "DFS":
            nodes_ = []
            nodes_.append(self.node)

            while not nodes_:
                cur_node = nodes_.pop()
                for node in cur_node.children:
                    if node and self.check_measure(node):
                        out.append(self.get_return_attr(node))
                    else: 
                        nodes_.append(node)

            return out

        else: 
            print("No known traversal method")
            if hasattr(self, "node") and self.node and self.check_measure(self.node):
                out.append(self.get_return_attr(self.node))

        return out

    def check_measure(self, node):
        if hasattr(self, "measure"):
            if hasattr(self, "data"):
                val = self.measure(node, self.data)
            else:
                val = self.measure(node)
            return self.compare(val, self.threshold)
        return False
    

    def measure_(self, node):
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics.pairwise import cosine_similarity
        
        attr="id"
        if hasattr(node, attr) and hasattr(node,'parent') and hasattr(node.parent,attr):
            cid, pid = getattr(node, attr), getattr(node.parent, attr)
            if cid >=0 and pid>=0: #check both are valid partitions

                cx, cy = node.data.x.values, node.data.y.values
                px, py = node.parent.data.x.values, node.parent.data.y.values
                
                # Linear coeff for both and similarity 
                creg, preg = LinearRegression().fit(cx, cy), \
                            LinearRegression().fit(px, py)

                # fitness
                cscore, pscore = creg.score(cx, cy), preg.score(px, py)
                # sensitivity
                ccoef, pcoef = creg.coef_, preg.coef_
                # intercept
                cint, pint = creg.intercept_, preg.intercept_

                return cosine_similarity(ccoef.reshape(1, -1), pcoef.reshape(1, -1))[0][0]
        return -1  