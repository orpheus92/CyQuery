import cymetric as cym
from cymetric import metric


def read_db(filename):
    db = cym.dbopen(filename)
    return db


def get_table(db, table_name):
    # Resources, Materials, Products, Recipes, Compostions, TimeSeriesEnrichmentFeed, TimeSeriesEnrichmentSWU, Transactions
    evaler = cym.Evaluator(db)
    return evaler.eval(table_name)  # if attr is not None else


def get_data(table, attr, func):
    return table[func(table[attr])]
    # return table[attr]


def func(x, cmp=None):
    return x == x if cmp is None else cmp(x)


def get_commodity(db, cmd=None):
    # Commodity lists or df for given commodity
    table = get_table(db, 'Transactions')
    return table.Commodity.unique() if cmd is None else table[table.Commodity == cmd]


def get_recipe(db):
    # Return recipe name and QualId
    recipe = get_table(db, 'Recipes')
    return recipe.Recipe.unique(), recipe.QualId.unique()


class CyclusData:
    def __init__(self, filename):
        db = cym.dbopen(filename)
        self.db = db

    def transactions(self):
        self.transactions_table = get_table(self.db, 'Transactions') \
                return self.tranactions_table

    def resources(self):
        self.resources_table = get_table(self.db, 'Resources')
        return self.resources_table

    def compositions(self):
        self.compositions_table = get_table(self.db, 'Compositions')
        return self.compostions_table

    def materials(self):
        self.materials_table = get_table(self.db, 'Materials')
        return self.materials_table

    def tables(self):
        self.tables = self.db.tables
        return self.tables

    def get_table(self, attr):
        self.select_table = get_table(self.db, attr)
        return self.select_table

    # Time Series Transaction Query
    def get_time_transaction(self, commod=None, rec=None, send=None):
        # return resources
        if not hasattr(self, 'transactions_table'):
            # if self.transactions_table is None:
            self.transactions()
        selections = []
        if commod is not None:
            selections.append(self.transactions_table.Commodity == commod)
        if rec is not None:
            selections.append(self.transactions_table.ReceiverId == rec)
        if send is not None:
            selections.append(self.transactions_table.SenderId == send)
        if len(selections) == 0:
            return self.transactions_table
        elif len(selections) == 1:
            return self.transactions_table[selections[0]]
        else:
            sel = selections[0]
            for i in range(1, len(selections)):
                sel = sel & selections[i]

            return self.transactions_table[sel]

    def get_time_commod(self, commod=None, rec=None, send=None):
        selectionrId = self.get_time_transaction(commod, rec, send)
        if not hasattr(self, 'resources_table'):
            self.resources()
            df = self.resources_table
            return df.loc[df['ResourceId'].isin(selectionrId.ResourceId)]
            # def get_time_resource()