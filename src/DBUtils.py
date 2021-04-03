# Module: DBUtils.py
def convertToDictionary(cursor,records):
    """ Given a DB API 2.0 cursor object that has been executed, returns
    a dictionary that maps each field name to a column index; 0 and up. """
    fields = {}
    column = 0
    for d in cursor.description:
        fields[d[0]] = column
        column = column + 1

    results = []
    for record in records:
        recordDict = {}
        for field,pos in fields.items():
            recordDict[field] = record[pos]
        results.append(recordDict)

    return results