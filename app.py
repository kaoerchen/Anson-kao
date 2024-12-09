from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets  # 用於生成安全密鑰

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 設置隨機生成的安全密鑰

# 設定 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義資料模型
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """將資料庫記錄轉換成字典格式"""
        return {
            "id": self.id,
            "date": self.date,
            "item": self.item,
            "amount": self.amount
        }

# 初始化資料庫
with app.app_context():
    db.create_all()

# 路由：顯示花費紀錄
@app.route('/')
def index():
    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses)

# 路由：顯示新增花費頁面
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # 從表單獲取資料
        date = request.form['date']
        item = request.form['item']
        amount = request.form['amount']
        try:
            # 新增到資料庫
            new_expense = Expense(date=date, item=item, amount=float(amount))
            db.session.add(new_expense)
            db.session.commit()
            flash('花費已成功新增！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'發生錯誤：{str(e)}', 'danger')
    return render_template('add_expense.html')

# 1. Create: 新增花費紀錄
@app.route('/api/expenses', methods=['POST'])
def create_expense():
    data = request.get_json()
    new_expense = Expense(date=data['date'], item=data['item'], amount=data['amount'])
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"message": "Expense created", "expense": new_expense.to_dict()}), 201

# 2. Read: 取得所有花費紀錄
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([expense.to_dict() for expense in expenses]), 200

# 3. Update: 修改花費紀錄
@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.get_json()
    expense = Expense.query.get_or_404(expense_id)
    expense.date = data.get('date', expense.date)
    expense.item = data.get('item', expense.item)
    expense.amount = data.get('amount', expense.amount)
    db.session.commit()
    return jsonify({"message": "Expense updated", "expense": expense.to_dict()}), 200

# 4. Delete: 刪除花費紀錄
@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)

