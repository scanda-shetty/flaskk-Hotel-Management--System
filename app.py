from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import json
from json import loads
app = Flask(__name__)
app.secret_key ="jusfondiaxylliphyte" 
@app.route('/')
def login():
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3308,
        database="hotel"
    )
    mycursor = mydb.cursor()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        print("Name:", name)
        print("Email:", email)
        print("Password:", password)


        # Use parameterized query to prevent SQL injection
        query = "INSERT INTO admin (name, email, password) VALUES (%s, %s, %s)"
        mycursor.execute(query, (name, email, password))

        mydb.commit()
        mydb.close()

        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/reset', methods=['POST', 'GET'])
def reset_password():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Replace with your database password
        port=3308,      # Replace with your MySQL server port
        database="hotel"
    )
    mycursor = mydb.cursor()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Update the user's password in the database
        update_query = "UPDATE admin SET password = %s WHERE email = %s"
        mycursor.execute(update_query, (password, email))
        mydb.commit()
        mydb.close()
        return redirect(url_for('login'))
    return render_template("register.html")
    

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3308,
        database="hotel"
    )
    mycursor = mydb.cursor()

    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')

        query = "SELECT * FROM admin WHERE name = %s AND password = %s"
        mycursor.execute(query, (username, password))

        r = mycursor.fetchall()
        count = mycursor.rowcount
        if count == 1:
            session['user'] = username
            if username == 'Admin1':
                session['admin_id'] = 1
            else:
                session['admin_id'] = 0
            return render_template("home.html")
        elif count > 1:
            return "More than 1 user"
        else:
            return render_template("login.html", is_admin=is_admin())

    mydb.commit()
    mycursor.close()


def is_authenticated():
    return 'user' in session

# Authorization function to check if a user has admin privileges (user_id == 1)
def is_admin():
    result = is_authenticated() and session.get('admin_id') == 1
    print("is_admin result:", result)  # Add this debugging statement
    return result

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove 'user' key from the session
    return redirect(url_for('login'))


@app.route('/room_info', methods=['GET', 'POST'])
def room_info():
    if 'user' in session:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3308,
            database="hotel"
        )
        mycursor = mydb.cursor()

        total_rooms = """
            SELECT COUNT(DISTINCT Room_No) AS total_rooms_occupied
            FROM all_bookings
            WHERE Checkin_Date <= CURDATE() AND Checkout_Date > CURDATE();
            """
        mycursor.execute(total_rooms)
        result = mycursor.fetchone()[0]  # Fetch the result


        total_revenue = """
SELECT SUM(Total_Amount) AS total_revenue
FROM all_bookings
WHERE MONTH(Checkout_Date) = MONTH(CURDATE());

            """
        mycursor.execute(total_revenue)
        result1 = mycursor.fetchone()[0]


        Ac = request.form.get('Ac')
        Price = request.form.get('Price')

        check_in_date_str = request.form.get('Checkin_Date')
        check_out_date_str = request.form.get('Checkout_Date')

        # Initialize variables for datetime objects
        check_in_date = None
        check_out_date = None

        # Convert date strings to datetime objects if they are not None
        if check_in_date_str:
            check_in_date = datetime.strptime(check_in_date_str, "%Y-%m-%d")
        if check_out_date_str:
            check_out_date = datetime.strptime(check_out_date_str, "%Y-%m-%d")

        # Debugging: Print the values of check-in and check-out dates
        print("Check-in Date:", check_in_date)
        print("Check-out Date:", check_out_date)

        # Check if any filters were selected
        filters_selected = any(filter_value is not None for filter_value in [Ac, Price])

        # Build the SQL query based on the selected filters and date range
        query = "SELECT * FROM room WHERE 1"
        if Ac:
            query += f" AND Ac = {Ac}"
        if Price:
            query += f" AND Price <= {Price}"

        mycursor.execute(query)
        rooms_data = mycursor.fetchall()

        # Debugging: Print the rooms_data to see the retrieved data
        print("Rooms Data:", rooms_data)

        # Filter rooms that are available for the specified date range
        available_rooms = []
        for room in rooms_data:
            # Debugging: Print the room details to check the format of room_reserved_dates
            print("Room:", room)
            room_reserved_dates_json = room[5]

            if room_reserved_dates_json is not None:
                # Attempt to load JSON data
                reserved_dates = json.loads(room_reserved_dates_json)
            else:
                # Handle the case where the data is None or incorrect
                reserved_dates = []

            is_available = True
            for reserved_date in reserved_dates:
                # Check if the date strings are not None before comparing
                if check_in_date and check_out_date:
                    reserved_check_in = datetime.strptime(reserved_date['check_in_date'], "%d-%m-%Y")
                    reserved_check_out = datetime.strptime(reserved_date['check_out_date'], "%d-%m-%Y")
                    if (check_in_date <= reserved_check_out and check_out_date >= reserved_check_in):
                        is_available = False
                        break

            if is_available:
                available_rooms.append(room)

        mydb.close()

        # Debugging: Print the available rooms
        print("Available Rooms:", available_rooms)
        return render_template("room.html", room_data=available_rooms, result=result, result1=result1, filters_selected=filters_selected, Ac=Ac, Price=Price, is_admin=is_admin())
    
    else:
        return render_template("login.html")


