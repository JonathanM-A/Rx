# Rx: Pharmacy Inventory and Retail Management System

Rx is a comprehensive solution for managing pharmacy inventory, client orders, and in-store retail operations. Built with Django and Django Rest Framework, this project is designed to streamline pharmacy operations with robust features like warehouse management, online orders, and a point-of-sale (POS) system.

## Key Features

- **Warehouse Management**: Efficiently manage stock levels and inventory for your pharmacy.
- **Online Orders**: Allow clients to place orders online for pickup or delivery.
- **POS System**: Handle in-store purchases seamlessly with an integrated point-of-sale system.

## Technology Stack

- **Backend**: Django
- **Database**: PostgreSQL (or your database of choice)

## Getting Started

### Prerequisites

- Python 3.x
- Django
- Django Rest Framework
- PostgreSQL (or another database)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/JonathanM-A/Rx.git
   cd Rx
   ```

2. Set up a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate   # For Linux/macOS
   env\Scripts\activate      # For Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database settings in `settings.py`.

5. Run migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Contributing

Contributions are welcome! Please feel free to fork this repository and submit pull requests. If you reproduce this project in any form, I kindly ask that you acknowledge my work.

### Steps to Contribute:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Description of changes"
   ```

4. Push your branch:

   ```bash
   git push origin feature-name
   ```

5. Open a pull request.

## License

This project is open source. Please include acknowledgment to [JonathanM-A](https://github.com/JonathanM-A) in any reproductions of this work.