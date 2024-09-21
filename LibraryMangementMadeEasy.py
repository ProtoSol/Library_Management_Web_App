import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize dataframes in session state if not already done at the start of the code.
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
            'username': ['admin', 'user1', 'user2', 'john_doe', 'jane_smith', 'alice_jones'],
            'password': ['adminpass', 'user1pass', 'user2pass', 'johnpass', 'janepass', 'alicepass'],
            'role': ['admin', 'user', 'user', 'user', 'user', 'user'],
            'subscription_end': [pd.NaT, datetime.now() + timedelta(days=30), datetime.now() + timedelta(days=90), datetime.now() + timedelta(days=60), pd.NaT, datetime.now() + timedelta(days=365)],
            'fines': [0, 0, 0, 0, 0, 0]  # Initialize fines
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

# Admin download options to obtain various information stored in the instance
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
    # Logic to display the correct query question based on the selection of the admin.
    name = st.text_input(f"Enter {item_type} Name")
    author_or_director = st.text_input(f"Enter {'Author' if item_type == 'Book' else 'Director'} Name")
    # Usage of the one if condtion to update the correct dataframe.
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
    # Select the appropriate dataframe based on the selected item type
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
    subscription_duration = st.selectbox("Subscription Duration", ['None', '1 Month', '3 Months', '6 Months', '1 Year'])

    df = st.session_state.user_df

    if action == 'Add User' and st.button("Add User"):
        if username and password:
            subscription_end = pd.NaT
            if subscription_duration != 'None':
                days_map = {'1 Month': 30, '3 Months': 90, '6 Months': 180, '1 Year': 365}
                subscription_end = datetime.now() + timedelta(days=days_map[subscription_duration])
                
            new_user = pd.DataFrame([{'username': username, 'password': password, 'role': role, 'subscription_end': subscription_end, 'fines': 0}])
            df = pd.concat([df, new_user], ignore_index=True)
            update_dataframe('user_df', df)
            st.success(f"User '{username}' added successfully!")
        else:
            st.error("Please fill all fields.")
    
    if action == 'Update User' and st.button("Update User"):
        if username in df['username'].values:
            subscription_end = df.loc[df['username'] == username, 'subscription_end'].values[0]
            if subscription_duration != 'None':
                days_map = {'1 Month': 30, '3 Months': 90, '6 Months': 180, '1 Year': 365}
                subscription_end = datetime.now() + timedelta(days=days_map[subscription_duration])
                
            df.loc[df['username'] == username, ['password', 'role', 'subscription_end']] = password, role, subscription_end
            update_dataframe('user_df', df)
            st.success(f"User '{username}' updated successfully!")
        else:
            st.error(f"User '{username}' not found!")

# View available and unavailable items (Admin only)
@role_required('admin')
def view_available_items():
    st.subheader("Available and Unavailable Books and Movies")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    view_type = st.selectbox("Select availability", ['Available Items', 'Unavailable Items'])
    
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    if view_type == 'Available Items':
        items = df[df['available']]
    else:
        items = df[~df['available']]
    
    st.dataframe(items)

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
    if not is_subscription_valid():
        st.error("Your subscription has expired or is not valid. Please purchase a subscription to issue items.")
        return

    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    name = st.selectbox(f"Select {item_type}", df[df['available']]['name'])
    issue_date = st.date_input("Issue Date", datetime.now())
    return_date = issue_date + timedelta(days=7)
    
    if st.button(f"Issue {item_type}"):
        new_issue = {
            'username': st.session_state['username'],
            'item_type': item_type,
            'item_name': name,
            'issue_date': issue_date,
            'return_date': return_date,
            'status': 'Issued'
        }
        issue_df = pd.concat([st.session_state.issue_df, pd.DataFrame([new_issue])], ignore_index=True)
        update_dataframe('issue_df', issue_df)
        
        # Mark the item as unavailable
        df.loc[df['name'] == name, 'available'] = False
        update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
        
        st.success(f"{item_type} '{name}' issued successfully!")


# Return item (User only)
def return_item():
    st.subheader("Return a Book or Movie")
    item_type = st.selectbox("Select type", ['Book', 'Movie'])
    df = st.session_state.books_df if item_type == 'Book' else st.session_state.movies_df
    name = st.selectbox(f"Select {item_type} to Return", df[df['available'] == False]['name'])
    
    if st.button(f"Return {item_type}"):
        item_row = st.session_state.issue_df[(st.session_state.issue_df['item_name'] == name) & 
                                             (st.session_state.issue_df['item_type'] == item_type) &
                                             (st.session_state.issue_df['username'] == st.session_state['username'])]

        if not item_row.empty:
            # Calculate overdue days
            current_date = datetime.now().date()
            return_date = item_row['return_date'].values[0].date() if isinstance(item_row['return_date'].values[0], datetime) else item_row['return_date'].values[0]
            overdue_days = (current_date - return_date).days
            
            # Mark item as available
            df.loc[df['name'] == name, 'available'] = True
            update_dataframe('books_df' if item_type == 'Book' else 'movies_df', df)
            
            # Remove issue record
            issue_df = st.session_state.issue_df[~((st.session_state.issue_df['item_name'] == name) & 
                                                   (st.session_state.issue_df['item_type'] == item_type) &
                                                   (st.session_state.issue_df['username'] == st.session_state['username']))]
            update_dataframe('issue_df', issue_df)
            
            # Notify user
            if overdue_days > 0:
                st.success(f"{item_type} '{name}' returned successfully! You have {overdue_days} overdue days.")
            else:
                st.success(f"{item_type} '{name}' returned successfully!")
        else:
            st.error("No issue record found for this item.")