@app.route('/update_room', methods=['POST'])
def update_room():
    if 'user' in session and is_admin():
        if request.method == 'POST':
            roomID = request.form.get('roomID')
            newDescription = request.form.get('newDescription')
            newPrice = request.form.get('newPrice')
            newAc = request.form.get('newAc')

            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    port=3308,
                    database="hotel"
                )
                cursor = connection.cursor()

                print(f"roomID: {roomID}")
                print(f"newDescription: {newDescription}")
                print(f"newPrice: {newPrice}")
                print(f"newAc: {newAc}")

                # Check if the procedure call is working
                cursor.callproc("UpdateRoomInfo", (roomID, newDescription, newPrice, newAc))
                connection.commit()

                print('Room information updated successfully', 'success')
            except mysql.connector.Error as err:
                print(f'Error: {err}', 'error')
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        return render_template("room.html")
    else:
        return render_template("login.html")



# @app.route('/customer_info', methods=['GET', 'POST'])
# def customer_info():
#     if is_admin():
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             port=3308,
#             database="hotel"
#         )
#         mycursor = mydb.cursor()

#         # Get filter values from the form
#         fname = request.form.get('fname')
#         lname = request.form.get('lname')

#         # Check if any filters were selected
#         filters_selected = any(filter_value is not None for filter_value in [fname, lname])

#         # Build the SQL query based on the selected filters
#         query = "SELECT * FROM Customer WHERE 1"
#         if fname:
#             query += f" AND fname LIKE '%{fname}%'"
#         if lname:
#             query += f" AND lname LIKE '%{lname}%'"

#         mycursor.execute(query)
#         customer_data = mycursor.fetchall()

#         mydb.close()

#         return render_template("customer.html", customer_data=customer_data, filters_selected=filters_selected, fname=fname, lname=lname)
#     else:
#         return render_template("login.html")
def get_customer_data(fname, lname):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3308,
        database="hotel"
    )
    mycursor = mydb.cursor()

    # Build the SQL query based on the selected filters
    query = "SELECT * FROM Customer WHERE 1"
    if fname:
        query += f" AND fname LIKE '%{fname}%'"
    if lname:
        query += f" AND lname LIKE '%{lname}%'"

    mycursor.execute(query)
    customer_data = mycursor.fetchall()

    mydb.close()

    return customer_data

@app.route('/customer_info', methods=['GET', 'POST'])
def customer_info():
    if is_admin():
        # Handle form submission for filters
        if request.method == 'POST':
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            filter_option = request.form.get('filter_option', '')  
            # Check the selected filter option
            #1) Highest Spenders
            if filter_option == 'Highest Spenders':
                # Execute SQL query for Highest Spenders
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    port=3308,
                    database="hotel"
                )
                mycursor = mydb.cursor()

                query = """
        SELECT c.Cus_id, c.email, c.fname, c.lname, c.Age,
       (SELECT SUM(ab.Total_Amount) FROM all_bookings ab WHERE ab.cus_id = c.Cus_id) AS total_spending
FROM customer c
ORDER BY total_spending DESC;

                """
                mycursor.execute(query)
                customer_data = mycursor.fetchall()

                mydb.close()

                # Render the template with the query results
                return render_template("customer.html", customer_data=customer_data, filters_selected=True, fname=fname, lname=lname, order="", filter_option= filter_option)

            # 2)Most Reservations
            if filter_option == 'Most Reservations':
                # Execute SQL query for Most Reservations
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    port=3308,
                    database="hotel"
                )
                mycursor = mydb.cursor()

                query = """
    SELECT c.Cus_id, c.email, c.fname, c.lname, c.Age,
    COUNT(ab.Reservation_id) AS total_bookings
FROM customer c
LEFT JOIN all_bookings ab ON c.Cus_id = ab.cus_id
GROUP BY c.Cus_id, c.fname, c.lname
ORDER BY total_bookings DESC;


                """
                mycursor.execute(query)
                customer_data = mycursor.fetchall()

                mydb.close()

                # Render the template with the query results
                return render_template("customer.html", customer_data=customer_data, filters_selected=True, fname=fname, lname=lname, order="", filter_option= filter_option)

            # If no special filter is selected, proceed with the default behavior
            customer_data = get_customer_data(fname, lname)
            filters_selected = any(filter_value is not None for filter_value in [fname, lname])

            return render_template("customer.html", customer_data=customer_data, filters_selected=filters_selected, fname=fname, lname=lname, order="")

            customer_data = get_customer_data(fname, lname)
            filters_selected = any(filter_value is not None for filter_value in [fname, lname])

            return render_template("customer.html", customer_data=customer_data, filters_selected=filters_selected, fname=fname, lname=lname, order="")

        # Handle sorting based on table headers
        elif request.method == 'GET':
            selected_column = request.args.get('selected_column')
            order = request.args.get('order', 'asc')

            if selected_column:
                customer_data = get_customer_data("", "")

                # Sort the data based on the selected column and order
                if selected_column in ['Customer_ID', 'Email', 'First_Name', 'Last_Name', 'Age', 'Address']:
                    index = ['Customer_ID', 'Email', 'First_Name', 'Last_Name', 'Age', 'Address'].index(selected_column)
                    customer_data = sorted(customer_data, key=lambda x: x[index], reverse=(order == 'desc'))

                return render_template("customer.html", customer_data=customer_data, filters_selected=False, fname="", lname="", order=order)

        # Render the initial template
        return render_template("customer.html", customer_data=[], filters_selected=False, fname="", lname="", order="")
    else:
        return render_template("login.html")


@app.route('/booking_details/<int:cus_id>')
def booking_details(cus_id):
    if is_admin():
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3308,
            database="hotel"
        )
        mycursor = mydb.cursor()

        # Query all information from the all_bookings table based on cus_id
        query = f"SELECT * FROM all_bookings WHERE cus_id = {cus_id}"
        mycursor.execute(query)
        bookings_data = mycursor.fetchall()
        mydb.close()
        return render_template('booking_details.html', bookings_data=bookings_data)
    else:
        return render_template("login.html")




@app.route('/make_reservation', methods=['POST', 'GET'])
def make_reservation():
    if 'user' in session:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            port=3308,
            database="hotel"
        )
        mycursor = mydb.cursor()

        if request.method == 'POST':
            email = request.form.get('email')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            Age = request.form.get('Age')
            Address = request.form.get('Address')
            Room_No = request.form.get('Room_No')
            Amount = request.form.get('Amount')
            Checkin_Date = request.form.get('Checkin_Date')
            Checkout_Date = request.form.get('Checkout_Date')
            # Check if the room is available during the specified date range
            mycursor.execute("SELECT room_reserved_dates FROM room WHERE Room_No = %s", (Room_No,))
            room_reserved_dates_json = mycursor.fetchone()[0]

            if room_reserved_dates_json is None:
                # Initialize room_reserved_dates as an empty list
                reserved_dates = []
            else:
                reserved_dates = json.loads(room_reserved_dates_json)

            is_available = True
            for reserved_date in reserved_dates:
                reserved_check_in = reserved_date['check_in_date']
                reserved_check_out = reserved_date['check_out_date']

                if (Checkin_Date <= reserved_check_out and Checkout_Date >= reserved_check_in):
                    is_available = False
                    break

            if is_available:
                # Insert customer information into the Customer table
                mycursor.execute(
                    "INSERT INTO Customer (email, fname, lname, Age, Address) VALUES (%s, %s, %s, %s, %s)",
                    (email, fname, lname, Age, Address)
                )
                cus_id = mycursor.lastrowid  # Get the generated customer ID

                # Update the Reservation table
                mycursor.execute(
                    "INSERT INTO Reservation (Cus_ID, Room_No, Amount, Checkin_Date, Checkout_Date) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (cus_id, Room_No, Amount, Checkin_Date, Checkout_Date)
                )

                # Update the room_reserved_dates column in the Room table
                reserved_dates.append({
                    "check_in_date": Checkin_Date,
                    "check_out_date": Checkout_Date
                })
                updated_reserved_dates_json = json.dumps(reserved_dates)

                mycursor.execute("UPDATE room SET room_reserved_dates = %s WHERE Room_No = %s",
                                (updated_reserved_dates_json, Room_No))

                mydb.commit()
                mydb.close()
                return "Reservation successfully made!"
            else:
                mydb.close()
                return "Room not available for reservation."

        mydb.close()
        return render_template("make_reservation.html", is_admin=is_admin())
    else:
        return render_template("login.html")

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if 'user' in session and is_admin():
        if request.method == 'POST':
            Reservation_id = request.form.get('Reservation_id')
            cus_id = request.form.get('cus_id')
            Room_No = request.form.get('Room_No')
            Checkout_Date = request.form.get('Checkout_Date')

            try:
                # Calculate the total amount using the CalculateAmount procedure
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    port=3308,
                    database="hotel"
                )
                cursor = connection.cursor()
                
                totalAmount = 1  # Initialize the total amount
                
                # Call the CalculateAmount procedure
                cursor.callproc("CalculateAmount", (Reservation_id, totalAmount))
                
                # Get the calculated total amount from the OUT parameter
                cursor.execute("SELECT @totalAmount;")
                totalAmount = cursor.fetchone()[0]

                # Insert payment records into the Payment table using the modified InsertPayment procedure
                cursor.callproc("InsertPayment", (Reservation_id, totalAmount))
                
                # Commit the changes
                connection.commit()
                
                # Close the connection
                connection.close()
                flash("Chesckout successfull!")

                return render_template("home.html")

            except mysql.connector.Error as err:
                return "Error: " + str(err)
            
        return render_template("checkout.html")
    else:
        return render_template("login.html")



if __name__ == '__main__':
    app.run(debug=True)
