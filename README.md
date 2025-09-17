# 🎓 School Face Attendance System

Isang modern face recognition attendance system na ginawa gamit ang Python, CustomTkinter, at OpenCV. Ang system na ito ay nagbibigay ng seamless at automated attendance tracking para sa schools through facial recognition technology.

## ✨ Features

- 🔐 **User Authentication** - Secure login system para sa admins, teachers, at staff
- 👤 **Face Recognition** - Advanced facial detection at recognition gamit ang OpenCV
- 📊 **Attendance Management** - Comprehensive attendance tracking at reporting
- 🖥️ **Modern UI** - Beautiful dark theme interface gamit ang CustomTkinter
- 🗄️ **Dual Storage** - Support para sa MySQL database at JSON file storage
- 🔄 **Hot Reload** - Development mode na may automatic app reloading
- 📈 **Dashboard** - Real-time analytics at statistics
- 👥 **Student Management** - Complete student database management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 o mas bago
- MySQL Server (optional, pwede rin JSON storage)
- Webcam para sa face recognition

### Installation

1. **Clone ang repository**

   ```bash
   git clone <repository-url>
   cd my_python_auth_face_app
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database (optional)**

   ```bash
   # Para sa MySQL setup
   python scripts/migrate.py
   ```

4. **Run ang application**

   ```bash
   # Production mode
   python main.py

   # Development mode na may hot reload
   python scripts/dev.py
   ```

## 📁 Project Structure

```
my_python_auth_face_app/
├── app/                          # Main application directory
│   ├── assets/                   # Static assets (icons, images)
│   │   └── icons/               # Application icons
│   ├── data/                     # JSON data storage
│   │   ├── images/              # Student face images
│   │   └── users.json           # User data file
│   ├── database/                # Database management
│   │   ├── database_service.py  # Database operations
│   │   ├── migrations/          # Database migrations
│   │   └── seeders/            # Sample data seeders
│   ├── models/                  # ML models at haar cascades
│   │   └── haarcascade_frontalface_default.xml
│   ├── services/               # Business logic services
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── data_store.py       # Data management
│   │   ├── json_store.py       # JSON storage operations
│   │   └── face/               # Face recognition modules
│   │       ├── detector.py     # Face detection
│   │       ├── recognizer.py   # Face recognition
│   │       ├── trainer.py      # Model training
│   │       ├── advanced_recognition.py # Advanced recognition features
│   │       ├── confidence_validator.py # Confidence validation
│   │       ├── gpu_acceleration.py # GPU acceleration
│   │       └── image_preprocessor.py # Image preprocessing
│   ├── ui/                     # User interface components
│   │   ├── app.py             # Main application window
│   │   ├── components/        # Reusable UI components
│   │   │   ├── navbar.py      # Navigation bar
│   │   │   └── sidebar.py     # Sidebar component
│   │   ├── pages/             # Application pages
│   │   │   ├── home.py        # Home/landing page
│   │   │   ├── login.py       # Login page
│   │   │   ├── register.py    # Registration page
│   │   │   ├── dashboard.py   # Main dashboard
│   │   │   ├── students.py    # Student management
│   │   │   ├── attendance.py  # Attendance tracking
│   │   │   └── shell.py       # Main application shell
│   │   └── widget/            # Custom widgets
│   │       ├── data_table.py  # Data table widget
│   │       └── gradient_button.py # Gradient button widget
│   └── utils/                 # Utility functions
│       ├── config.py          # Configuration settings
│       ├── dev_state.py       # Development state management
│       └── performance_config.py # Performance configuration
├── db/                        # Database files
│   ├── database.py           # Database utilities
│   ├── schema.sql            # Database schema
│   └── school_face_attendance.sql # Database schema
├── scripts/                   # Development and utility scripts
│   ├── dev.py                # Development server na may hot reload
│   ├── migrate.py            # Database migration runner
│   ├── performance_tuner.py  # Performance tuning script
│   ├── improve_face_recognition.py # Face recognition improvement
│   └── README.md             # Scripts documentation
├── tests/                     # Test files
│   ├── test_simple.py        # Basic UI test
│   ├── test_compound_names.py # Compound name matching test
│   ├── test_db_connection.py # Database connection test
│   └── README.md             # Tests documentation
├── examples/                  # Example code and demonstrations
│   ├── example_crud_table.py # CRUD DataTable example
│   └── README.md             # Examples documentation
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── COMPOUND_NAMES_GUIDE.md   # Compound names guide
├── dev_state_example.md      # Development state example
└── README.md                 # Project documentation
```

## 💾 Database Schema

Ang system ay sumusuporta ng comprehensive database schema:

- **users** - System users (admin, teacher, staff)
- **students** - Student information at details
- **faces** - Face encoding data para sa recognition
- **attendance** - Attendance records na may timestamps
- **logs** - System activity logs

## 🔧 Configuration

### Database Setup

Edit ang `app/utils/config.py` para sa inyong database settings:

```python
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "school_face_attendance"
```

### Storage Backend

Pwede kayong pumili between MySQL at JSON storage:

```python
STORAGE_BACKEND = "json"  # o "mysql"
```

## 🖥️ Usage

### 1. User Roles

- **Admin** - Full system access
- **Teacher** - Attendance management at student viewing
- **Staff** - Basic attendance operations

### 2. Face Recognition Setup

1. Navigate sa Students page
2. Add new student information
3. Capture face samples para sa training
4. Train ang recognition model
5. Start attendance tracking

### 3. Attendance Tracking

- Real-time face detection gamit ang camera
- Automatic attendance marking
- Timestamp recording
- Status tracking (present, late, absent)

## 🎨 UI Features

- **Dark Theme** - Modern at eye-friendly interface
- **Gradient Buttons** - Beautiful custom button widgets
- **Responsive Layout** - Adaptive design na gumagana sa iba't ibang screen sizes
- **Navigation** - Intuitive sidebar navigation
- **Dashboard** - Real-time statistics at insights

## 📂 Project Organization

Ang project ay organized sa mga sumusunod na directories:

### 📁 Core Directories

- **`app/`** - Main application code (UI, services, database, etc.)
- **`db/`** - Database files at schemas
- **`scripts/`** - Development at utility scripts
- **`tests/`** - Test files para sa different components
- **`examples/`** - Example code at demonstrations

### 🛠️ Scripts Directory

Contains development at utility scripts:

- `dev.py` - Development server na may hot reload
- `migrate.py` - Database migration runner
- `performance_tuner.py` - Face recognition performance tuning
- `improve_face_recognition.py` - Face recognition accuracy improvement

### 🧪 Tests Directory

Contains test files para sa different components:

- `test_simple.py` - Basic UI functionality test
- `test_compound_names.py` - Compound name matching test
- `test_db_connection.py` - Database connectivity test

### 📚 Examples Directory

Contains example code at demonstrations:

- `example_crud_table.py` - CRUD DataTable widget example

## 🔄 Development

### Hot Reload Development

```bash
python scripts/dev.py
```

Ang development server ay:

- Automatically reloads ang app kapag may file changes
- Monitors ang `app/` directory
- Supports F5 o Ctrl+R para sa manual reload

### Development Features

- File watcher na nag-monitor ng changes
- Automatic process restart
- Console logging para sa debugging
- Error handling at graceful restarts

## 📦 Dependencies

- **opencv-python** - Computer vision at face detection
- **opencv-contrib-python** - Additional OpenCV modules
- **mysql-connector-python** - MySQL database connectivity
- **Pillow** - Image processing
- **customtkinter** - Modern UI framework
- **bcrypt** - Password hashing
- **watchdog** - File system monitoring

## 🚀 Production Deployment

1. Install production dependencies
2. Setup MySQL database
3. Configure environment variables
4. Run migrations: `python scripts/migrate.py`
5. Start application: `python main.py`

## 🤝 Contributing

1. Fork ang repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push sa branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 Sample Data

Ang system ay may built-in sample data:

- 500 sample students na may complete information
- Sample attendance records
- Default admin accounts

Run `python scripts/migrate.py` para ma-setup ang sample data.

## 🔐 Security Features

- Password hashing gamit ang bcrypt
- Session management
- Role-based access control
- Secure face data storage

## 📱 Screenshots

_Note: Add screenshots ng inyong application dito_

## 📞 Support

Para sa issues o questions, mag-create ng issue sa repository o contact ang development team.

## 📄 License

Ang project na ito ay licensed under ang MIT License - tingnan ang LICENSE file para sa details.

---

**Made with ❤️ para sa Filipino schools**
