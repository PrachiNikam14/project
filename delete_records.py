import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('share_a_meal.db')
cursor = conn.cursor()

# Delete all records from a table (replace 'table_name' with your actual table name)
cursor.execute('DELETE FROM id;')

# Commit changes
conn.commit()

# Close the connection
conn.close()
print("All records deleted from NGO table.")

# import sqlite3

# # Connect to the database
# conn = sqlite3.connect('share_a_meal.db')  # Replace with your database name
# cursor = conn.cursor()

# # Execute query to fetch all table names
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# # Fetch all results
# tables = cursor.fetchall()

# # Print table names
# print("Tables in the database:")
# for table in tables:
#     print(table[0])

# # Close the connection
# conn.close()
