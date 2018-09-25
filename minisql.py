import sys
import re
import csv
metadata={}
F=['max','min','sum','avg','count']
operators = ['>=','<=','>','<','=']
colum=[]
aggre=[]
dist=[]

def readmetadata():
    meta_file = open('metadata.txt', 'r')
    start = False
    table_name = ""
    for line in meta_file:
        line = line.strip()
        if line == '<begin_table>':
            start = True
        elif start:
            table_name = line
            metadata[table_name] = []
            start = False
        elif line != '<end_table>':
            metadata[table_name].append(line)
    '''
    i=0
    f = open('metadata.txt','r')
    f=f.read().split('\n')
    while(i<len(f)):
        if f[i]=='<begin_table>':
            tablename=f[i+1]
            i+=2
            attributes=[]
            while f[i]!='<end_table>':
                attributes.append(f[i])
                i+=1
            metadata[tablename]=attributes
        i+=1
    '''
def readcsv(table_name):
    data = []
    file_name = table_name + '.csv'
    data_file = open(file_name, 'r')
    reader = csv.reader(data_file)
    for row in reader:
        data.append(row)
    data_file.close()
    return data
    '''
    f=open(filename+'.csv','r')
    data=[]
    f=f.read().split('\n')
    for i in range(len(f)):
        y = f[i].split(',')
        if(len(y)==1 and y[0]==''):
            break
        data.append(y)
    return data
    '''
def main():
    queries = str(sys.argv[1]).split(';')
    for query in queries:
        if query!='':
            sql_query(query)

def printerror(error):
    sys.stderr.write(error+'\n')
    quit(-1)

def checkerrors(query):
    if not 'from' in query.lower().split():
        printerror('From attribute missing')
    if(query.lower().count('select')>1):
        printerror('More than one select attribute given')
    if(query.lower().count('from')>1):
        printerror('More than one from attribute given')
    subquery = query.split('from')
    if not 'select' in str(subquery[0]).lower().split():
        printerror('select attribute not given')

def checkerrorswhere(query,aggre,dist,col):
    if(len(col)+len(aggre)+len(dist)==0):
        printerror('Nothing selected')
    elif len(dist)!=0 and len(aggre)!=0:
        printerror('distinct and aggregate not used together')

def format(query):
    query = re.sub(' +',' ',query).strip()
    return query

def splitcolumns(columns,end):
    for col in columns:
        fl=False
        col = format(col)
        for f in F:
            if f+'(' in col.lower():
                if ')' not in col:
                    printerror('missing ) in query')
                colname = col.strip(')').split('(')[1]
                fl=True
                aggre.append([f,colname])
                break
        if fl==False and distfl==False:
            colum.append(col)
    checkerrorswhere(end.split('where'),aggre,dist,colum)

def aggregate_query(tables,tabledata):
    if len(colum)!=0:
        printerror('syntax error')
    tablehead=''
    ans=''
    for col in aggre:
        func = col[0]
        column = col[1]
        if column=='*':
            column = metadata[tables[0]][0]
        if '.' in column:
            table,column = column.split('.')
        else:
            c=0
            for tab in tables:
                if column in metadata[tab]:
                    table=tab
                    c+=1
            if c==0:
                printerror('No column exists')
            elif c>1:
                printerror('specify the table for a same column name')
        tablehead+=table+'.'+column+','
        data=[]
        for x in range(len(tabledata[table])):
            if len(tabledata[table][x])==1 and tabledata[table][x][0]=='':
                break
            val = tabledata[table][x][metadata[table].index(column)]
            data.append(val)
        if func.lower()=='min':
            ans+=str(min(data))
        if func.lower()=='max':
            ans+=str(max(data))
        if func.lower()=='sum':
            s=0
            for i in range(len(data)):
                s=s+int(data[i])
            ans+=str(s)
        if func.lower()=='avg':
            s=0
            for i in range(len(data)):
                s=s+int(data[i])
            ans+=str(float(s/len(data)))
        if func.lower()=='count':
            ans+=str(len(tabledata[table]))
        ans+=','
    print(tablehead.strip(','))
    print(ans.strip(','))


def findtable(col,tables):
    if '.' in col:
        table,col=col.split('.')
        table=format(table)
        col=format(col)
        if table not in tables:
            printerror(table+':No such table exists')
        return table
    c=0
    for table in tables:
        if col in metadata[table]:
            c+=1
            tab=table
    if c>1:
        printerror(col+':specify the table name for the column')
    if c==0:
        printerror(col+':No such column exists')
    return tab

def distinct_query(tables,tabledata):
    tablehead=''
    coldata={}
    maxlen=0
    fl=0
    data=[]
    if tables[0] not in tabledata:
        printerror(tables[0]+':No such table')
    for col in dist:
        if col not in metadata[tables[0]]:
            printerror(col+':No such column in given table')
    for x in range(len(tabledata[tables[0]])):
        a=()
        for col in dist:
            if fl==0:
                tablehead += tables[0]+'.'+col+','
            a+=(tabledata[tables[0]][x][metadata[tables[0]].index(col)],)
        fl=1
        if list(a) not in data:
            data.append(list(a))
    print (tablehead.strip(','))
    for i in range(len(data)):
        print(data[i])

