from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


import os



app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

   
     return mysql.connector.connect(
        host=os.environ["gateway01.ap-northeast-1.prod.aws.tidbcloud.com"],
        port=int(os.environ.get("TIDB_PORT", "4000")),
        user=os.environ["34K2vSTosu2TySb.root"],
        password=os.environ["hvVUv00ds9pc9KIA"],
        database=os.environ.get("TIDB_DATABASE", "expense_tracker"),
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "Expense Tracker Flask Server is working!"
    })


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["POST"])
def register():

    conn = None
    cursor = None

    try:

        # Get JSON from Android
        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # Get values
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")


        # ==========================================
        # CHECK EMPTY FIELDS
        # ==========================================

        if not name or not email or not password or not confirm_password:

            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400


        # ==========================================
        # CHECK PASSWORDS
        # ==========================================

        if password != confirm_password:

            return jsonify({
                "success": False,
                "message": "Passwords do not match"
            }), 400


        # ==========================================
        # DATABASE CONNECTION
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor()


        # ==========================================
        # CHECK EMAIL
        # ==========================================

        query = """
            SELECT id
            FROM users
            WHERE email = %s
        """

        cursor.execute(
            query,
            (email,)
        )

        existing_user = cursor.fetchone()


        if existing_user:

            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 409


        # ==========================================
        # HASH PASSWORD
        # ==========================================

        hashed_password = generate_password_hash(password)


        # ==========================================
        # INSERT USER
        # ==========================================

        insert_query = """
            INSERT INTO users
            (fullname, email, password)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "name": name,
            "email": email
        }), 201


    except Exception as e:

        if conn:
            conn.rollback()

        print("REGISTER ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    conn = None
    cursor = None

    try:

        # Get JSON from Android
        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # Get values
        email = data.get("email")
        password = data.get("password")


        # ==========================================
        # CHECK EMPTY FIELDS
        # ==========================================

        if not email or not password:

            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400


        # ==========================================
        # DATABASE CONNECTION
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)


        # ==========================================
        # FIND USER
        # ==========================================

        query = """
            SELECT id, fullname, email, password
            FROM users
            WHERE email = %s
        """

        cursor.execute(
            query,
            (email,)
        )

        user = cursor.fetchone()


        # ==========================================
        # USER NOT FOUND
        # ==========================================

        if not user:

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401


        # ==========================================
        # CHECK PASSWORD
        # ==========================================

        if not check_password_hash(
                user["password"],
                password):

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401


        # ==========================================
        # LOGIN SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Login successful",
            "id": user["id"],
            "name": user["fullname"],
            "email": user["email"]
        }), 200


    except Exception as e:

        if conn:
            conn.rollback()

        print("LOGIN ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================
# ADD EXPENSE
# ==========================================

@app.route("/add_expense", methods=["POST"])
def add_expense():

    conn = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # ==========================================
        # GET DATA
        # ==========================================

        user_id = data.get("user_id")
        amount = data.get("amount")
        category = data.get("category")
        description = data.get("description")
        date = data.get("date")


        # ==========================================
        # VALIDATION
        # ==========================================

        if not user_id:

            return jsonify({
                "success": False,
                "message": "User ID is required"
            }), 400


        if not amount:

            return jsonify({
                "success": False,
                "message": "Amount is required"
            }), 400


        if not category:

            return jsonify({
                "success": False,
                "message": "Category is required"
            }), 400


        if not date:

            return jsonify({
                "success": False,
                "message": "Date is required"
            }), 400


        # ==========================================
        # DATABASE
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor()


        sql = """
            INSERT INTO transactions
            (
                user_id,
                type,
                category,
                amount,
                description,
                transaction_date
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """


        values = (
            user_id,
            "Expense",
            category,
            amount,
            description,
            date
        )


        cursor.execute(sql, values)

        conn.commit()


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Expense added successfully"
        }), 201


    except Exception as e:

        if conn:
            conn.rollback()

        print("EXPENSE ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================
# ADD INCOME
# ==========================================

@app.route("/add_income", methods=["POST"])
def add_income():

    conn = None
    cursor = None

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400


        # ==========================================
        # GET DATA
        # ==========================================

        user_id = data.get("user_id")
        amount = data.get("amount")
        source = data.get("source")
        description = data.get("description")
        date = data.get("date")


        # ==========================================
        # VALIDATION
        # ==========================================

        if not user_id:

            return jsonify({
                "success": False,
                "message": "User ID is required"
            }), 400


        if not amount:

            return jsonify({
                "success": False,
                "message": "Amount is required"
            }), 400


        if not source:

            return jsonify({
                "success": False,
                "message": "Income source is required"
            }), 400


        if not date:

            return jsonify({
                "success": False,
                "message": "Date is required"
            }), 400


        # ==========================================
        # DATABASE
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor()


        sql = """
            INSERT INTO transactions
            (
                user_id,
                type,
                category,
                amount,
                description,
                transaction_date
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """


        values = (
            user_id,
            "Income",
            source,
            amount,
            description,
            date
        )


        cursor.execute(sql, values)

        conn.commit()


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "message": "Income added successfully"
        }), 201


    except Exception as e:

        if conn:
            conn.rollback()

        print("INCOME ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================
# GET USER TRANSACTIONS
# ==========================================

@app.route("/transactions", methods=["GET"])
def get_transactions():

    conn = None
    cursor = None

    try:

        # ==========================================
        # GET USER ID
        # ==========================================

        user_id = request.args.get("user_id")


        if not user_id:

            return jsonify({
                "success": False,
                "message": "User ID is required"
            }), 400


        # ==========================================
        # DATABASE
        # ==========================================

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)


        # ==========================================
        # GET ONLY THIS USER'S TRANSACTIONS
        # ==========================================

        query = """
            SELECT
                id,
                user_id,
                type,
                category,
                amount,
                description,
                transaction_date,
                created_at
            FROM transactions
            WHERE user_id = %s
            ORDER BY id DESC
        """


        cursor.execute(
            query,
            (user_id,)
        )


        transactions = cursor.fetchall()


        # ==========================================
        # SUCCESS
        # ==========================================

        return jsonify({
            "success": True,
            "transactions": transactions
        }), 200


    except Exception as e:

        print("TRANSACTIONS ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ==========================================
# RUN FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )