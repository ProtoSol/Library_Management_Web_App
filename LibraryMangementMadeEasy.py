import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize dataframes in session state if not already done
def init_dataframes():
    if 'books_df' not in st.session_state:
        st.session_state.books_df = pd.DataFrame({
            'name': ['1984', 'Brave New World', 'To Kill a Mockingbird', 'The Great Gatsby'],
            'author': ['George Orwell', 'Aldous Huxley', 'Harper Lee', 'F. Scott Fitzgerald'],
            'available': [True, True, False, True]
        })

    if 'movies_df' not in st.session_state:
        st.session_state.movies_df = pd.DataFrame({
            'name': ['Inception', 'Interstellar', 'The Matrix', 'Parasite'],
            'director': ['Christopher Nolan', 'Christopher Nolan', 'Wachowski Brothers', 'Bong Joon-ho'],
            'available': [True, False, True, True]
        })

    if 'user_df' not in st.session_state:
        st.session_state.user_df = pd.DataFrame({
            'username': ['admin', 'user1', 'user2'],
            'password': ['adminpass', 'user1pass', 'user2pass'],
            'role': ['admin', 'user', 'user']
        })

    if 'issue_df' not in st.session_state:
        st.session_state.issue_df = pd.DataFrame(columns=['username', 'item_name', 'item_type', 'issue_date', 'return_date', 'status'])

# Update DataFrame in session state
def update_dataframe(df_name, df):
    st.session_state[df_name] = df

