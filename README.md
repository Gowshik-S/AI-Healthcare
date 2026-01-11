
#  HealthCare AI

> **AI-powered healthcare triage system for intelligent symptom assessment and patient management**

A comprehensive healthcare platform that combines artificial intelligence with traditional healthcare workflows, enabling patients to receive instant health guidance while maintaining connectivity with certified medical professionals.

---

## Features

### For Patients
- ** AI Health Consultation** — Chat with an intelligent AI assistant for instant symptom analysis and health guidance
- ** Consultation History** — Access complete records of all past consultations and diagnoses
- ** Prescription Management** — Track medications, set reminders, and monitor treatment progress
- ** Health Profile** — Maintain personal health records including medical history and allergies

### For Doctors
- ** Patient Dashboard** — Comprehensive overview of patient cases and health metrics
- ** Triage Alerts** — Real-time notifications for high-risk patients requiring immediate attention
- ** Consultation Management** — Create, manage, and follow up on patient consultations
- ** Prescription System** — Issue and track prescriptions with dosage instructions

### Platform Features
- ** Secure Authentication** — JWT-based authentication with role-based access control
- ** HIPAA Considerations** — Privacy-focused design for healthcare data handling
- ** Responsive Design** — Seamless experience across desktop and mobile devices
- ** Real-time Updates** — Instant notification system for critical health alerts

---

##  Architecture

```
AI-HEALTHCARE/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # Application entry point
│   ├── database.py             # SQLAlchemy database configuration
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── utils.py                # Utility functions & JWT handling
│   ├── requirements.txt        # Python dependencies
│   └── routes/                 # API route handlers
│       ├── auth.py             # Authentication endpoints
│       ├── patients.py         # Patient management
│       ├── doctors.py          # Doctor management
│       ├── triage.py           # AI triage system
│       └── consultations.py    # Consultation management
│
├── frontend/                   # Vanilla JS Frontend
│   ├── css/
│   │   ├── style.css           # Design system & utilities
│   │   ├── components.css      # Component styles
│   │   └── responsive.css      # Responsive breakpoints
│   ├── js/
│   │   ├── api.js              # API client
│   │   ├── auth.js             # Authentication handlers
│   │   ├── chat.js             # Chat functionality
│   │   └── utils.js            # Utility functions
│   └── pages/
│       ├── landing.html        # Public landing page
│       ├── index.html          # Login/Signup
│       ├── patient-dashboard.html
│       ├── doctor-dashboard.html
│       ├── consultation-chat.html
│       ├── consultations.html
│       └── prescriptions.html
│
└── README.md
```

---

##  Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AI-HEALTHCARE.git
   cd AI-HEALTHCARE
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

5. **Access API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

The frontend is built with vanilla HTML, CSS, and JavaScript — no build step required!

1. **Open in browser**
   - Simply open `frontend/pages/landing.html` in your web browser
   - Or use a local server for better experience:
   
   ```bash
   # Using Python
   cd frontend
   python -m http.server 5500
   
   # Using Node.js (if installed)
   npx serve frontend
   ```

2. **Access the application**
   - Landing page: `http://localhost:5500/pages/landing.html`
   - Login/Signup: `http://localhost:5500/pages/index.html`

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/auth/me` | Get current user |

### Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients/profile` | Get patient profile |
| PUT | `/patients/profile` | Update patient profile |
| GET | `/patients/consultations` | Get patient's consultations |
| GET | `/patients/prescriptions` | Get patient's prescriptions |

### Doctors
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/doctors/patients` | Get assigned patients |
| GET | `/doctors/dashboard` | Get dashboard statistics |
| POST | `/doctors/prescriptions` | Create prescription |

### Triage
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/triage/start` | Start triage session |
| POST | `/triage/analyze` | Analyze symptoms |
| GET | `/triage/history` | Get triage history |

### Consultations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/consultations` | List consultations |
| POST | `/consultations` | Create consultation |
| GET | `/consultations/{id}` | Get consultation details |

---

## 🎨 Design System

The frontend uses a clean, professional color palette:

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#208090` | Buttons, links, accents |
| Success | `#22C55E` | Healthy states, confirmations |
| Warning | `#F97316` | Caution, reminders |
| Danger | `#EF4444` | Emergency, high risk |
| Background | `#FFFFFF` | Primary background |
| Text | `#1F2937` | Primary text |
| Border | `#E5E7EB` | Borders, dividers |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — Modern, high-performance Python web framework
- **SQLAlchemy** — SQL toolkit and ORM
- **Pydantic** — Data validation using Python type hints
- **SQLite** — Lightweight database (upgradable to PostgreSQL)
- **python-jose** — JWT token handling
- **passlib** — Password hashing

### Frontend
- **HTML5** — Semantic markup
- **CSS3** — Custom design system with CSS variables
- **Vanilla JavaScript** — No framework dependencies
- **Inter Font** — Clean, professional typography

---

##  Security

- JWT-based authentication with secure token handling
- Password hashing using bcrypt
- Role-based access control (Patient, Doctor, Admin)
- CORS configuration for frontend security
- Input validation on all endpoints

---

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Support

For support, please open an issue in the GitHub repository or contact the development team.

Email : gowshik@vortexinfinite.xyz

---


