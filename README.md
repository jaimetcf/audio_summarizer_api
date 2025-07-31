# Audio Summarizer

A Python application that transcribes audio files and generates comprehensive summary reports using OpenAI Agents. The project includes both a command-line interface and a REST API for audio processing and summarization.

## 🎯 Features

- **Audio Transcription**: Convert audio files to text using OpenAI's advanced speech recognition
- **AI-Powered Summarization**: Generate intelligent summaries using OpenAI Agents
- **Template-Based Reports**: Create structured reports using Word document templates
- **Firebase Integration**: Store and retrieve files from Firebase Storage
- **REST API**: Full REST API with FastAPI for integration with web applications
- **Authentication**: Firebase user token validation for secure access
- **Interactive Documentation**: Auto-generated API documentation with Swagger UI

## 📁 Project Structure

```
audio_summarizer/
├── data/
│   ├── audio_files/          # Sample audio files for testing
│   ├── report_templates/     # Word document templates
│   └── reports/             # Generated reports output
├── helper_agents/
│   ├── transcriber_agent.py  # OpenAI agent for audio transcription
│   ├── summarizer_agent.py   # OpenAI agent for text summarization
│   └── test_*.py            # Unit tests for agents
├── main.py                   # Command-line interface
├── api.py                    # FastAPI REST API
├── settings.py               # Configuration settings
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- Firebase project with Storage enabled
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd audio_summarizer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Firebase Configuration
   FIREBASE_SERVICE_ACCOUNT_PATH=path/to/service_account.json
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   
   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   FRONTEND_URL=http://localhost:3000
   ```

5. **Set up Firebase:**
   - Download your Firebase service account key from Firebase Console
   - Place it in the project root or specify the path in `.env`
   - Enable Firebase Storage in your Firebase project

## 📖 Usage

### Command Line Interface

The `main.py` script provides a command-line interface for processing local audio files:

```bash
# Process default audio file with default template
python main.py

# Process specific audio file
python main.py --audio-file audio-test1.mp3

# Process with custom template
python main.py --audio-file audio-test1.mp3 --template-file custom_template.docx
```

**Available options:**
- `--audio-file, -a`: Audio file name (default: transformer-paper-introduction.mp3)
- `--template-file, -t`: Template file name (default: default_report_template.docx)

### REST API

The `api.py` provides a REST API for processing audio files stored in Firebase Storage:

#### Start the API server:
```bash
# Using uvicorn directly
uvicorn api:app --reload

# Or using the Python script
python api.py
```

#### API Endpoints:

**POST `/api/summarize`**
- **Purpose**: Transcribe and summarize audio files
- **Authentication**: Requires Firebase Bearer token
- **Request Body**:
  ```json
  {
    "audio_file_locator": "gs://bucket/audio/file.mp3",
    "template_file_locator": "gs://bucket/templates/template.docx"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Audio summarization completed successfully",
    "report_file_locator": "gs://bucket/reports/user123/file.docx"
  }
  ```

**GET `/api/health`**
- **Purpose**: Health check endpoint
- **Response**: API status information

#### API Documentation:

Once the server is running, access the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Example API Usage

```bash
# Using curl
curl -X POST "http://localhost:8000/api/summarize" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file_locator": "gs://your-bucket/audio/audio-test1.mp3",
    "template_file_locator": "gs://your-bucket/templates/default_report_template.docx"
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Path to Firebase service account JSON | Yes |
| `FIREBASE_STORAGE_BUCKET` | Firebase Storage bucket name | Yes |
| `API_HOST` | API server host (default: 0.0.0.0) | No |
| `API_PORT` | API server port (default: 8000) | No |
| `FRONTEND_URL` | Frontend URL for CORS (default: http://localhost:3000) | No |

### Firebase Setup

1. **Create a Firebase project** at [Firebase Console](https://console.firebase.google.com/)
2. **Enable Firebase Storage** in your project
3. **Download service account key**:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the JSON file securely
4. **Update your `.env` file** with the correct paths and bucket name

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest

# Run specific test files
pytest helper_agents/test_transcriber_agent.py
pytest helper_agents/test_summarizer_agent.py
```

## 📋 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for building APIs
- **OpenAI**: Official OpenAI Python client
- **openai-agents**: OpenAI Agents SDK for AI-powered workflows
- **firebase-admin**: Firebase Admin SDK for server-side operations
- **python-docx**: Library for creating and modifying Word documents
- **uvicorn**: ASGI server for running FastAPI applications

### Development Dependencies
- **pytest**: Testing framework
- **python-dotenv**: Environment variable management
- **httpx**: HTTP client for testing

## 🔒 Security

- **Firebase Authentication**: All API endpoints require valid Firebase user tokens
- **Token Validation**: Server-side verification of Firebase ID tokens
- **CORS Protection**: Configured CORS middleware for secure cross-origin requests
- **Environment Variables**: Sensitive configuration stored in environment variables

## 🚀 Deployment

### Local Development
```bash
# Start the API server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
1. **Set up a production server** (AWS, Google Cloud, etc.)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure environment variables** for production
4. **Use a production ASGI server** like Gunicorn:
   ```bash
   gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📞 Support

For support and questions:
- **Email**: jaime.santo@gmail.com
- **Issues**: Create an issue in the repository

## 🔄 Changelog

### Version 1.0.0
- Initial release with command-line interface
- REST API with FastAPI
- Firebase Storage integration
- OpenAI Agents for transcription and summarization
- Interactive API documentation
- Comprehensive test suite 