# Role check decorator
def role_required(role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if st.session_state.get('role') != role:
                st.error("Unauthorized access.")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Download CSV functionality
def download_link(df, filename):
    csv = df.to_csv(index=False)
    st.download_button(label=f"Download {filename}",
                       data=csv,
                       file_name=filename,
                       mime='text/csv')

# Admin download options
@role_required('admin')
def admin_downloads():
    st.subheader("Download Data")
    options = st.multiselect("Select Data to Download", ['Books', 'Movies', 'Users', 'Issued Items'])
    
    if 'Books' in options:
        download_link(st.session_state.books_df, 'books.csv')
    if 'Movies' in options:
        download_link(st.session_state.movies_df, 'movies.csv')
    if 'Users' in options:
        download_link(st.session_state.user_df, 'users.csv')
    if 'Issued Items' in options:
        download_link(st.session_state.issue_df, 'issued_items.csv')

# Add new item (Admin only)
@role_required('admin')
def add_item():
    st.subheader("Add New Book or Movie")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    name = st.text_input(f"Enter {item_type} Name")
    author_or_director = st.text_input(f"Enter {'Author' if item_type == 'Book' else 'Director'} Name")
    
    if st.button(f"Add {item_type}"):
        if name and author_or_director:
            df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
            new_entry = {'name': name, 'available': True}
            if item_type == 'Book':
                new_entry['author'] = author_or_director
            else:
                new_entry['director'] = author_or_director
            
            df = df.append(new_entry, ignore_index=True)
            update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
            st.success(f"{item_type} '{name}' added successfully!")
        else:
            st.error("Please fill all fields.")

# Update item (Admin only)
@role_required('admin')
def update_item():
    st.subheader("Update Existing Book or Movie")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    name = st.selectbox(f"Select {item_type} to Update", df['name'])
    is_available = st.checkbox("Available", df.loc[df['name'] == name, 'available'].values[0])
    
    if st.button(f"Update {item_type}"):
        df.loc[df['name'] == name, 'available'] = is_available
        update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
        st.success(f"{item_type} '{name}' updated successfully!")

# Manage users (Admin only)
@role_required('admin')
def manage_users():
    st.subheader("User Management")
    action = st.selectbox("Select Action", ['Add User', 'Update User'])
    username = st.text_input("Username")
    password = st.text_input("Password")
    role = st.selectbox("Role", ['admin', 'user'])
    
    df = st.session_state.user_df

    if action == 'Add User' and st.button("Add User"):
        if username and password:
            new_user = pd.DataFrame([{'username': username, 'password': password, 'role': role}])
            df = pd.concat([df, new_user], ignore_index=True)
            update_dataframe('user_df', df)
            st.success(f"User '{username}' added successfully!")
        else:
            st.error("Please fill all fields.")
    
    if action == 'Update User' and st.button("Update User"):
        if username in df['username'].values:
            df.loc[df['username'] == username, ['password', 'role']] = password, role
            update_dataframe('user_df', df)
            st.success(f"User '{username}' updated successfully!")
        else:
            st.error(f"User '{username}' not found!")

# View reports (Admin and User)
def view_reports():
    st.subheader("Reports")
    report_options = ['Active Issues', 'Master List of Movies', 'Master List of Books']
    if st.session_state.get('role') == 'admin':
        report_options.insert(0, 'Master List of Memberships')
        report_options.append('Overdue Returns')
        report_options.append('Pending Requests')
    
    report_type = st.selectbox("Select Report", report_options)
    
    if report_type == 'Active Issues':
        st.dataframe(st.session_state.issue_df)
    elif report_type == 'Master List of Memberships' and st.session_state.get('role') == 'admin':
        st.dataframe(st.session_state.user_df)
    elif report_type == 'Master List of Movies':
        st.dataframe(st.session_state.movies_df)
    elif report_type == 'Master List of Books':
        st.dataframe(st.session_state.books_df)

# Check item availability
def check_item_availability():
    st.subheader("Check Availability")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    st.dataframe(df)

# Issue item (User only)
def issue_item():
    st.subheader("Issue a Book or Movie")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    name = st.selectbox(f"Select {item_type}", df[df['available']]['name'])
    issue_date = st.date_input("Issue Date", datetime.now())
    return_date = issue_date + timedelta(days=15)
    st.write(f"Return Date: {return_date}")

    if st.button(f"Issue {item_type}"):
        issue_df = st.session_state.issue_df
        issue_df = issue_df.append({
            'username': st.session_state['username'],
            'item_name': name,
            'item_type': item_type,
            'issue_date': issue_date,
            'return_date': return_date,
            'status': 'Issued'
        }, ignore_index=True)
        update_dataframe('issue_df', issue_df)
        df.loc[df['name'] == name, 'available'] = False
        update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
        st.success(f"{item_type} '{name}' issued successfully!")

# Return item (User only)
def return_item():
    st.subheader("Return Book or Movie")
    user_issues = st.session_state.issue_df[(st.session_state.issue_df['username'] == st.session_state['username']) & (st.session_state.issue_df['status'] == 'Issued')]
    if user_issues.empty:
        st.error("You have no items to return.")
        return
    item_name = st.selectbox("Select Item to Return", user_issues['item_name'])
    return_date = st.date_input("Return Date", datetime.now())
    
    if st.button("Return Item"):
        issue_df = st.session_state.issue_df
        issue_df.loc[(issue_df['username'] == st.session_state['username']) & (issue_df['item_name'] == item_name), 'status'] = 'Returned'
        update_dataframe('issue_df', issue_df)
        item_type = user_issues.loc[user_issues['item_name'] == item_name, 'item_type'].values[0]
        df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
        df.loc[df['name'] == item_name, 'available'] = True
        update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
        st.success(f"'{item_name}' returned successfully!")

# Fine payment (User only)
def fine_payment():
    st.subheader("Fine Payment")
    today = datetime.now().date()
    user_issues = st.session_state.issue_df[st.session_state.issue_df['username'] == st.session_state['username']]
    
    overdue_items = user_issues[
        (user_issues['status'] == 'Issued') & 
        (pd.to_datetime(user_issues['return_date']).dt.date < today)
    ]
    
    if overdue_items.empty:
        st.write("No fines due currently.")
    else:
        fine_rate = 1  # $1 per day
        total_fine = 0
        
        st.write("Overdue Items:")
        for _, item in overdue_items.iterrows():
            days_overdue = (today - pd.to_datetime(item['return_date']).date()).days
            item_fine = days_overdue * fine_rate
            total_fine += item_fine
            st.write(f"- {item['item_name']} (Due: {item['return_date']}): ${item_fine:.2f}")
        
        st.write(f"\nTotal Fine Due: ${total_fine:.2f}")
        
        if st.button("Pay Fine"):
            for index in overdue_items.index:
                st.session_state.issue_df.loc[index, 'status'] = 'Returned'
            
            update_dataframe('issue_df', st.session_state.issue_df)
            st.success(f"Fine of ${total_fine:.2f} paid successfully. All overdue items marked as returned.")
            
            for _, item in overdue_items.iterrows():
                df = st.session_state.books_df if item['item_type'] == 'Book' else st.session_state.movies_df
                df.loc[df['name'] == item['item_name'], 'available'] = True
                update_dataframe('books_df' if item['item_type'] == 'Book' else 'movies_df', df)

# Main Application Logic
def main():
    st.title("Library Management System")
    init_dataframes()

    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['username'] is None:
        # Login logic
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user = st.session_state.user_df[(st.session_state.user_df['username'] == username) & (st.session_state.user_df['password'] == password)]
            if not user.empty:
                st.session_state['username'] = username
                st.session_state['role'] = user['role'].values[0]
                st.success(f"Logged in as {st.session_state['role']}.")
            else:
                # Check if the username exists in the user DataFrame
                if username in st.session_state.user_df['username'].values:
                    st.error("Incorrect password. Please try again.")
                else:
                    st.error("User not found. Please contact the admin to create an account.")
    else:
        if st.session_state['role'] == 'admin':
            menu_admin()
        elif st.session_state['role'] == 'user':
            menu_user()

# Menu for Admin
@role_required('admin')
def menu_admin():
    menu = st.sidebar.radio("Admin Menu", ['Add Item', 'Update Item', 'Manage Users', 'View Reports', 'Download Data', 'Transactions', 'Logout'])
    
    if menu == 'Add Item':
        add_item()
    elif menu == 'Update Item':
        update_item()
    elif menu == 'Manage Users':
        manage_users()
    elif menu == 'View Reports':
        view_reports()
    elif menu == 'Download Data':
        admin_downloads()
    elif menu == 'Transactions':
        check_item_availability()
    elif menu == 'Logout':
        st.session_state['username'] = None
        st.experimental_rerun()

# Menu for User
@role_required('user')
def menu_user():
    menu = st.sidebar.radio("User Menu", ['View Reports', 'Transactions', 'Logout'])
    
    if menu == 'View Reports':
        view_reports()
    elif menu == 'Transactions':
        transaction_menu = st.selectbox("Select Transaction", ['Check Availability', 'Issue Item', 'Return Item', 'Fine Payment'])
        if transaction_menu == 'Check Availability':
            check_item_availability()
        elif transaction_menu == 'Issue Item':
            issue_item()
        elif transaction_menu == 'Return Item':
            return_item()
        elif transaction_menu == 'Fine Payment':
            fine_payment()
    elif menu == 'Logout':
        st.session_state['username'] = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()