# Pay fines (User only)
def pay_fines():
    st.subheader("Pay Fines")
    username = st.session_state.get('username')
    if not username:
        st.error("You need to be logged in to pay fines.")
        return

    fines = st.session_state.user_df.loc[st.session_state.user_df['username'] == username, 'fines'].values[0]
    if fines == 0:
        st.success("You have no fines to pay.")
        return

    st.write(f"Total Fines: {fines}")
    if st.button("Pay Fines"):
        st.session_state.user_df.loc[st.session_state.user_df['username'] == username, 'fines'] = 0
        update_dataframe('user_df', st.session_state.user_df)
        st.success("Fines paid successfully!")

# Check subscription validity
def is_subscription_valid():
    username = st.session_state.get('username')
    if username:
        user_data = st.session_state.user_df.loc[st.session_state.user_df['username'] == username]
        if not user_data.empty:
            subscription_end = user_data['subscription_end'].values[0]
            if pd.isna(subscription_end):
                return True
            # Ensure subscription_end is a datetime object
            if not isinstance(subscription_end, datetime):
                subscription_end = pd.to_datetime(subscription_end, errors='coerce')
            return subscription_end >= datetime.now()
    return False

# Get subscription info of the current user
def get_subscription_info(username, user_df):
    user_data = user_df.loc[user_df['username'] == username]
    if user_data.empty:
        return None, None

    subscription_end = pd.to_datetime(user_data['subscription_end'].values[0])
    
    if pd.isna(subscription_end):
        return None, None
    
    days_remaining = (subscription_end - datetime.now()).days
    return subscription_end, days_remaining

# Format subscription info
def format_subscription_info(subscription_end, days_remaining):
    if subscription_end is None:
        return "Subscription: No subscription"
    return (
        f"Subscription Ends On: {subscription_end.strftime('%Y-%m-%d')}\n"
        f"Days Remaining: {days_remaining}"
    )

# Logout functionality
def logout():
    st.session_state.clear()
    st.session_state['logged_out'] = True
    st.rerun() # as the experimental_rerun() was replaced with rerun()

def main():
    st.title("Library Management Made Easy")

    # Initialize dataframes
    init_dataframes()

    # Handle logout
    if 'logged_out' in st.session_state and st.session_state['logged_out']:
        st.session_state['logged_out'] = False
        st.rerun()

    # Check if user is logged in
    if 'username' not in st.session_state:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            user = st.session_state.user_df[(st.session_state.user_df['username'] == username) & 
                                            (st.session_state.user_df['password'] == password)]
            if not user.empty:
                st.session_state['username'] = username
                st.session_state['role'] = user['role'].values[0]
                st.rerun()  # Reload the app to show the appropriate menu
            else:
                st.error("Invalid username or password, or contact admin if you are an new user.")
    else:
        # Display subscription info in sidebar for users
        if st.session_state['role'] == 'user':
            username = st.session_state['username']
            subscription_end, days_remaining = get_subscription_info(username, st.session_state.user_df)
            sidebar_text = format_subscription_info(subscription_end, days_remaining)
            st.sidebar.text(sidebar_text)

        # Display admin menu or user menu based on role
        if st.session_state['role'] == 'admin':
            st.sidebar.title("Admin Menu")
            menu = st.sidebar.radio("Select Menu", [
                'Manage Users', 
                'Add Item', 
                'Update Item', 
                'Admin Downloads', 
                'View Reports', 
                'View Items Availability', 
                'Logout'
            ])
            # Admin menu added here
            if menu == 'Manage Users':
                manage_users()
            elif menu == 'Add Item':
                add_item()
            elif menu == 'Update Item':
                update_item()
            elif menu == 'Admin Downloads':
                admin_downloads()
            elif menu == 'View Reports':
                view_reports()
            elif menu == 'View Items Availability':
                view_available_items()
            elif menu == 'Logout':
                logout()

        elif st.session_state['role'] == 'user':
            st.sidebar.title("User Menu")
            menu = st.sidebar.radio("Select Menu", [
                'Check Item Availability', 
                'Issue Item', 
                'View Reports', 
                'Logout'
            ])

            # User menu added here
            if menu == 'Check Item Availability':
                check_item_availability()
            elif menu == 'Issue Item':
                issue_item()
            elif menu == 'View Reports':
                view_reports()
            elif menu == 'Logout':
                logout()

# Run the app
if __name__ == "__main__":
    main()