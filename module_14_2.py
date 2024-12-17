from setup import get_cursor


cursor, connection = get_cursor()

cursor.execute("DELETE FROM Users WHERE id = 6")

total_users = cursor.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
all_balances = cursor.execute("SELECT SUM(balance) FROM Users").fetchone()[0]
print(all_balances / total_users)

connection.commit()
connection.close()
