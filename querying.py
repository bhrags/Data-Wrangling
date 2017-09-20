
# coding: utf-8

# In[66]:

import sqlite3
import csv
from pprint import pprint
import pandas as pd
import numpy as np
from time import time

sqlite_file = 'hydsample.db'

conn = sqlite3.connect(sqlite_file)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS nodes')
conn.commit()

cur.execute('''
    CREATE TABLE nodes(id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT)
''')
conn.commit()

with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['lat'],i['lon'], i['user'].decode("utf-8"), i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]
    
# insert data
cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()


conn.close()


# In[67]:

sqlite_file = 'hydsample.db'

conn = sqlite3.connect(sqlite_file)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS ways')
conn.commit()

cur.execute('''
    CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT)
''')
conn.commit()

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['user'].decode("utf-8"), i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]
    
# insert data
cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()

#cur.execute('SELECT * FROM ways')
#all_rows = cur.fetchall()
#print('1):')
#pprint(all_rows)

conn.close()


# In[68]:

sqlite_file = 'hydsample.db'

conn = sqlite3.connect(sqlite_file)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS ways_nodes')
conn.commit()

cur.execute('''
    CREATE TABLE ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id))
''')
conn.commit()

with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['node_id'],i['position']) for i in dr]
    
# insert data
cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
# commit the changes
conn.commit()

#cur.execute('SELECT * FROM ways_nodes')
#all_rows = cur.fetchall()
#print('1):')
#pprint(all_rows)

conn.close()


# In[76]:

sqlite_file = 'hydsample.db'

conn = sqlite3.connect(sqlite_file)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS ways_tags')
conn.commit()

cur.execute('''
    CREATE TABLE ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id))
''')
conn.commit()

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'],i['value'].decode("utf-8"), i['type']) for i in dr]
    
# insert data
cur.executemany("INSERT INTO ways_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()

#cur.execute('SELECT * FROM ways_tags')
#all_rows = cur.fetchall()
#print('1):')
#pprint(all_rows)



# In[84]:

sqlite_file = 'hydsample.db'

conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS nodes_tags')
conn.commit()

cur.execute("CREATE TABLE nodes_tags(id,key,value,type);")
with open ('nodes_tags.csv' , 'rb') as f:
    dic = csv.DictReader(f)
    to_db = [(i['id'].decode("utf-8"),i['key'].decode("utf-8"),i['value'].decode("utf-8"),i['type'].decode("utf-8"))
            for i in dic]
cur.executemany("INSERT INTO nodes_tags(id,key,value,type) VALUES (?,?,?,?);" , to_db)
conn.commit()


# In[85]:

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT COUNT(*) FROM nodes;
''')
results = cursor.fetchall()
print results
conn.close()


# There are 3222808 nodes

# In[86]:


conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT COUNT(*) FROM ways;
''')
results = cursor.fetchall()
print results
conn.close()


# There are 77012 ways

# In[87]:

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT Count(DISTINCT both.user)
    FROM (SELECT user FROM nodes
    UNION ALL SELECT user FROM ways) as both;
''')
results = cursor.fetchall()
print results
conn.close


# There 571 distinct users.

# In[93]:

import pandas as pd 

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute(''' SELECT value, COUNT(*) as num 
FROM (select value , key from nodes_tags UNION ALL select value, key from ways_tags)
WHERE key='religion'
GROUP BY value
ORDER BY num DESC
limit 10
;
''')
cur.execute(QUERY)
results = cur.fetchall()
df = pd.DataFrame(results)
print df
conn.close


# In[89]:

import pandas as pd 

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT both.value, COUNT(*) as Total 
    FROM (SELECT * FROM nodes_tags UNION ALL 
    SELECT * FROM ways_tags) as both
    WHERE both.key == 'postcode'
    GROUP BY both.value
    ORDER BY Total DESC
    LIMIT 5;
''')

results = cursor.fetchall()
df = pd.DataFrame(results)
print df
conn.close


# In[90]:

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT value, COUNT(*) as Total 
    FROM nodes_tags
    WHERE key == 'denomination'
    GROUP BY value
    ORDER BY Total DESC
    LIMIT 5;
''')

results = cursor.fetchall()
df = pd.DataFrame(results)
print df
conn.close


# In[91]:

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT both.value, COUNT(*) as Total 
    FROM (SELECT * FROM nodes_tags UNION ALL 
    SELECT * FROM ways_tags) as both
    WHERE both.key == 'sport'
    GROUP BY both.value
    ORDER BY Total DESC
    LIMIT 5;
''')

results = cursor.fetchall()
df = pd.DataFrame(results)
print df
conn.close


# In[92]:

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()
cursor.execute('''
    SELECT both.value, COUNT(*) as Total 
    FROM (SELECT * FROM nodes_tags UNION ALL 
    SELECT * FROM ways_tags)
    as both
    WHERE both.key == 'cuisine'
    GROUP BY both.value
    ORDER BY Total DESC
    LIMIT 5;
''')

results = cursor.fetchall()
df = pd.DataFrame(results)
print df
conn.close


# In[94]:

QUERY ='''SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key LIKE '%city'
GROUP BY tags.value
ORDER BY count DESC;'''

cur.execute(QUERY)
all_cITIES = cur.fetchall()
df = pd.DataFrame(all_cITIES)
print "number of places :", len(df)


# In[95]:

QUERY =''' SELECT user,count(user) from( select user from nodes UNION ALL select user from ways)
GROUP BY user
ORDER BY count(user)
DESC;
'''
cur.execute(QUERY)
all_unique_users = cur.fetchall()
import pandas as pd
df = pd. DataFrame(all_unique_users)
print df[1].describe()
print('\n')
print "Total users:" , df[1].sum()


# Advantages and Disadvantages : The main advantage is that Open Street Map data is open-source and therefore free to use. This means anyone can use the data to create their own maps (and then use services like Map Box to generate and host customised map tiles). This means the developer doesn't have to work within Google's constraints. The only imaginable downside to me is quality. Get me right, 99% is the good stuff, but as all crowd sourced data it's hard to maintain consistent quality control. Of course is free to alter and complete the data, but there's no guarantees as there would with a company behind it.
# 

# Conclusion: After series of iterations in Auditing process, I believe that the data has been cleaned precisely and analysed well in exploration phase .

# In[ ]:



