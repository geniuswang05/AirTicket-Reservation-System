from flask import Flask, render_template, request, url_for, redirect, session, flash
import mysql.connector
from datetime import datetime, timedelta
from flask import jsonify

app = Flask(__name__)

# Configure MySQL connection function
def getConnect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="air_reservation"  # Keep your database name
    )

# Get a global connection for simple queries
conn = getConnect()

# Home route
@app.route('/')
def hello():
    if 'username' in session:
        user_type = session.get('user_type')
        if user_type == 'customer':
            return redirect(url_for('customer_home'))
        elif user_type == 'staff':
            return redirect(url_for('staff_home'))
        elif user_type == 'agent':
            return redirect(url_for('agent_home'))
    return render_template('index.html')

# CUSTOMER ROUTES
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    return render_template('customer_login.html')

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        building_number = request.form.get('building_number', '')
        street = request.form.get('street', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        phone_number = request.form.get('phone_number', '')
        passport_number = request.form.get('passport_number', '')
        passport_expiration = request.form.get('passport_expiration', '')
        passport_country = request.form.get('passport_country', '')
        date_of_birth = request.form.get('date_of_birth', '')
        
        print(f"DEBUG - Registration attempt: {email}, {name}")
        
        conn = getConnect()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if email already exists
            query = "SELECT * FROM customer WHERE email = %s"
            cursor.execute(query, (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                error = "Email already registered"
                return render_template('customer_register.html', error=error)

            # Insert new customer - adapted for professor's schema
            insert = """
                INSERT INTO customer (email, name, password, building_number, street, 
                city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert, (email, name, password, building_number, street, 
                city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
            conn.commit()
            
            session.clear()
            session['username'] = email
            session['display_name'] = name 
            session['user_type'] = 'customer'
            
            print(f"DEBUG - Registration successful: {email}, {name}")
            
            flash("Registration successful! Welcome to our Air Ticket Reservation System.")
            return redirect(url_for('hello'))
            
        except Exception as e:
            print(f"DEBUG - Registration error: {str(e)}")
            conn.rollback()
            error = f"Registration failed: {str(e)}"
            return render_template('customer_register.html', error=error)
        finally:
            cursor.close()
            conn.close()

    return render_template('customer_register.html')

@app.route('/customer/loginAuth', methods=['GET', 'POST'])
def customer_loginAuth():
    email = request.form['email address']
    password = request.form['password']

    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM customer WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if data:
        session['username'] = data['email']
        session['user_type'] = 'customer'
        session['display_name'] = data['name']
        return redirect(url_for('hello'))
    else:
        error = 'Invalid email or password'
        return render_template('customer_login.html', error=error)

@app.route('/customer_search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        source = request.form['source'].strip()
        destination = request.form['destination'].strip()
        date = request.form['date']

        print(f"DEBUG - Searching for: source={source}, destination={destination}, date={date}")

        conn = getConnect()
        cursor = conn.cursor(dictionary=True)
        
        # First, try to debug by listing all flights for that date
        debug_query = """
            SELECT COUNT(*) as flight_count 
            FROM flight 
            WHERE DATE(departure_time) = %s
        """
        cursor.execute(debug_query, (date,))
        debug_result = cursor.fetchone()
        print(f"DEBUG - Total flights on {date}: {debug_result['flight_count'] if debug_result else 'unknown'}")
        
        # More flexible query with airport matching
        query = """
            SELECT a.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
                  f.departure_time, f.arrival_time, f.price, f.status
            FROM flight f
            JOIN airline a ON f.airline_name = a.airline_name
            WHERE f.departure_airport = %s 
              AND f.arrival_airport = %s 
              AND DATE(f.departure_time) = %s
        """
        # Removed the f.departure_time > NOW() condition
        
        cursor.execute(query, (source, destination, date))
        results = cursor.fetchall()
        
        # If no results with exact match, try joining with airport table
        if not results:
            print("DEBUG - No results with exact match, trying with airport city")
            city_query = """
                SELECT a.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
                      f.departure_time, f.arrival_time, f.price, f.status
                FROM flight f
                JOIN airline a ON f.airline_name = a.airline_name
                JOIN airport dep ON f.departure_airport = dep.airport_name
                JOIN airport arr ON f.arrival_airport = arr.airport_name
                WHERE (dep.airport_name = %s OR dep.airport_city = %s)
                  AND (arr.airport_name = %s OR arr.airport_city = %s)
                  AND DATE(f.departure_time) = %s
            """
            cursor.execute(city_query, (source, source, destination, destination, date))
            results = cursor.fetchall()
        
        print(f"DEBUG - Query returned {len(results)} flights")
        cursor.close()
        conn.close()
        
        return render_template('search_results.html', flights=results)
    
    return render_template('search.html')

@app.route('/view_my_flights', methods=['GET', 'POST'])
def view_my_flights():
    if 'username' not in session:
        return redirect(url_for('customer_login'))
        
    customer_email = session['username']
    from_date = request.form.get('from_date') if request.method == 'POST' else None
    to_date = request.form.get('to_date') if request.method == 'POST' else None
    source = request.form.get('source') if request.method == 'POST' else None
    destination = request.form.get('destination') if request.method == 'POST' else None

    # Adapted for professor's schema with purchases table
    query = """
        SELECT f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport,
               f.departure_time, f.arrival_time, f.status, f.price
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s
    """
    params = [customer_email]

    if from_date:
        query += " AND DATE(f.departure_time) >= %s"
        params.append(from_date)
    else:
        # Default: only show future flights
        query += " AND f.departure_time >= NOW()"

    if to_date:
        query += " AND DATE(f.departure_time) <= %s"
        params.append(to_date)

    if source:
        query += " AND f.departure_airport LIKE %s"
        params.append(f"%{source}%")

    if destination:
        query += " AND f.arrival_airport LIKE %s"
        params.append(f"%{destination}%")

    query += " ORDER BY f.departure_time ASC"

    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('my_flights.html', flights=flights)

@app.route('/purchase_ticket', methods=['POST'])
def purchase_ticket():
    if 'username' not in session:
        return redirect(url_for('customer_login'))
    
    airline_name = request.form.get('airline_name')
    flight_num = request.form.get('flight_num')
    customer_email = session['username']
    
    print(f"DEBUG - Purchase ticket: airline={airline_name}, flight={flight_num}, email={customer_email}")
    
    if not airline_name or not flight_num or not customer_email:
        message = "Invalid flight or user data."
        return redirect(url_for('customer_home', banner=message))

    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Validate flight exists - adapted for professor's schema
        cursor.execute("SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s", 
                      (airline_name, flight_num))
        if not cursor.fetchone():
            message = "Invalid flight number."
            return redirect(url_for('customer_home', banner=message))

        # Check if ticket already exists - adapted for professor's schema
        check_query = """
            SELECT t.ticket_id 
            FROM ticket t 
            JOIN purchases p ON t.ticket_id = p.ticket_id
            WHERE t.airline_name = %s AND t.flight_num = %s AND p.customer_email = %s
        """
        cursor.execute(check_query, (airline_name, flight_num, customer_email))
        if cursor.fetchone():
            message = "You have already purchased this ticket."
            return redirect(url_for('customer_home', banner=message))
            
        # Get next ticket_id
        cursor.execute("SELECT MAX(ticket_id) AS max_id FROM ticket")
        result = cursor.fetchone()
        new_ticket_id = 1  # Default if no tickets exist
        if result and result['max_id']:
            new_ticket_id = result['max_id'] + 1
        
        # Get current date for purchase_date
        current_date = datetime.today().strftime('%Y-%m-%d')
        
        # Insert new ticket with all required fields - adapted for professor's schema
        # First create the ticket
        ticket_query = """
            INSERT INTO ticket (ticket_id, airline_name, flight_num) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(ticket_query, (new_ticket_id, airline_name, flight_num))
        
        # Then create the purchase record
        purchase_query = """
            INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(purchase_query, (new_ticket_id, customer_email, None, current_date))
        
        conn.commit()
        message = "Ticket purchased successfully!"
        
    except Exception as e:
        print(f"DEBUG - Error in purchase_ticket: {e}")
        conn.rollback()
        message = f"Failed to purchase ticket: {str(e)}"
    finally:
        cursor.close()
        conn.close()
    
    # Redirect to customer_home which will fetch fresh data
    return redirect(url_for('customer_home', banner=message))

@app.route('/track_spending')
def track_spending():
    if 'username' not in session or session['user_type'] != 'customer':
        return redirect(url_for('customer_login'))
    
    return render_template('spending_chart.html')

@app.route('/chartCus', methods=['GET', 'POST'])
def chartCus():
    if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
        return redirect(url_for('get_spending_data'))
    
    if 'username' not in session:
        return redirect(url_for('customer_login'))
        
    customer_email = session['username']
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify customer exists
        query = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query, (customer_email,))
        customer = cursor.fetchone()
        
        if not customer:
            return render_template('chartCus.html', 
                                  error=f"Customer with email '{customer_email}' not found in database.", 
                                  nonemp=0)
        
        # Calculate date ranges
        today = datetime.today()
        end_date = today.strftime('%Y-%m-%d')
        start_date_year = (today - timedelta(days=1095)).strftime('%Y-%m-%d')
        start_date_6m = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        
        # Modified query for professor's schema
        monthly_query = """
        SELECT MONTH(p.purchase_date) AS month, SUM(f.price) AS monthly_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        GROUP BY MONTH(p.purchase_date)
        ORDER BY MONTH(p.purchase_date)
        """
        
        cursor.execute(monthly_query, (customer_email, start_date_6m, end_date))
        monthly_data = cursor.fetchall()
        
        # Get total yearly spending
        total_query = """
        SELECT SUM(f.price) AS total_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        """
        cursor.execute(total_query, (customer_email, start_date_year, end_date))
        total_result = cursor.fetchone()
        
        # Process total spent
        total_spent = 0
        if total_result and 'total_spent' in total_result and total_result['total_spent']:
            total_spent = float(total_result['total_spent'])
        
        # If no monthly data found, try broader date range as fallback
        if not monthly_data:
            cursor.execute(monthly_query, (customer_email, start_date_year, end_date))
            monthly_data = cursor.fetchall()
        
        # Process monthly data
        if monthly_data:
            months = []
            spent = []
            height = []
            
            for item in monthly_data:
                months.append(item['month'])
                monthly_amount = float(item['monthly_spent']) if item['monthly_spent'] else 0
                spent.append(monthly_amount)
            
            # Calculate heights for bars
            max_spent = max(spent) if spent else 1
            for amount in spent:
                percent = int((amount / max_spent) * 100) if max_spent > 0 else 0
                height.append(f"height:{percent}%")
            
            length = len(months)
            return render_template('chartCus.html', 
                                  month=months, 
                                  spent=spent, 
                                  height=height, 
                                  length=length, 
                                  allyear=total_spent,
                                  nonemp=1)
        else:
            # Check if any tickets exist
            direct_query = """
            SELECT COUNT(*) as ticket_count 
            FROM purchases 
            WHERE customer_email = %s
            """
            cursor.execute(direct_query, (customer_email,))
            ticket_count = cursor.fetchone()
            
            if ticket_count and ticket_count['ticket_count'] > 0:
                return render_template('chartCus.html', 
                                    allyear=total_spent,
                                    error="Records exist but no monthly spending data could be calculated. Check date formats in your database.",
                                    nonemp=0)
            else:
                return render_template('chartCus.html', 
                                    allyear=total_spent,
                                    error="No spending data available. You haven't purchased any tickets yet.",
                                    nonemp=0)
    
    except Exception as e:
        print(f"DEBUG - Exception: {str(e)}")
        return render_template('chartCus.html', 
                              error=f"An error occurred: {str(e)}", 
                              nonemp=0)
    finally:
        cursor.close()
        conn.close()

@app.route('/chartCusDate', methods=['GET', 'POST'])
def chartCusDate():
    if 'username' not in session:
        return redirect(url_for('customer_login'))
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    customer_email = session['username']
    
    if not start_date or not end_date:
        return render_template('chartCus.html', 
                              error="Please provide both start and end dates.", 
                              nonemp=0)
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify customer exists
        query = "SELECT * FROM customer WHERE email = %s"
        cursor.execute(query, (customer_email,))
        customer = cursor.fetchone()
        
        if not customer:
            return render_template('chartCus.html', 
                                  error=f"Customer with email '{customer_email}' not found in database.", 
                                  nonemp=0)
        
        # Monthly spending query - adapted for professor's schema
        monthly_query = """
        SELECT MONTH(p.purchase_date) AS month, SUM(f.price) AS monthly_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        GROUP BY MONTH(p.purchase_date)
        ORDER BY MONTH(p.purchase_date)
        """
        
        cursor.execute(monthly_query, (customer_email, start_date, end_date))
        monthly_data = cursor.fetchall()
        
        # Get total spending for this date range
        total_query = """
        SELECT SUM(f.price) AS total_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        """
        cursor.execute(total_query, (customer_email, start_date, end_date))
        total_result = cursor.fetchone()
        
        # Process total spent
        total_spent = 0
        if total_result and 'total_spent' in total_result and total_result['total_spent']:
            total_spent = float(total_result['total_spent'])
        
        # Process monthly data
        if monthly_data:
            months = []
            spent = []
            height = []
            
            for item in monthly_data:
                months.append(item['month'])
                monthly_amount = float(item['monthly_spent']) if item['monthly_spent'] else 0
                spent.append(monthly_amount)
            
            # Calculate heights for bars
            max_spent = max(spent) if spent else 1
            for amount in spent:
                percent = int((amount / max_spent) * 100) if max_spent > 0 else 0
                height.append(f"height:{percent}%")
            
            length = len(months)
            return render_template('chartCus.html', 
                                  month=months, 
                                  spent=spent, 
                                  height=height, 
                                  length=length, 
                                  allyear=total_spent,
                                  nonemp=1)
        else:
            # Check if any tickets exist in this date range
            direct_query = """
            SELECT COUNT(*) as ticket_count 
            FROM purchases
            WHERE customer_email = %s
            AND purchase_date >= %s 
            AND purchase_date <= %s
            """
            cursor.execute(direct_query, (customer_email, start_date, end_date))
            ticket_count = cursor.fetchone()
            
            if ticket_count and ticket_count['ticket_count'] > 0:
                return render_template('chartCus.html', 
                                    allyear=total_spent,
                                    error=f"Records exist but no monthly spending data could be calculated for the selected date range ({start_date} to {end_date}).",
                                    nonemp=0)
            else:
                return render_template('chartCus.html', 
                                    allyear=total_spent,
                                    error=f"No spending data found for the selected date range ({start_date} to {end_date}).",
                                    nonemp=0)
    
    except Exception as e:
        print(f"DEBUG - Exception in chartCusDate: {str(e)}")
        return render_template('chartCus.html', 
                              error=f"An error occurred: {str(e)}", 
                              nonemp=0)
    finally:
        cursor.close()
        conn.close()

@app.route('/api/spending_data', methods=['GET'])
def get_spending_data():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    customer_email = session['username']
    
    # Calculate date ranges
    today = datetime.today()
    end_date = today.strftime('%Y-%m-%d')
    start_date_6m = (today - timedelta(days=180)).strftime('%Y-%m-%d')
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get monthly spending data - adapted for professor's schema
        monthly_query = """
        SELECT MONTH(p.purchase_date) AS month, SUM(f.price) AS monthly_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        GROUP BY MONTH(p.purchase_date)
        ORDER BY MONTH(p.purchase_date)
        """
        cursor.execute(monthly_query, (customer_email, start_date_6m, end_date))
        monthly_data = cursor.fetchall()
        
        # Get total spending
        total_query = """
        SELECT SUM(f.price) AS total_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        """
        cursor.execute(total_query, (customer_email, start_date_6m, end_date))
        total_result = cursor.fetchone()
        
        # Format the data for the frontend
        formatted_data = []
        for item in monthly_data:
            formatted_data.append({
                'month': item['month'],
                'spent': float(item['monthly_spent']) if item['monthly_spent'] else 0
            })
            
        total_spent = float(total_result['total_spent']) if total_result and total_result['total_spent'] else 0
        
        return jsonify({
            'monthlyData': formatted_data,
            'totalSpent': total_spent
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/spending_data/filtered', methods=['POST'])
def get_filtered_spending_data():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    customer_email = session['username']
    
    if not start_date or not end_date:
        return jsonify({'error': 'Start and end dates are required'}), 400
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get filtered monthly spending data - adapted for professor's schema
        monthly_query = """
        SELECT MONTH(p.purchase_date) AS month, SUM(f.price) AS monthly_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        GROUP BY MONTH(p.purchase_date)
        ORDER BY MONTH(p.purchase_date)
        """
        cursor.execute(monthly_query, (customer_email, start_date, end_date))
        monthly_data = cursor.fetchall()
        
        # Get total spending for filtered range
        total_query = """
        SELECT SUM(f.price) AS total_spent 
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s 
        AND p.purchase_date >= %s 
        AND p.purchase_date <= %s
        """
        cursor.execute(total_query, (customer_email, start_date, end_date))
        total_result = cursor.fetchone()
        
        # Format the data
        formatted_data = []
        for item in monthly_data:
            formatted_data.append({
                'month': item['month'],
                'spent': float(item['monthly_spent']) if item['monthly_spent'] else 0
            })
            
        total_spent = float(total_result['total_spent']) if total_result and total_result['total_spent'] else 0
        
        return jsonify({
            'monthlyData': formatted_data,
            'totalSpent': total_spent
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/customer/home')
def customer_home():
    if 'username' not in session or session['user_type'] != 'customer':
        return redirect(url_for('customer_login'))
    
    username = session['username']
    display_name = session.get('display_name', username)
    banner = request.args.get('banner')  # Get banner message from URL parameter
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Count upcoming flights
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s AND f.departure_time > NOW()
        """, (username,))
        result = cursor.fetchone()
        upcoming_flights_count = result['count'] if result else 0
        
        # Calculate total spent
        cursor.execute("""
            SELECT SUM(f.price) as total 
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s
        """, (username,))
        result = cursor.fetchone()
        total_spent = float(result['total']) if result and result['total'] else 0
        
        # Get next flight date
        cursor.execute("""
            SELECT f.departure_time
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s AND f.departure_time > NOW()
            ORDER BY f.departure_time ASC
            LIMIT 1
        """, (username,))
        result = cursor.fetchone()
        next_flight_date = result['departure_time'].strftime('%Y-%m-%d') if result else 'No flights'
        
        return render_template('customer_home.html', 
                              username=username, 
                              display_name=display_name,
                              upcoming_flights_count=upcoming_flights_count,
                              total_spent=total_spent,
                              next_flight_date=next_flight_date,
                              banner=banner)  # Pass banner to template
    
    except Exception as e:
        print(f"DEBUG - Error in customer_home: {str(e)}")
        return render_template('customer_home.html', 
                              username=username, 
                              display_name=display_name,
                              error=f"Error loading dashboard: {str(e)}",
                              banner=banner)  # Pass banner even if error occurs
    finally:
        cursor.close()
        conn.close()

# BOOKING AGENT ROUTES
@app.route('/agent/login')
def agent_login():
    return render_template('agent_login.html')

@app.route('/agent/register', methods=['GET', 'POST'])
def agent_register():
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    # Fetch list of airlines for the dropdown - adapted for professor's schema
    cursor.execute("SELECT airline_name FROM airline")
    airlines = cursor.fetchall()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        agent_id = request.form['booking_agent_id']
        airline_names = request.form.getlist("airline_name[]")

        print(f"DEBUG - Agent registration attempt: email={email}, id={agent_id}, airlines={airline_names}")

        # Validate at least one airline was selected
        if not airline_names:
            print(f"DEBUG - No airlines selected")
            error = "Please select at least one airline"
            return render_template('agent_register.html', error=error,
                               email=email, agent_id=agent_id,
                               airlines=airlines)

        try:
            # Check if email already exists
            query = "SELECT * FROM booking_agent WHERE email = %s"
            cursor.execute(query, (email,))
            existing_agent = cursor.fetchone()
            if existing_agent:
                print(f"DEBUG - Agent already exists: {existing_agent}")
                error = "Email already registered"
                return render_template('agent_register.html', error=error,
                                   email=email, agent_id=agent_id,
                                   airline_name=airline_names, airlines=airlines)

            try:
                # Parse agent_id as integer
                agent_id_int = int(agent_id)
                
                # Insert new agent - adapted for professor's schema
                insert_agent = """
                    INSERT INTO booking_agent (email, password, booking_agent_id)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_agent, (email, password, agent_id_int))
                
                # Insert airline relationships - adapted for professor's schema
                insert_relation = """
                    INSERT INTO booking_agent_work_for (email, airline_name)
                    VALUES (%s, %s)
                """
                for airline_name in airline_names:
                    print(f"DEBUG - Adding airline association: {email} -> {airline_name}")
                    cursor.execute(insert_relation, (email, airline_name))
                
                conn.commit()
                
                # Save session data
                session['username'] = email
                session['user_type'] = 'agent'
                return redirect(url_for('agent_home'))
            
            except ValueError:
                conn.rollback()
                error = "Booking Agent ID must be a valid number"
                print(f"DEBUG - Invalid agent_id (not an integer): {agent_id}")
                return render_template('agent_register.html', error=error,
                                    email=email, agent_id=agent_id,
                                    airline_name=airline_names, airlines=airlines)
        except Exception as e:
            conn.rollback()
            print(f"DEBUG - Registration error: {str(e)}")
            error = f"Registration failed: {str(e)}"
            return render_template('agent_register.html', error=error,
                                email=email, agent_id=agent_id,
                                airline_name=airline_names, airlines=airlines)
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()
    return render_template('agent_register.html', airlines=airlines)

@app.route('/agent/loginAuth', methods=['GET', 'POST'])
def agent_loginAuth():
    email = request.form['email']
    password = request.form['password']
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM booking_agent WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if data:
        session['username'] = email
        session['user_type'] = 'agent'
        return redirect(url_for('hello'))
    else:
        error = 'Invalid email or password'
        return render_template('agent_login.html', error=error)

@app.route('/agent/home')
def agent_home():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
        
    email = session['username']
    banner = request.args.get('banner')  # Get banner message from URL parameter
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get agent's airlines - adapted for professor's schema
        query = """
            SELECT a.airline_name
            FROM booking_agent_work_for ba
            JOIN airline a ON ba.airline_name = a.airline_name
            WHERE ba.email = %s
        """
        cursor.execute(query, (email,))
        airlines = cursor.fetchall()
        
        # Get agent ID for purchases query
        agent_id_query = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(agent_id_query, (email,))
        agent_data = cursor.fetchone()
        
        # Initialize stats variables
        tickets_sold = 0
        commission = 0
        
        if agent_data and agent_data['booking_agent_id']:
            agent_id = agent_data['booking_agent_id']
            
            # Get last 30 days stats - adapted for professor's schema
            today = datetime.today().strftime('%Y-%m-%d')
            thirty_days_ago = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            stats_query = """
                SELECT COUNT(p.ticket_id) as tickets_sold, 
                       SUM(f.price * 0.1) as commission
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                WHERE p.booking_agent_id = %s
                AND p.purchase_date BETWEEN %s AND %s
            """
            cursor.execute(stats_query, (agent_id, thirty_days_ago, today))
            stats = cursor.fetchone()
            
            if stats:
                tickets_sold = stats['tickets_sold'] if stats['tickets_sold'] else 0
                commission = float(stats['commission']) if stats['commission'] else 0
        
        return render_template('agent_home.html', 
                              username=email,
                              airlines=airlines,
                              tickets_sold=tickets_sold,
                              commission=commission,
                              banner=banner)  # Pass banner to template
    except Exception as e:
        print(f"DEBUG - Error in agent_home: {e}")
        return render_template('agent_home.html', 
                              username=email,
                              error=f"Error loading data: {str(e)}",
                              banner=banner)  # Pass banner even if error occurs
    finally:
        cursor.close()
        conn.close()

@app.route('/agent/view_flights', methods=['GET', 'POST'])
def agent_view_flights():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
    
    email = session['username']
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get agent's ID for purchases table lookup
        agent_id_query = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(agent_id_query, (email,))
        agent_data = cursor.fetchone()
        
        if not agent_data:
            cursor.close()
            conn.close()
            return render_template('agent_flights.html', 
                                 error="Agent account not found in database",
                                 flights=[])
        
        agent_id = agent_data['booking_agent_id']
        
        # Build query to get flights - adapted for professor's schema
        if request.method == 'POST':
            # Get filter criteria
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            source = request.form.get('source')
            destination = request.form.get('destination')
            
            query = """
                SELECT f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
                       f.departure_time, f.arrival_time, c.name as customer_name, 
                       c.email as customer_email
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                JOIN customer c ON p.customer_email = c.email
                WHERE p.booking_agent_id = %s
            """
            params = [agent_id]
            
            if from_date:
                query += " AND DATE(f.departure_time) >= %s"
                params.append(from_date)
            else:
                # Default: only show future flights
                query += " AND f.departure_time >= NOW()"
                
            if to_date:
                query += " AND DATE(f.departure_time) <= %s"
                params.append(to_date)
                
            if source:
                query += " AND f.departure_airport LIKE %s"
                params.append(f"%{source}%")
                
            if destination:
                query += " AND f.arrival_airport LIKE %s"
                params.append(f"%{destination}%")
                
            query += " ORDER BY f.departure_time ASC"
            
        else:
            # Default view - upcoming flights
            query = """
                SELECT f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
                       f.departure_time, f.arrival_time, c.name as customer_name, 
                       c.email as customer_email
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                JOIN customer c ON p.customer_email = c.email
                WHERE p.booking_agent_id = %s
                AND f.departure_time >= NOW()
                ORDER BY f.departure_time ASC
            """
            params = [agent_id]
        
        cursor.execute(query, params)
        flights = cursor.fetchall()
        
        return render_template('agent_flights.html', flights=flights)
    
    except Exception as e:
        print(f"DEBUG - Error in agent_view_flights: {e}")
        return render_template('agent_flights.html', 
                             error=f"An error occurred: {str(e)}",
                             flights=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/agent/search', methods=['GET', 'POST'])
def agent_search():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
        
    if request.method == 'POST':
        source = request.form['source'].strip()
        destination = request.form['destination'].strip()
        date = request.form['date']
        
        email = session['username']
        conn = getConnect()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get agent's authorized airlines - adapted for professor's schema
            agent_query = """
                SELECT airline_name 
                FROM booking_agent_work_for 
                WHERE email = %s
            """
            cursor.execute(agent_query, (email,))
            agent_airlines = cursor.fetchall()
            
            if not agent_airlines:
                return render_template('agent_search.html', 
                                    error="Warning: You are not authorized to book for any airline yet.")
            
            # List of airlines the agent can book for
            airline_names = [airline['airline_name'] for airline in agent_airlines]
            
            # Search for flights - adapted for professor's schema
            available_flights_query = """
                SELECT f.airline_name, f.flight_num, f.departure_airport, f.arrival_airport, 
                       f.departure_time, f.arrival_time, f.price, f.status
                FROM flight f
                WHERE f.departure_airport = %s 
                AND f.arrival_airport = %s 
                AND DATE(f.departure_time) = %s
            """
            cursor.execute(available_flights_query, (source, destination, date))
            all_flights = cursor.fetchall()
            
            # Add a flag to each flight indicating if the agent can book it
            for flight in all_flights:
                flight['can_book'] = flight['airline_name'] in airline_names
            
            return render_template('agent_search_results.html', 
                                  flights=all_flights, 
                                  authorized_airlines=airline_names)
        
        except Exception as e:
            print(f"DEBUG - Error in agent_search: {str(e)}")
            return render_template('agent_search.html', 
                                error=f"An error occurred while searching: {str(e)}")
        finally:
            cursor.close()
            conn.close()
        
    return render_template('agent_search.html')

@app.route('/agent/purchase_ticket', methods=['POST'])
def agent_purchase_ticket():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
    
    airline_name = request.form.get('airline_name')
    flight_num = request.form.get('flight_num')
    customer_email = request.form.get('customer_email')
    agent_email = session['username']
    
    print(f"DEBUG - Agent purchase ticket: airline={airline_name}, flight={flight_num}, customer={customer_email}, agent={agent_email}")
    
    if not airline_name or not flight_num or not customer_email:
        message = "Invalid flight or customer data."
        return redirect(url_for('agent_home', banner=message))
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Validate customer exists
        cursor.execute("SELECT * FROM customer WHERE email = %s", (customer_email,))
        if not cursor.fetchone():
            message = f"Customer with email {customer_email} does not exist."
            return redirect(url_for('agent_home', banner=message))
        
        # Validate flight exists - adapted for professor's schema
        cursor.execute("SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s", 
                      (airline_name, flight_num))
        if not cursor.fetchone():
            message = "Invalid flight number."
            return redirect(url_for('agent_home', banner=message))
        
        # Check if agent is authorized for this airline - adapted for professor's schema
        auth_query = """
            SELECT * FROM booking_agent_work_for 
            WHERE email = %s
            AND airline_name = %s
        """
        cursor.execute(auth_query, (agent_email, airline_name))
        if not cursor.fetchone():
            message = f"You are not authorized to book tickets for {airline_name}."
            return redirect(url_for('agent_home', banner=message))
        
        # Get agent ID
        agent_id_query = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(agent_id_query, (agent_email,))
        agent_data = cursor.fetchone()
        agent_id = agent_data['booking_agent_id']
        
        # Check if ticket already exists - adapted for professor's schema
        check_query = """
            SELECT t.ticket_id 
            FROM ticket t 
            JOIN purchases p ON t.ticket_id = p.ticket_id
            WHERE t.airline_name = %s AND t.flight_num = %s AND p.customer_email = %s
        """
        cursor.execute(check_query, (airline_name, flight_num, customer_email))
        if cursor.fetchone():
            message = "This customer has already purchased this ticket."
            return redirect(url_for('agent_home', banner=message))
        
        # Get next ticket_id
        cursor.execute("SELECT MAX(ticket_id) AS max_id FROM ticket")
        result = cursor.fetchone()
        new_ticket_id = 1  # Default if no tickets exist
        if result and result['max_id']:
            new_ticket_id = result['max_id'] + 1
        
        # Current date for purchase_date
        current_date = datetime.today().strftime('%Y-%m-%d')
        
        # Insert new ticket - adapted for professor's schema
        # First create the ticket
        ticket_query = """
            INSERT INTO ticket (ticket_id, airline_name, flight_num) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(ticket_query, (new_ticket_id, airline_name, flight_num))
        
        # Then create the purchase record with agent ID
        purchase_query = """
            INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(purchase_query, (new_ticket_id, customer_email, agent_id, current_date))
        
        conn.commit()
        message = "Ticket purchased successfully for customer!"
        
    except Exception as e:
        print(f"DEBUG - Error in agent_purchase_ticket: {e}")
        conn.rollback()
        message = f"Failed to purchase ticket: {str(e)}"
    finally:
        cursor.close()
        conn.close()
    
    # Redirect to agent_home which will fetch fresh data
    return redirect(url_for('agent_home', banner=message))

@app.route('/agent/commission', methods=['GET', 'POST'])
def agent_commission():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
    
    email = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get agent ID
        agent_id_query = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(agent_id_query, (email,))
        agent_data = cursor.fetchone()
        
        if not agent_data:
            cursor.close()
            conn.close()
            return render_template('agent_commission.html', 
                                 error="Agent account not found in database",
                                 tickets_sold=0,
                                 total_commission=0,
                                 avg_commission=0)
        
        agent_id = agent_data['booking_agent_id']
        
        if request.method == 'POST':
            # Custom date range
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not start_date or not end_date:
                return render_template('agent_commission.html', 
                                     error="Please provide both start and end dates.")
        else:
            # Default: past 30 days
            end_date = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Get commission stats - adapted for professor's schema
        commission_query = """
            SELECT 
                COUNT(p.ticket_id) as tickets_sold,
                SUM(f.price * 0.1) as total_commission,
                AVG(f.price * 0.1) as avg_commission
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.booking_agent_id = %s
            AND p.purchase_date BETWEEN %s AND %s
        """
        cursor.execute(commission_query, (agent_id, start_date, end_date))
        commission_data = cursor.fetchone()
        
        # Prepare data for display
        tickets_sold = commission_data['tickets_sold'] if commission_data['tickets_sold'] else 0
        total_commission = float(commission_data['total_commission']) if commission_data['total_commission'] else 0
        avg_commission = float(commission_data['avg_commission']) if commission_data['avg_commission'] else 0
        
        return render_template('agent_commission.html', 
                              tickets_sold=tickets_sold,
                              total_commission=total_commission,
                              avg_commission=avg_commission,
                              start_date=start_date,
                              end_date=end_date)
        
    except Exception as e:
        print(f"DEBUG - Exception in agent_commission: {str(e)}")
        return render_template('agent_commission.html', 
                              error=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.route('/agent/top_customers')
def agent_top_customers():
    if 'username' not in session or session['user_type'] != 'agent':
        return redirect(url_for('agent_login'))
    
    email = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get agent ID
        agent_id_query = "SELECT booking_agent_id FROM booking_agent WHERE email = %s"
        cursor.execute(agent_id_query, (email,))
        agent_data = cursor.fetchone()
        
        if not agent_data:
            cursor.close()
            conn.close()
            return render_template('agent_top_customers.html', 
                                 error="Agent account not found in database")
        
        agent_id = agent_data['booking_agent_id']
        
        # Current date for calculations
        today = datetime.today()
        six_months_ago = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        one_year_ago = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        
        # Top 5 by tickets (last 6 months) - adapted for professor's schema
        tickets_query = """
            SELECT c.email, c.name, COUNT(p.ticket_id) as ticket_count
            FROM purchases p
            JOIN customer c ON p.customer_email = c.email
            WHERE p.booking_agent_id = %s
            AND p.purchase_date BETWEEN %s AND %s
            GROUP BY c.email, c.name
            ORDER BY ticket_count DESC
            LIMIT 5
        """
        cursor.execute(tickets_query, (agent_id, six_months_ago, today))
        top_by_tickets = cursor.fetchall()
        
        # Top 5 by commission (last year) - adapted for professor's schema
        commission_query = """
            SELECT c.email, c.name, SUM(f.price * 0.1) as total_commission
            FROM purchases p
            JOIN customer c ON p.customer_email = c.email
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.booking_agent_id = %s
            AND p.purchase_date BETWEEN %s AND %s
            GROUP BY c.email, c.name
            ORDER BY total_commission DESC
            LIMIT 5
        """
        cursor.execute(commission_query, (agent_id, one_year_ago, today))
        top_by_commission = cursor.fetchall()
        
        # Prepare data for charts
        ticket_customers = [customer['name'] for customer in top_by_tickets]
        ticket_counts = [customer['ticket_count'] for customer in top_by_tickets]
        
        commission_customers = [customer['name'] for customer in top_by_commission]
        commission_amounts = [float(customer['total_commission']) for customer in top_by_commission]
        
        return render_template('agent_top_customers.html',
                              top_by_tickets=top_by_tickets,
                              top_by_commission=top_by_commission,
                              ticket_customers=ticket_customers,
                              ticket_counts=ticket_counts,
                              commission_customers=commission_customers,
                              commission_amounts=commission_amounts)
        
    except Exception as e:
        print(f"DEBUG - Exception in agent_top_customers: {str(e)}")
        return render_template('agent_top_customers.html', 
                              error=f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# AIRLINE STAFF ROUTES
@app.route('/staff/login')
def staff_login():
    return render_template('staff_login.html')

@app.route('/staff/register', methods=['GET', 'POST'])
def staff_register():
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Grab data from the form
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        airline_name = request.form['airline_name']

        # Check if the username already exists - adapted for professor's schema
        query = "SELECT * FROM airline_staff WHERE username = %s"
        cursor.execute(query, (username,))
        data = cursor.fetchone()

        if data:
            # Get airlines again for rendering dropdown
            cursor.execute("SELECT airline_name FROM airline")
            airlines = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('staff_register.html', error="Username already exists", airlines=airlines)

        # Check if airline_name exists
        cursor.execute("SELECT * FROM airline WHERE airline_name = %s", (airline_name,))
        airline_data = cursor.fetchone()
        if not airline_data:
            cursor.execute("SELECT airline_name FROM airline")
            airlines = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('staff_register.html', error="Airline name does not exist", airlines=airlines)

        # Insert new staff - adapted for professor's schema
        insert = """
            INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, airline_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert, (username, password, first_name, last_name, dob, airline_name))
        conn.commit()
        cursor.close()
        conn.close()

        # Log the user in
        session['username'] = username
        session['user_type'] = 'staff'
        return redirect(url_for('staff_home'))

    # GET method: fetch airline list for dropdown
    cursor.execute("SELECT airline_name FROM airline")
    airlines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('staff_register.html', airlines=airlines)

@app.route('/staff/loginAuth', methods=['GET', 'POST'])
def staff_loginAuth():
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)
    
    username = request.form['username']
    password = request.form['password']
    
    # Adapted for professor's schema
    query = "SELECT * FROM airline_staff WHERE username = %s and password = %s"
    cursor.execute(query, (username, password))
    
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if data:
        session['username'] = username
        session['user_type'] = 'staff'
        return redirect(url_for('hello'))
    else:
        error = 'Invalid username or password'
        return render_template('staff_login.html', error=error)

@app.route('/staff/home', methods=['GET', 'POST'])
def staff_home():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    banner = request.args.get('banner')  # Get banner message from URL parameter if exists
    
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        filters = {
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'source': request.form.get('source'),
            'destination': request.form.get('destination')
        }
    
        # Default: flights in the next 30 days - adapted for professor's schema
        query = """
            SELECT f.* FROM flight f
            JOIN airline_staff s ON f.airline_name = s.airline_name
            WHERE s.username = %s
            AND f.departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
        """
        params = [username]
    
        # If user applied filters
        if request.method == 'POST':
            query = """
                SELECT f.* FROM flight f
                JOIN airline_staff s ON f.airline_name = s.airline_name
                WHERE s.username = %s
            """
            conditions = []
            if filters['start_date']:
                conditions.append("f.departure_time >= %s")
                params.append(filters['start_date'])
            if filters['end_date']:
                conditions.append("f.departure_time <= %s")
                params.append(filters['end_date'])
            if filters['source']:
                conditions.append("f.departure_airport = %s")
                params.append(filters['source'])
            if filters['destination']:
                conditions.append("f.arrival_airport = %s")
                params.append(filters['destination'])
    
            if conditions:
                query += " AND " + " AND ".join(conditions)
    
        cursor.execute(query, params)
        flights = cursor.fetchall()
        
        # Get staff details to display full name
        staff_query = """
            SELECT first_name, last_name 
            FROM airline_staff 
            WHERE username = %s
        """
        cursor.execute(staff_query, (username,))
        staff_info = cursor.fetchone()

        # Use staff's first name if available, otherwise use username
        display_name = username
        if staff_info and staff_info['first_name']:
            display_name = staff_info['first_name']
        
        return render_template('staff_home.html', 
                             username=display_name,
                             flights=flights,
                             banner=banner)
    
    except Exception as e:
        print(f"DEBUG - Error in staff_home: {str(e)}")
        return render_template('staff_home.html', 
                             username=username,
                             error=f"An error occurred: {str(e)}",
                             flights=[],
                             banner=banner)
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline - adapted for professor's schema
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            error = "Staff profile not found."
            return render_template('create_flight.html', error=error)
    
        airline_name = staff_info['airline_name']
        
        # Check if staff has admin permission
        cursor.execute("""
            SELECT * FROM permission 
            WHERE username = %s AND permission_type = 'admin'
        """, (username,))
        admin_permission = cursor.fetchone()
        
        # Check if staff has admin permission
        has_admin_permission = admin_permission is not None
    
        if request.method == 'POST':
            # If staff doesn't have admin permission, return error
            if not has_admin_permission:
                error = "You do not have permission to create flights. Admin permission required."
                
                # Get upcoming flights for display
                cursor.execute("""
                    SELECT * FROM flight 
                    WHERE airline_name = %s 
                    AND departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
                    ORDER BY departure_time
                """, (airline_name,))
                flights = cursor.fetchall()
                
                return render_template('create_flight.html', 
                                      error=error, 
                                      airline=airline_name,
                                      has_admin_permission=has_admin_permission,
                                      flights=flights)
            
            flight_num = request.form['flight_num']
            airplane_id = request.form['airplane_id']
            departure_airport = request.form['departs_airport_name']
            arrival_airport = request.form['arrives_airport_name']
            departure_time = request.form['departure_time']
            arrival_time = request.form['arrival_time']
            price = request.form['price']
            status = request.form['status']
    
            # Check if airplane exists and belongs to staff's airline - adapted for professor's schema
            cursor.execute("""
                SELECT airplane_id FROM airplane 
                WHERE airplane_id = %s AND airline_name = %s
            """, (airplane_id, airline_name))
            
            airplane = cursor.fetchone()
            if not airplane:
                error = f"Airplane ID {airplane_id} not found or doesn't belong to {airline_name}."
                return render_template('create_flight.html', 
                                     error=error, 
                                     airline=airline_name, 
                                     form_data=request.form,
                                     has_admin_permission=has_admin_permission)
    
            # Insert flight - adapted for professor's schema
            insert_query = """
                INSERT INTO flight (airline_name, flight_num, departure_airport, departure_time, 
                                  arrival_airport, arrival_time, price, status, airplane_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (airline_name, flight_num, departure_airport, departure_time, 
                                        arrival_airport, arrival_time, price, status, airplane_id))
            conn.commit()
            message = "Flight successfully created."
    
            # Show future flights - adapted for professor's schema
            cursor.execute("""
                SELECT * FROM flight 
                WHERE airline_name = %s 
                AND departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
                ORDER BY departure_time
            """, (airline_name,))
            flights = cursor.fetchall()
            
            return render_template('create_flight_result.html', message=message, flights=flights)
        
        # Get upcoming flights for display
        cursor.execute("""
            SELECT * FROM flight 
            WHERE airline_name = %s 
            AND departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
            ORDER BY departure_time
        """, (airline_name,))
        flights = cursor.fetchall()
    
        return render_template('create_flight.html', 
                              airline=airline_name, 
                              has_admin_permission=has_admin_permission,
                              flights=flights)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in create_flight: {str(e)}")
        return render_template('create_flight.html', 
                             error=f"An error occurred: {str(e)}",
                             airline=staff_info['airline_name'] if staff_info else None,
                             has_admin_permission=False)
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/update_flight_status', methods=['GET', 'POST'])
def update_flight_status():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_result = cursor.fetchone()
        
        if not staff_result:
            error = "Staff account not found."
            return render_template('update_status.html', error=error, flights=[])
        
        airline_name = staff_result['airline_name']
        
        # Check operator permission - adapted for professor's schema
        cursor.execute("""
            SELECT * FROM permission 
            WHERE username = %s AND permission_type = 'operator'
        """, (username,))
        permission_result = cursor.fetchone()
        
        # If no operator permission
        if not permission_result:
            error = "Unauthorized. Operator permission required."
            
            # Get flights anyway to display the page - adapted for professor's schema
            cursor.execute("""
                SELECT airline_name, flight_num, departure_time, arrival_time, status
                FROM flight
                WHERE airline_name = %s AND departure_time >= NOW()
                ORDER BY departure_time
            """, (airline_name,))
            flights = cursor.fetchall()
            
            return render_template('update_status.html', error=error, flights=flights)

        if request.method == 'POST':
            flight_num = request.form.get('flight_num')
            status = request.form.get('status')
            
            # We need to pass airline_name as a hidden field or get it from staff info
            # Using staff's airline_name from database for security
            
            if not flight_num or not status:
                error = "Flight number and status are required."
                cursor.execute("""
                    SELECT airline_name, flight_num, departure_time, arrival_time, status
                    FROM flight
                    WHERE airline_name = %s AND departure_time >= NOW()
                    ORDER BY departure_time
                """, (airline_name,))
                flights = cursor.fetchall()
                return render_template('update_status.html', error=error, flights=flights)

            # Update flight status - adapted for professor's schema
            update_query = """
                UPDATE flight 
                SET status = %s 
                WHERE airline_name = %s AND flight_num = %s
            """
            cursor.execute(update_query, (status, airline_name, flight_num))
            conn.commit()
            message = "Flight status updated successfully."

            # Get the updated flight
            cursor.execute("""
                SELECT * FROM flight 
                WHERE airline_name = %s AND flight_num = %s
            """, (airline_name, flight_num))
            flights = cursor.fetchall()
            
            return render_template('update_status_result.html', message=message, flights=flights)
        
        # For GET requests, show flights from this airline
        cursor.execute("""
            SELECT airline_name, flight_num, departure_time, arrival_time, status
            FROM flight
            WHERE airline_name = %s AND departure_time >= NOW()
            ORDER BY departure_time
        """, (airline_name,))
        flights = cursor.fetchall()
        
        return render_template('update_status.html', flights=flights)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in update_flight_status: {str(e)}")
        error = f"An error occurred: {str(e)}"
        return render_template('update_status.html', error=error, flights=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check admin permission - adapted for professor's schema
        cursor.execute("""
            SELECT a.airline_name, p.permission_type 
            FROM airline_staff a
            LEFT JOIN permission p ON a.username = p.username AND p.permission_type = 'admin'
            WHERE a.username = %s
        """, (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info or not staff_info.get('permission_type'):
            # Get airline name for display even if no admin permission
            cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
            airline_info = cursor.fetchone()
            airline_name = airline_info['airline_name'] if airline_info else "Unknown Airline"
            
            # Get airplanes to show even if permission denied
            cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
            airplanes = cursor.fetchall()
            
            return render_template('add_airplane.html', 
                                 error="Unauthorized. Admin permission required.",
                                 airplanes=airplanes,
                                 airline_name=airline_name)
    
        airline_name = staff_info['airline_name']
    
        if request.method == 'POST':
            airplane_id = request.form['airplane_id']
            seats = request.form['seats']
            
            # Validate input
            if not airplane_id or not seats:
                cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
                airplanes = cursor.fetchall()
                return render_template('add_airplane.html', 
                                    error="Airplane ID and seats are required fields.",
                                    airplanes=airplanes,
                                    airline_name=airline_name)
            
            try:
                seats = int(seats)
                if seats <= 0:
                    raise ValueError("Seats must be a positive number")
            except ValueError:
                cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
                airplanes = cursor.fetchall()
                return render_template('add_airplane.html', 
                                    error="Seats must be a valid positive number.",
                                    airplanes=airplanes,
                                    airline_name=airline_name)
    
            try:
                # Check if airplane already exists
                cursor.execute("SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s", 
                            (airline_name, airplane_id))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
                    airplanes = cursor.fetchall()
                    return render_template('add_airplane.html', 
                                        error=f"Airplane with ID {airplane_id} already exists.",
                                        airplanes=airplanes,
                                        airline_name=airline_name)
                
                # Insert new airplane - adapted for professor's schema
                insert_query = """
                    INSERT INTO airplane (airline_name, airplane_id, seats)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (airline_name, airplane_id, seats))
                conn.commit()
                message = "Airplane added successfully."
        
                # Get updated airplane list
                cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
                airplanes = cursor.fetchall()
                
                # Debug print to check what data we're getting back
                print(f"DEBUG - Airplanes data after adding: {airplanes}")
                
                return render_template('add_airplane_result.html', message=message, airplanes=airplanes)
            except mysql.connector.Error as db_err:
                conn.rollback()
                print(f"DEBUG - Database error: {str(db_err)}")
                
                # Get airplane list to show with error message
                cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
                airplanes = cursor.fetchall()
                
                error_message = str(db_err)
                if "Duplicate entry" in error_message:
                    error_message = f"Airplane with ID {airplane_id} already exists."
                
                return render_template('add_airplane.html', 
                                    error=f"Database error: {error_message}",
                                    airplanes=airplanes,
                                    airline_name=airline_name)
    
        # Show existing airplanes for GET request
        cursor.execute("SELECT airplane_id, seats FROM airplane WHERE airline_name = %s", (airline_name,))
        airplanes = cursor.fetchall()
        
        # Debug print to check what data we're getting
        print(f"DEBUG - Initial airplanes data: {airplanes}")
        
        return render_template('add_airplane.html', airplanes=airplanes, airline_name=airline_name)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in add_airplane: {str(e)}")
        
        # Try to get airline name even if there's an error
        airline_name = "Unknown Airline"
        if 'staff_info' in locals() and staff_info and 'airline_name' in staff_info:
            airline_name = staff_info['airline_name']
        
        return render_template('add_airplane.html', 
                             error=f"An error occurred: {str(e)}",
                             airplanes=[],
                             airline_name=airline_name)
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/add_airport', methods=['GET', 'POST'])
def add_airport():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check admin permission - adapted for professor's schema
        cursor.execute("""
            SELECT a.airline_name, p.permission_type 
            FROM airline_staff a
            LEFT JOIN permission p ON a.username = p.username AND p.permission_type = 'admin'
            WHERE a.username = %s
        """, (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info or not staff_info.get('permission_type'):
            # Get airports to show even without admin permission
            cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
            airports = cursor.fetchall()
            
            print(f"DEBUG - Loaded {len(airports)} airports for unauthorized view")
            
            return render_template('add_airport.html', 
                                 error="Unauthorized. Admin permission required.",
                                 airports=airports)
    
        if request.method == 'POST':
            airport_name = request.form['airport_name']
            city = request.form['city']
            
            # Validate input
            if not airport_name or not city:
                cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
                airports = cursor.fetchall()
                return render_template('add_airport.html', 
                                    error="Airport name and city are required fields.",
                                    airports=airports)
    
            try:
                # Check if airport already exists
                cursor.execute("SELECT * FROM airport WHERE airport_name = %s", (airport_name,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
                    airports = cursor.fetchall()
                    return render_template('add_airport.html', 
                                        error=f"Airport with name {airport_name} already exists.",
                                        airports=airports)
                
                # Insert new airport - adapted for professor's schema
                insert_query = """
                    INSERT INTO airport (airport_name, airport_city)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_query, (airport_name, city))
                conn.commit()
                message = "Airport added successfully."
        
                # Get updated airport list
                cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
                airports = cursor.fetchall()
                
                # Debug output
                print(f"DEBUG - Airport added: {airport_name} in {city}")
                print(f"DEBUG - Now have {len(airports)} airports")
                for airport in airports[:5]:  # Show first 5 for debug
                    print(f"DEBUG - Sample airport: {airport}")
                
                return render_template('add_airport_result.html', message=message, airports=airports)
            except mysql.connector.Error as db_err:
                conn.rollback()
                print(f"DEBUG - Database error: {str(db_err)}")
                
                # Get airport list to show with error message
                cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
                airports = cursor.fetchall()
                
                error_message = str(db_err)
                if "Duplicate entry" in error_message:
                    error_message = f"Airport with name {airport_name} already exists."
                
                return render_template('add_airport.html', 
                                    error=f"Database error: {error_message}",
                                    airports=airports)
    
        # Show existing airports for GET request
        cursor.execute("SELECT airport_name, airport_city FROM airport ORDER BY airport_name")
        airports = cursor.fetchall()
        
        # Debug output
        print(f"DEBUG - Loaded {len(airports)} airports")
        
        return render_template('add_airport.html', airports=airports)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in add_airport: {str(e)}")
        return render_template('add_airport.html', 
                             error=f"An error occurred: {str(e)}",
                             airports=[])
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/view_agents')
def view_agents():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            return "Staff not found", 404
            
        airline_name = staff_info['airline_name']

        # Top 5 agents by ticket sales (last month) - adapted for professor's schema
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, COUNT(p.ticket_id) AS tickets_sold 
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN booking_agent ba ON p.booking_agent_id = ba.booking_agent_id
            WHERE t.airline_name = %s 
            AND p.booking_agent_id IS NOT NULL 
            AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY tickets_sold DESC
            LIMIT 5
        """, (airline_name,))
        top_agents_month = cursor.fetchall()

        # Top 5 agents by ticket sales (last year) - adapted for professor's schema
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, COUNT(p.ticket_id) AS tickets_sold 
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN booking_agent ba ON p.booking_agent_id = ba.booking_agent_id
            WHERE t.airline_name = %s 
            AND p.booking_agent_id IS NOT NULL 
            AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY tickets_sold DESC
            LIMIT 5
        """, (airline_name,))
        top_agents_year = cursor.fetchall()

        # Top 5 agents by commission (last year) - adapted for professor's schema
        cursor.execute("""
            SELECT ba.email, ba.booking_agent_id, SUM(f.price * 0.1) AS total_commission
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            JOIN booking_agent ba ON p.booking_agent_id = ba.booking_agent_id
            WHERE t.airline_name = %s 
            AND p.booking_agent_id IS NOT NULL 
            AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY ba.email, ba.booking_agent_id
            ORDER BY total_commission DESC
            LIMIT 5
        """, (airline_name,))
        top_commission_agents = cursor.fetchall()

        return render_template('view_agent.html',
                           top_agents_month=top_agents_month,
                           top_agents_year=top_agents_year,
                           top_commission_agents=top_commission_agents)
    
    except Exception as e:
        print(f"DEBUG - Error in view_agents: {str(e)}")
        error_message = str(e)
        return f"An error occurred: {error_message}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/frequent_customer', methods=['GET', 'POST'])
def frequent_customer():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            return "Staff not found", 404
            
        airline_name = staff_info['airline_name']

        top_customer = None
        customer_flights = []
        customer_name = None

        # Get past year's most frequent customer - adapted for professor's schema
        cursor.execute("""
            SELECT c.name, COUNT(*) AS flight_count
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN customer c ON p.customer_email = c.email
            WHERE t.airline_name = %s 
            AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY c.name
            ORDER BY flight_count DESC
            LIMIT 1
        """, (airline_name,))
        top_customer = cursor.fetchone()

        # If a specific customer name is submitted
        if request.method == 'POST':
            customer_name = request.form['customer_name']
            cursor.execute("""
                SELECT f.flight_num, f.departure_airport, f.arrival_airport,
                       f.departure_time, f.arrival_time
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                JOIN customer c ON p.customer_email = c.email
                WHERE t.airline_name = %s AND c.name = %s
                ORDER BY f.departure_time DESC
            """, (airline_name, customer_name))
            customer_flights = cursor.fetchall()

        return render_template('frequent_customer.html',
                           top_customer=top_customer,
                           customer_name=customer_name,
                           customer_flights=customer_flights,
                           airline_name=airline_name)
    
    except Exception as e:
        print(f"DEBUG - Error in frequent_customer: {str(e)}")
        error_message = str(e)
        return f"An error occurred: {error_message}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/view_reports', methods=['GET', 'POST'])
def view_reports():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            return "Staff not found", 404
            
        airline_name = staff_info['airline_name']

        # Default time period: last month
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not start_date or not end_date:
            end_date = datetime.today().strftime('%Y-%m-%d')
            start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

        # Query for tickets and revenue - adapted for professor's schema
        cursor.execute("""
            SELECT COUNT(*) AS total_tickets, COALESCE(SUM(f.price), 0) AS total_revenue
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE t.airline_name = %s AND p.purchase_date BETWEEN %s AND %s
        """, (airline_name, start_date, end_date))
        summary = cursor.fetchone()

        # Monthly stats for past year - adapted for professor's schema
        cursor.execute("""
            SELECT DATE_FORMAT(f.departure_time, '%Y-%m') AS month, COUNT(*) AS ticket_count
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE t.airline_name = %s AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY month
            ORDER BY month
        """, (airline_name,))
        month_stats = cursor.fetchall()

        return render_template('view_reports.html',
                            summary=summary,
                            start_date=start_date,
                            end_date=end_date,
                            month_stats=month_stats)
    
    except Exception as e:
        print(f"DEBUG - Error in view_reports: {str(e)}")
        error_message = str(e)
        return f"An error occurred: {error_message}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/revenue_comparison')
def revenue_comparison():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            return "Staff not found", 404
            
        airline_name = staff_info['airline_name']

        # Calculate revenue comparison - adapted for professor's schema
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) AS direct_revenue,
                SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) AS indirect_revenue
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()
        """, (airline_name,))
        last_month = cursor.fetchone()

        cursor.execute("""
            SELECT 
                SUM(CASE WHEN p.booking_agent_id IS NULL THEN f.price ELSE 0 END) AS direct_revenue,
                SUM(CASE WHEN p.booking_agent_id IS NOT NULL THEN f.price ELSE 0 END) AS indirect_revenue
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE t.airline_name = %s 
            AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
        """, (airline_name,))
        last_year = cursor.fetchone()

        return render_template('revenue_comparison.html',
                           last_month=last_month,
                           last_year=last_year)
    
    except Exception as e:
        print(f"DEBUG - Error in revenue_comparison: {str(e)}")
        error_message = str(e)
        return f"An error occurred: {error_message}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/top_destinations')
def top_destinations():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get staff's airline
        cursor.execute("SELECT airline_name FROM airline_staff WHERE username = %s", (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info:
            return "Staff not found", 404
            
        airline_name = staff_info['airline_name']

        # Top 3 destinations in last 3 months - adapted for professor's schema
        cursor.execute("""
            SELECT a.airport_city AS destination, COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            JOIN airport a ON f.arrival_airport = a.airport_name
            WHERE t.airline_name = %s AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            GROUP BY destination
            ORDER BY tickets_sold DESC
            LIMIT 3
        """, (airline_name,))
        top_3_months = cursor.fetchall()

        # Top 3 destinations in last year - adapted for professor's schema
        cursor.execute("""
            SELECT a.airport_city AS destination, COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            JOIN airport a ON f.arrival_airport = a.airport_name
            WHERE t.airline_name = %s AND p.purchase_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY destination
            ORDER BY tickets_sold DESC
            LIMIT 3
        """, (airline_name,))
        top_3_year = cursor.fetchall()

        return render_template('top_destinations.html',
                           top_3_months=top_3_months,
                           top_3_year=top_3_year,
                           airline_name=airline_name)
    
    except Exception as e:
        print(f"DEBUG - Error in top_destinations: {str(e)}")
        error_message = str(e)
        return f"An error occurred: {error_message}", 500
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/grant_permission', methods=['GET', 'POST'])
def grant_permission():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if staff has admin permission - adapted for professor's schema
        cursor.execute("""
            SELECT a.airline_name, p.permission_type 
            FROM airline_staff a
            LEFT JOIN permission p ON a.username = p.username AND p.permission_type = 'admin'
            WHERE a.username = %s
        """, (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info or not staff_info.get('permission_type'):
            return render_template('grant_permission.html', 
                                  error="You don't have Admin permission to perform this action.",
                                  airline_name=staff_info.get('airline_name') if staff_info else None)
            
        airline_name = staff_info['airline_name']

        # Process form submission
        if request.method == 'POST':
            target_username = request.form['username']
            new_permission = request.form['permission']

            # Check if target staff exists in same airline
            cursor.execute("SELECT * FROM airline_staff WHERE username = %s AND airline_name = %s", 
                          (target_username, airline_name))
            target_staff = cursor.fetchone()

            if not target_staff:
                return render_template('grant_permission.html', 
                                     error=f"Staff {target_username} does not exist or is not in your airline.",
                                     airline_name=airline_name)
            
            # Check if permission already exists - adapted for professor's schema
            cursor.execute("""
                SELECT * FROM permission 
                WHERE username = %s AND permission_type = %s
            """, (target_username, new_permission.lower()))
            existing_permission = cursor.fetchone()
            
            if not existing_permission:
                # Insert new permission
                cursor.execute("""
                    INSERT INTO permission (username, permission_type) 
                    VALUES (%s, %s)
                """, (target_username, new_permission.lower()))
                
                conn.commit()
                message = f"Successfully granted {new_permission} permission to {target_username}."
                return render_template('grant_permission.html', 
                                     message=message,
                                     airline_name=airline_name)
            else:
                message = f"{target_username} already has {new_permission} permission."
                return render_template('grant_permission.html', 
                                     message=message,
                                     airline_name=airline_name)

        # Show form for GET request
        return render_template('grant_permission.html', airline_name=airline_name)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in grant_permission: {str(e)}")
        return render_template('grant_permission.html', 
                             error=f"An error occurred: {str(e)}",
                             airline_name=staff_info.get('airline_name') if staff_info else None)
    finally:
        cursor.close()
        conn.close()

@app.route('/staff/add_booking_agent', methods=['GET', 'POST'])
def add_booking_agent():
    if 'username' not in session or session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))

    username = session['username']
    conn = getConnect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if staff has admin permission - adapted for professor's schema
        cursor.execute("""
            SELECT a.airline_name, p.permission_type 
            FROM airline_staff a
            LEFT JOIN permission p ON a.username = p.username AND p.permission_type = 'admin'
            WHERE a.username = %s
        """, (username,))
        staff_info = cursor.fetchone()
        
        if not staff_info or not staff_info.get('permission_type'):
            return render_template('add_booking_agent.html', 
                                  message="You don't have Admin permission to perform this action.",
                                  airline_name=staff_info.get('airline_name') if staff_info else None)
            
        airline_name = staff_info['airline_name']

        if request.method == 'POST':
            agent_email = request.form['agent_email']

            # Check if agent exists
            cursor.execute("SELECT * FROM booking_agent WHERE email = %s", (agent_email,))
            agent = cursor.fetchone()
            
            if not agent:
                return render_template('add_booking_agent.html', 
                                     message="Booking agent not found. The agent must register first.",
                                     airline_name=airline_name)

            # Check if already working for this airline - adapted for professor's schema
            cursor.execute("""
                SELECT * FROM booking_agent_work_for 
                WHERE email = %s AND airline_name = %s
            """, (agent_email, airline_name))
            
            exists = cursor.fetchone()
            if exists:
                return render_template('add_booking_agent.html', 
                                     message="This agent already works for your airline.",
                                     airline_name=airline_name)

            # Add relationship - adapted for professor's schema
            cursor.execute("""
                INSERT INTO booking_agent_work_for (email, airline_name) 
                VALUES (%s, %s)
            """, (agent_email, airline_name))
            
            conn.commit()
            return render_template('add_booking_agent.html', 
                                 message="Booking agent successfully added to your airline.",
                                 airline_name=airline_name)

        # Show form for GET request
        return render_template('add_booking_agent.html', airline_name=airline_name)
    
    except Exception as e:
        conn.rollback()
        print(f"DEBUG - Error in add_booking_agent: {str(e)}")
        return render_template('add_booking_agent.html', 
                             message=f"An error occurred: {str(e)}",
                             airline_name=staff_info.get('airline_name') if staff_info else None)
    finally:
        cursor.close()
        conn.close()

# Flight status check
@app.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        date = request.form['date']  # Format like "2025-04-13"
        airline_name = request.form.get('airline_name', '')  # May need to add this to the form

        conn = getConnect()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Adapted for professor's schema with composite key
            if airline_name:
                query = """
                    SELECT airline_name, flight_num, status,
                          DATE(departure_time) as departure_date,
                          TIME(departure_time) as departure_time,
                          DATE(arrival_time) as arrival_date,
                          TIME(arrival_time) as arrival_time
                    FROM flight 
                    WHERE airline_name = %s AND flight_num = %s 
                      AND (DATE(departure_time) = %s
                           OR DATE(arrival_time) = %s)
                """
                cursor.execute(query, (airline_name, flight_number, date, date))
            else:
                # Find by flight number and date if airline not specified
                query = """
                    SELECT airline_name, flight_num, status,
                          DATE(departure_time) as departure_date,
                          TIME(departure_time) as departure_time,
                          DATE(arrival_time) as arrival_date,
                          TIME(arrival_time) as arrival_time
                    FROM flight 
                    WHERE flight_num = %s 
                      AND (DATE(departure_time) = %s
                           OR DATE(arrival_time) = %s)
                """
                cursor.execute(query, (flight_number, date, date))
                
            results = cursor.fetchall()
            return render_template('check_results.html', status=results)

            
        except Exception as e:
            print(f"DEBUG - Error in status check: {str(e)}")
            return render_template('check_results.html', 
                                 error=f"An error occurred: {str(e)}",
                                 status=[])
        finally:
            cursor.close()
            conn.close()
    
    return render_template('check.html')

@app.route('/login')
def login_selection():
    return render_template('login.html')

@app.route('/register')
def register_selection():
    return render_template('register.html')

# Common routes
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_type', None)
    session.pop('display_name', None)
    return redirect('/')

# Set secret key for session
app.secret_key = 'some_secure_key_for_airline_system'

# Run the app
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
    