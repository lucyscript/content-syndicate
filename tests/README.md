# ContentSyndicate Test Suite

This directory contains comprehensive test scripts to help debug the newsletter persistence issue and validate the entire application stack.

## Quick Start

Run the quick diagnostic test first to get an overview:

```bash
python tests/quick_test.py
```

## Test Scripts

### 1. `quick_test.py` - 🚀 Quick Diagnostic
**Purpose**: Fast overview of all system components
**What it checks**:
- Database connectivity and data
- File structure integrity
- Server processes (ports 3000, 8000)
- API endpoints
- Frontend proxy
- Newsletter creation flow

**Run**: `python tests/quick_test.py`

### 2. `test_database.py` - 🗃️ Database Deep Dive
**Purpose**: Comprehensive database testing
**What it checks**:
- Database file existence and connectivity
- Table schema validation
- User and newsletter data integrity
- Creates test data
- Checks for orphaned records

**Run**: `python tests/test_database.py`

### 3. `test_api.py` - 📡 API Endpoint Testing
**Purpose**: Backend API validation
**What it checks**:
- API server health
- Newsletter CRUD endpoints
- Content generation endpoints
- Authentication requirements
- CORS headers
- Response formats

**Run**: `python tests/test_api.py`

### 4. `test_integration.py` - 🔗 Frontend-Backend Integration
**Purpose**: End-to-end integration testing
**What it checks**:
- Frontend server status
- API proxy functionality
- Direct backend vs proxy comparison
- Environment variable configuration
- Data consistency across endpoints
- Complete newsletter creation flow

**Run**: `python tests/test_integration.py`

## Running Tests

### Prerequisites
Make sure you have the required dependencies:
```bash
pip install httpx  # For API testing
```

### Individual Tests
```bash
# Quick overview
python tests/quick_test.py

# Database deep dive
python tests/test_database.py

# API testing (requires backend running on :8000)
python tests/test_api.py

# Integration testing (requires both servers running)
python tests/test_integration.py
```

### Server Requirements
For full testing, you need both servers running:

**Backend** (Terminal 1):
```bash
cd app
python main.py
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

## Common Issues & Solutions

### Database Issues
- **Database file missing**: Run migrations or check `.env` DATABASE_URL
- **Empty tables**: Check if migrations ran successfully
- **Orphaned newsletters**: Newsletters without user_id won't show up

### API Issues
- **Connection refused**: Backend server not running on port 8000
- **401 Unauthorized**: Authentication not configured or tokens invalid
- **CORS errors**: Check CORS configuration in backend

### Frontend Issues
- **Proxy errors**: Check Next.js API routes in `/frontend/src/app/api/`
- **Data not showing**: Check React hooks and component state management
- **Hydration errors**: Check client/server rendering mismatches

### Integration Issues
- **Data inconsistency**: Backend and frontend showing different data
- **Creation works but listing doesn't**: Check API response formats
- **Authentication flow**: User login state not properly managed

## Debugging Workflow

1. **Start with Quick Test**: `python tests/quick_test.py`
   - Gets overview of what's working/broken
   - Identifies which area needs focus

2. **Database Issues**: `python tests/test_database.py`
   - Verifies data is actually being saved
   - Checks table structure and relationships

3. **API Issues**: `python tests/test_api.py`
   - Tests backend endpoints directly
   - Validates response formats and authentication

4. **Integration Issues**: `python tests/test_integration.py`
   - Tests frontend-backend communication
   - Validates end-to-end data flow

## Expected Output

### Healthy System
All tests should show:
- ✅ Database connected with newsletters present
- ✅ Backend API responding with newsletter data
- ✅ Frontend proxy working correctly
- ✅ Newsletter creation and listing working

### Common Problem Indicators
- ❌ Database has 0 newsletters (creation not working)
- ❌ Backend returns empty list (database query issue)
- ❌ Frontend proxy errors (API route configuration)
- ❌ Data inconsistency (caching or state management issue)

## Troubleshooting Tips

1. **Check Environment Variables**: Ensure `.env` file has correct DATABASE_URL
2. **Verify Server Ports**: Backend on 8000, Frontend on 3000
3. **Database Location**: Should be `./db/contentsyndicate.db`
4. **API Routes**: Check `/frontend/src/app/api/newsletters/route.ts`
5. **React Hooks**: Check `/frontend/src/hooks/useNewsletters.ts`

---

*These tests are designed to quickly identify and isolate the newsletter persistence issue. Start with `quick_test.py` and drill down based on the results.*
