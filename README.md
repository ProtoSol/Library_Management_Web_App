# Library Management System

## Overview

The Library Management System is a Streamlit-based application designed for managing a library's collection of books and movies. The application supports user and admin roles, allowing for various functionalities such as adding and updating items, managing users, issuing and returning items, and viewing reports.

## Features

- **User Login:** Users and admins can log in to access different features based on their role.
- **Admin Features:**
  - **Add Items:** Admins can add new books or movies to the library.
  - **Update Items:** Admins can update the availability status of existing books or movies.
  - **Manage Users:** Admins can add or update user accounts.
  - **View Reports:** Admins can view detailed reports including active issues, master lists of books, movies, memberships, overdue returns, and pending requests.
  - **Download Data:** Admins can download data related to books, movies, users, and issued items.
- **User Features:**
  - **View Reports:** Users can view the master lists of books and movies.
  - **Transactions:**
    - **Check Availability:** Users can check the availability of books and movies.
    - **Issue Items:** Users can issue books or movies from the library.
    - **Return Items:** Users can return previously issued items.
    - **Fine Payment:** Users can pay fines for overdue items.

## Live Preview

To view the live demo of the application, click [here](https://librarymanager.streamlit.app/).

## Installation

To run the Library Management System, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the project directory:**

   ```bash
   cd library-management-system
   ```

3. **Install dependencies:**

    Ensure you have Python installed, then install the required libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Streamlit app:**

    ```bash
    streamlit run LibraryMangementMadeEasy.py
    ```

## Usage

1. **Login:**
    - Enter your username and password to log in. Admins have additional options and functionalities compared to regular users.
2. **Admin Dashboard:**
    - Use the sidebar menu to navigate between different functionalities such as adding items, updating items, managing users, and viewing reports.
3. **User Dashboard:**
    - Users can check availability, issue or return items, and pay fines using the provided options.

## File Structure

The Library Management System is structured as follows:

- LibraryMangementMadeEasy.py: The main Streamlit app file.
- requirements.txt: A list of required libraries and their versions.
- README.md: A short description of the project.

## Contributing

If you'd like to contribute to the project, please follow the [contributing guidelines](https://github.com/StreamlitCommunity/library-management-system/blob/main/CONTRIBUTING.md).

Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

## Contact

If you have any questions or feedback, please reach out to [ps1442003@outlook.com](mailto:ps1442003@outlook.com)
