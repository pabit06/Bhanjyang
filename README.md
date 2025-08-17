# भञ्ज्याङ सहकारी (Bhanjyang Cooperative)

A modern, responsive website for Bhanjyang Cooperative built with Django and Tailwind CSS.

## 🌟 Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Multi-language Support**: Nepali and English content
- **Team Management**: Committee and member management system
- **News & Updates**: Blog-style updates and events
- **Contact Forms**: User-friendly contact system
- **File Downloads**: Secure document sharing
- **Admin Panel**: Comprehensive Django admin interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- pip
- npm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Bhanjyang5
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate      # Linux/Mac
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   npm install
   ```

5. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   SEND_REAL_EMAILS=False
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Build CSS assets**
   ```bash
   npm run build
   ```

9. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## 🎨 Development

### Available Scripts

- `npm run dev` - Watch mode for Tailwind CSS compilation
- `npm run build` - Build production CSS
- `npm run start` - Start Django development server
- `npm run migrate` - Run database migrations
- `npm run collectstatic` - Collect static files

### Project Structure

```
Bhanjyang5/
├── coop/                 # Main Django project settings
├── main/                 # Homepage and about pages
├── team/                 # Team and committee management
├── updates/              # News and events
├── contact/              # Contact forms
├── downloads/            # File download system
├── templates/            # Base templates and partials
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded content
└── manage.py            # Django management script
```

## 🔧 Configuration

### Django Settings

The main configuration is in `coop/settings.py`. Key settings include:

- **Database**: SQLite (development) / PostgreSQL (production)
- **Static Files**: WhiteNoise for production serving
- **Media Files**: Local file storage
- **Email**: Console backend (development) / SMTP (production)

### Tailwind CSS

Custom Tailwind configuration in `static/src/input.css` includes:

- Custom color palette
- Custom animations
- Responsive utilities

## 📱 Responsive Design

The website is built with a mobile-first approach:

- **Mobile**: Optimized for small screens
- **Tablet**: Responsive layouts for medium screens
- **Desktop**: Full-featured desktop experience

## 🌐 Deployment

### Production Checklist

1. Set `DEBUG=False` in environment variables
2. Configure production database
3. Set up proper email backend
4. Configure static file serving
5. Set secure HTTPS settings
6. Use environment variables for sensitive data

### Recommended Hosting

- **VPS**: DigitalOcean, Linode, or AWS EC2
- **Platform**: Heroku, Railway, or PythonAnywhere
- **Database**: PostgreSQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support or questions, please contact the development team or create an issue in the repository.

---

**Built with ❤️ for Bhanjyang Cooperative**