def distinctsplit(begin):
    if 'distinct' in begin:
        dis=begin.split('distinct')
        if(len(dis)==1):
            printerror('colums not specified for distinct')
        if len(dis)==2:
            distfl=True
            dis=format(str(dis[1])).split(',')
        for i in range(len(dis)):
            dist.append(dis[i])

def findtablecolumn(colum,tables):
    columntable={}
    tableused=[]
    if len(colum)==1 and colum[0]=='*':
        for tab in tables:
            columntable[tab]=[]
            for col in metadata[tab]:
                columntable[tab].append(col)
        return columntable,tables

    for col in colum:
        if '.' in col:
            table,col=col.split('.')
            table=format(table)
            col=format(col)
        else:
            table = findtable(col,tables)
        if table not in columntable.keys():
            columntable[table]=[]
            tableused.append(table)
        columntable[table].append(col)
    return columntable,tableused



def jointable_query(tables,tabledata):
    columntable,tableused=findtablecolumn(colum,tables)
    datajoin=[]
    if(len(tables)==2):
        t1=tableused[0]
        t2=tableused[1]
        for x in tabledata[t1]:
            for y in tabledata[t2]:
                datajoin.append(x+y)
        h=''
        for col in columntable[t1]:
            h+=t1+'.'+col+','
        for col in columntable[t2]:
            h+=t2+'.'+col+','
        print(h.strip(','))
        for x in datajoin:
            ans=''
            for col in columntable[t1]:
                ans+=x[metadata[t1].index(col)]+','
            for col in columntable[t2]:
                ans+=x[metadata[t2].index(col)+len(metadata[t1])]+','
            print(ans.strip(','))
    else:
        for tab in tableused:
            h=''
            for col in columntable[tab]:
                h+=tab+'.'+col+','
            print(h.strip(','))
            for x in tabledata[tab]:
                ans=''
                for col in columntable[tab]:
                    ans+=x[metadata[tab].index(col)]+','
                print(ans.strip(','))

def singletable_query(table,tabledata):
    if len(colum)==1 and colum[0]=='*':
        columns = metadata[table]
    else:
        columns=colum
    h=''
    for col in columns:
        if col not in metadata[table]:
            printerror(col+':column not declared in table')
        h+=table+'.'+col+','
    print(h.strip(','))
    for x in tabledata[table]:
        ans=''
        for col in columns:
            ans+=x[metadata[table].index(col)]+','
        print(ans.strip(','))


def getexpr(condition,table,row):
    expr = ''
    condition = condition.split(' ')
    for x in condition:
        x = format(x)
        if x.lower()=='and' or x.lower()=='or':
            expr+=' '+x.lower()+' '
        elif '>' in x or '<' in x or '>=' in x or '<=' in x or '=' in x:
            if '>' in x:
                op='>'
            elif '<' in x:
                op='<'
            elif '<=' in x:
                op='<='
            elif '>=' in x:
                op='>='
            elif '=' in x:
                op='='
            e = x.split(op)
            if len(e)==2:
                if '.' in e[0]:
                    table,e[0] = e[0].split('.')
                    table=format(table)
                    e[0]=format(e[0])
                if e[0] in metadata[table]:
                    expr+=row[metadata[table].index(e[0])]
                else:
                    expr+=e[0]
                expr+= op
                if(op=='='):
                    expr+=op
                if '.' in e[1]:
                    table,e[1] = e[1].split('.')
                    table=format(table)
                    e[1]=format(e[1])
                if e[1] in metadata[table]:
                    expr+=row[metadata[table].index(e[1])]
                else:
                    expr+=e[1]
        elif '.' in x :
            table,col = x.split('.')
            table=format(table)
            col=format(col)
            expr+=row[metadata[table].index(col)]
        elif x in metadata[table]:
            expr+=row[metadata[table].index(x)]
        else:
            expr+=x
    return expr

def singlewhere_query(condition,table,tabledata):
    if len(colum)==1 and colum[0]=='*':
        columns = metadata[table]
    h=''
    columns=colum
    for col in columns:
        h+=table+'.'+col+','
    print(h.strip(','))
    for x in tabledata[table]:
        expr = getexpr(condition,table,x)
        res=''
        if eval(expr):
            for col in columns:
                res+=x[metadata[table].index(col)]+','
            print(res.strip(','))

