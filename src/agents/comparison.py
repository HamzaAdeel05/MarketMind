class Comparison:
    def __init__(self,dispatcher): self.dispatcher=dispatcher
    def run(self,state,entities=None,attributes=None):
        return self.dispatcher.execute("compare_companies",{"entities":entities or ["Vendor Alpha","Vendor Beta","Vendor Gamma"],"attributes":attributes or ["repository context","administrative controls","deployment"]},{"compute"})
