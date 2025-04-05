from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ZFypiYieLAuQTPyVKxkUCZfTMOumSoyu@switchyard.proxy.rlwy.net:54569/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    incomes = db.Column(db.JSON, default=[])
    expenses = db.Column(db.JSON, default=[])
    goals = db.Column(db.JSON, default=[])
    achieved_goals = db.Column(db.JSON, default=[])
    monthly_report = db.Column(db.JSON, default=[])  

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([
        {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'incomes': user.incomes,
            'expenses': user.expenses,
            'goals': user.goals,
            'achieved_goals': user.achieved_goals,
            'monthly_report': user.monthly_report
        }
        for user in users
    ])

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        password=data['password'],
        incomes=data.get('incomes', []),
        expenses=data.get('expenses', []),
        goals=data.get('goals', []),
        achieved_goals=data.get('achieved_goals', []),
        monthly_report=data.get('monthly_report', [])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'id': new_user.id}), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/users/<int:user_id>/clear_data', methods=['DELETE'])
def clear_user_data(user_id):
    user = User.query.get_or_404(user_id)

    user.incomes = []
    user.expenses = []
    user.goals = []
    user.achieved_goals = []

    db.session.commit()

    return jsonify({'message': 'Financial data cleared successfully'}), 200

#Obtener ingresos
@app.route('/users/<int:user_id>/incomes', methods=['GET'])
def get_incomes(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    formatted_incomes = [
        {
            **income,
            "amount": float(f"{income['amount']:.2f}")  
        }
        for income in user.incomes
    ]

    return jsonify(formatted_incomes)

#Agregar nuevo ingreso
@app.route('/users/<int:user_id>/incomes', methods=['POST'])
def add_income(user_id):
    from copy import deepcopy  

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json

    # Convertir amount a float con 2 decimales
    amount = round(float(data['amount']), 2)

    new_income = {
        "date": data['date'],
        "amount": amount,
        "currency": data['currency'],
        "provenance": data['provenance']
    }

    incomes = deepcopy(user.incomes) if user.incomes else []
    incomes.append(new_income)

    user.incomes = incomes
    db.session.commit()

    return jsonify(new_income), 201

#Obtener gastos
@app.route('/users/<int:user_id>/expenses', methods=['GET'])
def get_expenses(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    formatted_expenses = [
        {
            **expense,
            "amount": float(f"{expense['amount']:.2f}")  
        }
        for expense in user.expenses
    ]

    return jsonify(formatted_expenses)

#Agregar nuevo gasto
@app.route('/users/<int:user_id>/expenses', methods=['POST'])
def add_expense(user_id):
    from copy import deepcopy  # Importamos deepcopy para clonar la lista

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json

    # Convertir amount a float con 2 decimales
    amount = round(float(data['amount']), 2)

    new_expense = {
        "date": data['date'],
        "amount": amount,
        "currency": data['currency'],
        "purpose": data['purpose']
    }

    # Clonamos la lista antes de modificarla
    expenses = deepcopy(user.expenses) if user.expenses else []
    expenses.append(new_expense)

    # Reasignamos la lista modificada para que SQLAlchemy detecte cambios
    user.expenses = expenses
    db.session.commit()

    return jsonify(new_expense), 201

#Agregar nueva meta
@app.route('/users/<int:user_id>/goals', methods=['POST'])
def add_goal(user_id):
    from copy import deepcopy
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    if data:
        goals = deepcopy(user.goals) if user.goals else []
        goals.append(data)
        user.goals = goals
        db.session.commit()
        return jsonify({'message': 'Goal added successfully'}), 201
    return jsonify({'error': 'Invalid goal data'}), 400

# Eliminar una meta por índice
@app.route('/users/<int:user_id>/goals/<int:goal_index>', methods=['DELETE'])
def delete_goal(user_id, goal_index):
    from copy import deepcopy  # Para clonar la lista y evitar modificarla directamente

    user = User.query.get_or_404(user_id)

    if goal_index < 0 or goal_index >= len(user.goals):
        return jsonify({"error": "Goal index out of range"}), 400

    # Clonamos la lista antes de modificarla
    goals = deepcopy(user.goals)
    deleted_goal = goals.pop(goal_index)  # Eliminamos la meta en la posición especificada

    user.goals = goals  # Reasignamos la lista modificada
    db.session.commit()

    return jsonify({
        "message": "Goal deleted successfully",
        "deleted_goal": deleted_goal
    }), 200

#Ruta para agregar una meta lograda
@app.route('/users/<int:user_id>/achieved_goals', methods=['POST'])
def add_achieved_goal(user_id):
    from copy import deepcopy  # Para clonar la lista antes de modificarla

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid goal data'}), 400

    achieved_goals = deepcopy(user.achieved_goals) if user.achieved_goals else []
    achieved_goals.append(data)

    user.achieved_goals = achieved_goals  # Reasignamos la lista para que SQLAlchemy detecte el cambio
    db.session.commit()

    return jsonify({'message': 'Achieved goal added successfully', 'goal': data}), 201


# Eliminar una meta lograda
@app.route('/users/<int:user_id>/achieved_goals/<int:goal_index>', methods=['DELETE'])
def delete_achieved_goal(user_id, goal_index):
    from copy import deepcopy  # Para clonar la lista antes de modificarla

    user = User.query.get_or_404(user_id)

    if goal_index < 0 or goal_index >= len(user.achieved_goals):
        return jsonify({"error": "Achieved goal index out of range"}), 400

    # Clonamos la lista antes de modificarla
    achieved_goals = deepcopy(user.achieved_goals)
    deleted_goal = achieved_goals.pop(goal_index)  # Eliminamos la meta en la posición especificada

    user.achieved_goals = achieved_goals  # Reasignamos la lista modificada
    db.session.commit()

    return jsonify({
        "message": "Achieved goal deleted successfully",
        "deleted_goal": deleted_goal
    }), 200


#Ruta para obtener el reporte mensual
@app.route('/users/<int:user_id>/monthly_report', methods=['POST'])
def add_monthly_report(user_id):
    from copy import deepcopy  # Importamos deepcopy para clonar la lista

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid monthly report data'}), 400

    # Clonamos la lista antes de modificarla
    monthly_reports = deepcopy(user.monthly_report) if user.monthly_report else []
    
    # Agregamos el nuevo reporte
    monthly_reports.append(data)

    # Reasignamos la lista modificada para que SQLAlchemy detecte cambios
    user.monthly_report = monthly_reports
    db.session.commit()

    return jsonify({'message': 'Monthly report added successfully', 'report': data}), 201

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Hello, Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Render o 5000 por defecto
    app.run(host="0.0.0.0", port=port)
