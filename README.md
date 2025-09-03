# Sohamactive-django-marketplace-app

This is a comprehensive Django web application that integrates a student management system with a full-featured e-commerce marketplace. The project, named "Sohamactive," combines educational and commercial functionalities into a single platform.

## Features

The application is divided into two main components, `app0` for the educational and core features, and `app1` for the e-commerce marketplace.

### Core & Educational Features (`app0`)

  * **Student Management**: A system to add, edit, and delete student records.
  * **Course and Instructor Details**: Students can be enrolled in courses, and their enrollment details, including assigned instructors, are displayed.
  * **Chatbot**: An AI chatbot is integrated using the Google Gemini API to respond to user prompts.
  * **Contact Form**: A contact form that, upon submission, generates a PDF of student data and sends it as an email attachment.
  * **PDF Generation**: The application can generate a PDF report of all registered students.

### Marketplace Features (`app1`)

  * **Product Catalog**: Users can browse a list of featured products.
  * **Shopping Cart**: Users can add products to a shopping cart, and the cart total dynamically updates via AJAX calls.
  * **Wishlist**: Users can save products to a wishlist for later.
  * **Checkout & Payments**: A checkout page and a payment gateway integrated with Razorpay for secure online transactions.
  * **Order History**: A page to view past orders and their status.

### Authentication

  * **Custom Backend**: The project uses a custom authentication backend to integrate with Auth0 for user login and logout.
  * **Social Login**: The project supports social logins, including Google.

## Installation

To get a local copy up and running, follow these simple steps.

### Prerequisites

  * Python 3.13.5
  * pip

### Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sohamactive/django-marketplace-app.git
    cd django-marketplace-app
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables**:
    Create a `.env` file in the root directory and add the following keys. These are necessary for security and functionality.
    ```
    SECRET_KEY=your_secret_key_here
    DEBUG=True
    RAZORPAY_KEY_ID=your_razorpay_key_id
    RAZORPAY_KEY_SECRET=your_razorpay_key_secret
    AUTH0_DOMAIN=your_auth0_domain
    AUTH0_CLIENT_ID=your_auth0_client_id
    AUTH0_CLIENT_SECRET=your_auth0_client_secret
    GEMINI_API_KEY=your_gemini_api_key
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    ```
5.  **Run migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
6.  **Create a superuser** to access the Django Admin panel:
    ```bash
    python manage.py createsuperuser
    ```
7.  **Run the development server**:
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## Technologies Used

  * **Backend**: Django 5.2.3
  * **Authentication**: Auth0, `django-allauth`
  * **Payments**: Razorpay
  * **AI**: Google Gemini API
  * **PDF Generation**: `weasyprint`, `xhtml2pdf`
  * **Deployment**: Gunicorn, Whitenoise, Heroku `Procfile`
