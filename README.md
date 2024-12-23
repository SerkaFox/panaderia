# Panaderia Project

Panaderia Project is a web application designed for managing a bakery database. It provides tools to interact with database tables, insert or update data, and view relationships between tables in an intuitive user interface.

## Features

### 1. **User Authentication**
- Users must log in with their database credentials to access the application.

### 2. **Dynamic Table Management**
- View, edit, and delete data from any table in the database.
- Automatically detects table structure and primary keys.
- Supports foreign key relationships for data integrity.

### 3. **Interactive Form for Data Insertion and Editing**
- Dynamic forms generated based on the selected table structure.
- Supports dropdowns for fields with predefined options (e.g., `SET` data type or related tables).
- Validation for required fields.

### 4. **Responsive and Customizable Design**
- Uses a clean and modern UI design for better user experience.
- Allows users to customize the background and button colors.

### 5. **Error Handling and Logging**
- Catches and logs database and application errors for debugging.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (with dynamic UI elements)
- **Database**: MySQL

## Project Structure

```
panaderia/
├── templates/              # HTML templates for UI
├── static/                 # Static files (CSS, JS, images)
├── app.py                  # Main Flask application
├── extensions.py           # Helper functions and Flask extensions
└── requirements.txt        # Python dependencies
```

## Installation and Setup

### Prerequisites
- Python 3.x
- MySQL database

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/SerkaFox/panaderia.git
   cd panaderia
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask application:
   ```bash
   python app.py
   ```

4. Open the application in your browser at `http://localhost`.

## How to Use

1. **Login**:
   - Enter your MySQL credentials to connect to the database.

2. **Select Table**:
   - Choose a table from the dropdown to view or edit its data.

3. **Insert or Update Data**:
   - Use the form to add new data or edit existing rows.
   - Related tables are automatically recognized for dropdown options.

4. **Customize**:
   - Change the background color using the color picker for a personalized experience.

## Contributions

Contributions are welcome! Please submit issues or pull requests to improve the project.

## License

This project is licensed under the MIT License.

---

Enjoy managing your bakery database with Panaderia!
