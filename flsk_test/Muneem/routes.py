from flask import render_template, request, redirect, url_for, flash
from Muneem import app, db
from Muneem.models import User, Personal_Expense, SplitExpense, Friend
from datetime import datetime

# Testing with user1 as the current user
@app.before_request
def before_request():
    global current_user
    current_user = User.query.filter_by(username="user1").first()  # Using "user1" as current user for now

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/personal')
def personal_page():
    return render_template('personal.html')

@app.route('/group-expense')
def group_expense():
    return render_template('group_expense.html')

@app.route('/submit-group-expense', methods=['POST'])
def submit_group_expense():
    data = {
        "item_name": request.form.get('itemName'),
        "category": request.form.get('category'),
        "description": request.form.get('description'),
        "date": request.form.get('date'),
        "total_amount": request.form.get('amount'),
        "paid_by": request.form.getlist('paidBy'),
        "split_among": request.form.getlist('splitAmong'),
    }

    paid_amounts = {}
    for person in data["paid_by"]:
        paid_amounts[person] = request.form.get(f"{person}_amount")

    data["paid_amounts"] = paid_amounts
    print(data)
    return "Group expense submitted successfully!"

@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if request.method == 'POST':
        # Get data from the form
        description = request.form['expenseTitle']
        amount = float(request.form['expenseAmount'])
        expense_date = request.form['expenseDate']

        # Create a new Personal_Expense record
        new_expense = Personal_Expense(
            description=description,
            amount=amount,
            date_time=datetime.strptime(expense_date, '%Y-%m-%d'),
            category='Uncategorized',  # You can add a category field to the form if you want
            owner=current_user.id  # Using current_user's ID
        )

        # Add the expense to the database
        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for('expense'))  # Redirect back to the same page to see the updated list

    # If GET request, show the form and list of expenses
    expenses = Personal_Expense.query.filter_by(owner=current_user.id).all()
    return render_template('personal.html', expenses=expenses)

@app.route('/edit-expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Personal_Expense.query.get_or_404(id)

    if request.method == 'POST':
        expense.description = request.form['expenseTitle']
        expense.amount = float(request.form['expenseAmount'])
        expense.date_time = datetime.strptime(request.form['expenseDate'], '%Y-%m-%d')
        expense.category = request.form.get('category', 'Uncategorized')

        db.session.commit()
        return redirect(url_for('expense'))  # Redirect back to the list of expenses

    return render_template('edit_expense.html', expense=expense)

@app.route('/delete-expense/<int:id>', methods=['GET'])
def delete_expense(id):
    expense = Personal_Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect(url_for('expense'))  # Redirect back to the list of expenses

@app.route('/add-friend', methods=['GET', 'POST'])
def add_friend():
    if request.method == 'POST':
        friend_email = request.form['friend_email']
        
        # Find the user by their email address
        friend = User.query.filter_by(email_address=friend_email).first()
        
        # Check if the friend exists and that the friend is not the current user
        if friend and friend.id != current_user.id:
            # Ensure the friendship is not already established
            existing_friendship = Friend.query.filter(
                (Friend.user_id == current_user.id) & (Friend.friend_id == friend.id) |
                (Friend.user_id == friend.id) & (Friend.friend_id == current_user.id)
            ).first()
            
            if not existing_friendship:
                # Create the friendship record
                new_friendship = Friend(user_id=current_user.id, friend_id=friend.id)
                db.session.add(new_friendship)
                db.session.commit()
                flash("Friend added successfully!", "success")
                return redirect(url_for('view_friend'))
            else:
                flash("You are already friends with this user.", "warning")
        else:
            flash("Invalid friend email or you can't add yourself.", "danger")
    
    return render_template('add_friend.html')

@app.route('/view-friends')
def view_friend():
    # Get the current user's friends
    friendships = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id)
    ).all()

    # Collect friends from both sides of the relationship
    friend_list = []
    for friendship in friendships:
        if friendship.user_id == current_user.id:
            friend_list.append(friendship.friend)
        else:
            friend_list.append(friendship.user)

    return render_template('view_friends.html', friends=friend_list)

@app.route('/split-expense', methods=['GET', 'POST'])
def split_expense():
    if request.method == 'POST':
        description = request.form.get('expenseTitle', '').strip()
        amount = request.form.get('expenseAmount', 0)
        expense_date = request.form.get('expenseDate', '')
        selected_friends = request.form.getlist('friends')  # List of friend IDs
        print(selected_friends)

        # Check if required fields are present
        if not description or not amount or not expense_date or not selected_friends:
            flash("All fields are required!", "danger")
            return redirect(url_for('split_expense'))

        amount = float(amount)

        # Calculate the split amount for each participant (including the user)
        split_amount = amount / (len(selected_friends) + 1)  # Including the user

        # Add the user's share to the Personal_Expense table
        user_expense = Personal_Expense(
            description=description,
            amount=split_amount,  # Only the user's share of the amount
            date_time=datetime.strptime(expense_date, '%Y-%m-%d'),
            category=request.form.get('category', 'Uncategorized'),
            owner=current_user.id
        )
        db.session.add(user_expense)
        db.session.commit()  # Commit to generate expense ID

        # Add the split entries for the current user and selected friends
        # 1. Add the user's own expense
        split_entry = SplitExpense(
            expense_id=user_expense.id,  # Using the new user's expense ID
            friend_id=current_user.id,  # The current user themselves
            amount=split_amount  # Split amount for the user
        )
        db.session.add(split_entry)

        # 2. Add the split entries for other friends
        for friend_id in selected_friends:
            friend_expense = Personal_Expense(
                description=description,
                amount=split_amount,  # Split amount for each friend
                date_time=datetime.strptime(expense_date, '%Y-%m-%d'),
                category=request.form.get('category', 'Uncategorized'),
                owner=int(friend_id)  # Set the friend as the owner
            )
            db.session.add(friend_expense)

            # Also add the split entry in the SplitExpense table
            split_entry = SplitExpense(
                expense_id=user_expense.id,  # Using the user's expense ID
                friend_id=int(friend_id),  # Friend ID
                amount=split_amount  # Split amount for the friend
            )
            db.session.add(split_entry)

        db.session.commit()  # Commit the split entries and all expenses

        flash("Expense split successfully!", "success")
        return redirect(url_for('expense'))
    else:
        friends = Friend.query.filter(
            (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id)
        ).all()
        return render_template('split_expense.html', friends=friends)

if __name__ == '__main__':
    app.run(debug=True)