def normaljoin(condition,tables,tabledata):
    dataused={}
    dataunused={}
    for x in condition[0]:
        x = format(x)
        for op in operators:
            if op in x:
                operator=op
                need=x.split(op)
                if op=='=':
                    operator+=op
                break
        colused,table = findtablecolumn(need,tables)
        c1 = metadata[tables[0]].index(colused[tables[0]][0])
        c2 = metadata[tables[1]].index(colused[tables[1]][0])
        dataused[x]=[]
        dataunused[x]=[]
        for i in tabledata[tables[0]]:
            for j in tabledata[tables[1]]:
                if eval(i[c1]+operator+j[c2]) and operator!='==':
                    dataused[x].append(i+j)
                elif eval(i[c1]+operator+j[c2]) and operator=='==':
                    temp=[]
                    for k in j:
                        if k!=j[c2]:
                            temp.append(k)
                    dataused[x].append(i+temp)

                else:
                    dataunused[x].append(i+j)
    finaldata=[]
    if condition[1]=='None':
        for k in list(dataused.keys()):
            for x in dataused[k]:
                finaldata.append(x)
    columns,tables = findtablecolumn(colum,tables)
    h=''
    for col in columns[tables[0]]:
        h+=tables[0]+'.'+col+','
    for col in columns[tables[1]]:
        if metadata[tables[1]].index(col)!=c2 or operator!='==':
            h+=tables[1]+'.'+col+','
    print(h.strip(','))
    for y in finaldata:
        res=''
        for col in columns[tables[0]]:
            res+=y[metadata[tables[0]].index(col)]+','
        for col in columns[tables[1]]:
            if metadata[tables[1]].index(col)!=c2 or operator!='==':
                res+=y[metadata[tables[1]].index(col)+len(metadata[table[0]])]+','
        print(res.strip(','))


def joinwhere_query(condition,tables,tabledata):
    joincon = condition
    if 'or' in joincon:
        joincon = joincon.split('or')
        operator='or'
    elif 'and' in joincon:
        joincon = joincon.split('and')
        operator='and'
    else:
        operator='None'
        joincon=[joincon]

    if len(joincon)>2:
        printerror('Single and,or should be used')
    subjoin = joincon[0]
    for op in operators:
        if op in subjoin:
            subjoin = subjoin.split(op)
    if len(subjoin)==2 and ('.' in subjoin[1] or subjoin[1] in metadata[tables[0]] or subjoin[1] in metadata[tables[1]]) :
        normaljoin([joincon,operator],tables,tabledata)
        return
    condata={}
    for con in joincon:
        need=[]
        for op in operators:
            if op in con:
                need=con.split(op)
                need[0]=format(need[0])
                break
        if '.' in need[0]:
            table,column = need[0].split('.')
            table=format(table)
            column = format(column)
        else:
            column=need[0]
            table = findtable(column,tables)
        condata[table]=[]
        for x in tabledata[table]:
            expr = getexpr(con,table,x)
            if eval(expr):
                condata[table].append(x)
    coldata,tableused = findtablecolumn(colum,tables)
    finaldata=[]
    t1=format(tableused[0])
    t2=format(tableused[1])
    if operator=='and':
        for x in condata[t1]:
            for y in condata[t2]:
                finaldata.append(x+y)
    elif operator=='or':
        for x in condata[t1]:
            for y in tabledata[t2]:
                if y not in condata[t2]:
                    finaldata.append(x+y)
        for x in condata[t2]:
            for y in tabledata[t1]:
                if y not in condata[t1]:
                    finaldata.append(y+x)
        for x in condata[t1]:
            for y in condata[t2]:
                finaldata.append(x+y)
    else:
        tab1 = list(condata.keys())[0]
        tab2=tables[1]
        fl=False
        if tab1==tables[1]:
            tab2=tables[0]
            fl=True
        for x in condata[tab1]:
            for y in tabledata[tab2]:
                if fl==False:
                    finaldata.append(x+y)
                else:
                    finaldata.append(y+x)
    h=''
    for col in coldata[t1]:
        h+=t1+'.'+col+','
    for col in coldata[t2]:
        h+=t2+'.'+col+','
    print(h.strip(','))
    for x in finaldata:
        res=''
        for col in coldata[t1]:
            res+=x[metadata[t1].index(col)]+','
        for col in coldata[t2]:
            res+=x[metadata[t2].index(col)+len(metadata[t1])]+','
        print(res.strip(','))

def sql_query(query):
    query = format(query)
    checkerrors(query)
    subquery = query.split('from')
    begin = format(str(subquery[0]))
    distinctsplit(begin)
    end = format(str(subquery[1]))
    tables = end.split('where')[0].split(',')
    wheresplit = end.split('where')
    tabledata={}
    for i in range(len(tables)):
        tables[i]=format(tables[i])
        if not tables[i] in metadata.keys():
            printerror(tables[i]+':No such table exists')
        tabledata[tables[i]]=readcsv(tables[i])

    columns = format(begin[len('select '):]).split(',')
    splitcolumns(columns,end)
    if len(wheresplit)>1 and len(tables)==1:
        condition = wheresplit[1]
        condition = format(condition)
        singlewhere_query(condition,tables[0],tabledata)
    elif len(wheresplit)>1 and len(tables)>1:
        condition = wheresplit[1]
        condition = format(condition)
        joinwhere_query(condition,tables,tabledata)
    elif(len(dist)!=0):
        distinct_query(tables,tabledata)
    elif len(aggre)!=0:
        aggregate_query(tables,tabledata)
    elif len(tables)>1:
        jointable_query(tables,tabledata)
    else:
        singletable_query(tables[0],tabledata)


if __name__ == '__main__':
    distfl=False
    readmetadata()
    main()
