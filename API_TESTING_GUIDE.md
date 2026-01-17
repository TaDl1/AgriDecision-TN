# 🧪 AgriDecision-TN API Testing Guide

Complete guide for testing all API endpoints using Postman or Insomnia.

---

## 📋 Table of Contents

1. [Setup](#setup)
2. [Authentication Endpoints](#authentication-endpoints)
3. [Crop Endpoints](#crop-endpoints)
4. [Decision Endpoints](#decision-endpoints)
5. [Analytics Endpoints](#analytics-endpoints)
6. [Health Check Endpoints](#health-check-endpoints)
7. [Error Handling](#error-handling)

---

## 🔧 Setup

### Base URL
```
Development: http://localhost:5000
Production: https://api.agridecision.tn
```

### Environment Variables
Create these variables in Postman/Insomnia:
```json
{
  "BASE_URL": "http://localhost:5000",
  "TOKEN": "",
  "USER_ID": "",
  "TEST_PHONE": "21699999999",
  "TEST_PASSWORD": "TestPass123"
}
```

---

## 🔐 Authentication Endpoints

### 1. Register New Farmer

**POST** `/api/auth/register`

**Request:**
```json
{
  "phone_number": "21612345678",
  "password": "SecurePass123",
  "governorate": "Tunis",
  "farm_type": "rain_fed"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "farmer_id": 1
}
```

**Validation Rules:**
- Phone: Must be `216XXXXXXXX` format
- Password: Min 8 chars, must include letter + number
- Governorate: Must be one of 24 Tunisian governorates
- Farm type: Either `rain_fed` or `irrigated`

---

### 2. Login

**POST** `/api/auth/login`

**Request:**
```json
{
  "phone": "21612345678",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "phone": "21612345678",
    "governorate": "Tunis",
    "farm_type": "rain_fed",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**⚠️ Important:** Save the `token` value for subsequent requests!

---

### 3. Get Current User

**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer {TOKEN}
```

**Response (200):**
```json
{
  "id": 1,
  "phone": "21612345678",
  "governorate": "Tunis",
  "farm_type": "rain_fed",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 🌾 Crop Endpoints

### 4. Get All Crops

**GET** `/api/crops/`

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Wheat",
    "category": "field",
    "icon": "🌾"
  },
  {
    "id": 2,
    "name": "Tomato",
    "category": "vegetable",
    "icon": "🍅"
  }
  // ... 11 crops total
]
```

---

### 5. Get Crop Details

**GET** `/api/crops/1`

**Response (200):**
```json
{
  "id": 1,
  "name": "Wheat",
  "scientific_name": "Triticum",
  "min_temp": 5.0,
  "max_temp": 28.0,
  "water_needs": "medium"
}
```

---

## 🎯 Decision Endpoints

### 6. Get Planting Advice (MAIN ENDPOINT)

**POST** `/api/decisions/get-advice`

**Headers:**
```
Authorization: Bearer {TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "crop_id": 2,
  "governorate": "Tunis"
}
```

**Response (200) - PLANT NOW:**
```json
{
  "status": "success",
  "data": {
    "decision": {
      "action": "PLANT_NOW",
      "wait_days": 0,
      "confidence": "HIGH",
      "reason": "Optimal period with favorable weather"
    },
    "period": {
      "id": "P4",
      "name": "Spring Stability",
      "risk": "low",
      "description": "Optimal planting conditions"
    },
    "weather_forecast": [
      {
        "date": "2024-03-15",
        "temp_min": 12.0,
        "temp_max": 22.0,
        "temp_avg": 17.0,
        "humidity": 60,
        "wind": 12.0,
        "rainfall": 0.0,
        "description": "Clear"
      }
      // ... 7 days total
    ],
    "weather_analysis": {
      "risks": [],
      "avg_temp": 18.5
    },
    "explanation": "Good time to plant Tomato now. The Spring Stability period provides ideal conditions for growth and weather is favorable."
  }
}
```

**Response (200) - WAIT:**
```json
{
  "status": "success",
  "data": {
    "decision": {
      "action": "WAIT",
      "wait_days": 5,
      "confidence": "HIGH",
      "reason": "Severe weather risk: frost_risk"
    },
    "period": {
      "id": "P3",
      "name": "Early Spring Transition",
      "risk": "medium"
    },
    "weather_analysis": {
      "risks": [
        {
          "type": "frost_risk",
          "severity": "high",
          "date": "2024-03-16"
        },
        {
          "type": "low_temperature",
          "severity": "medium",
          "date": "2024-03-17"
        }
      ]
    },
    "explanation": "Wait 5 days before planting Tomato. The Early Spring Transition period has cold nights expected that could harm young plants."
  }
}
```

**Response (200) - NOT RECOMMENDED:**
```json
{
  "status": "success",
  "data": {
    "decision": {
      "action": "NOT_RECOMMENDED",
      "confidence": "HIGH",
      "reason": "Not in the planting season."
    },
    "period": {
      "id": "P6",
      "name": "Peak Summer Risk",
      "risk": "high"
    },
    "explanation": "Tomato is not recommended right now. This is Peak Summer Risk period with high risks. Consider planting in a different season."
  }
}
```

---

### 7. Get Decision History

**GET** `/api/decisions/history`

**Headers:**
```
Authorization: Bearer {TOKEN}
```

**Response (200):**
```json
[
  {
    "id": 15,
    "date": "2024-03-15T10:30:00",
    "crop_name": "Tomato",
    "recommendation": "PLANT_NOW",
    "explanation": "Good time to plant...",
    "weather_temp": 18.5
  },
  {
    "id": 14,
    "date": "2024-03-10T14:20:00",
    "crop_name": "Wheat",
    "recommendation": "WAIT",
    "explanation": "Wait 7 days...",
    "weather_temp": 12.3
  }
  // ... up to 20 most recent
]
```

---

### 8. Record Outcome

**POST** `/api/decisions/record-outcome`

**Headers:**
```
Authorization: Bearer {TOKEN}
Content-Type: application/json
```

**Request:**
```json
{
  "decision_id": 15,
  "outcome": "success",
  "yield_kg": 450.5,
  "revenue_tnd": 2250.0,
  "notes": "Excellent harvest, followed advice exactly"
}
```

**Response (200):**
```json
{
  "status": "recorded",
  "message": "Outcome recorded successfully"
}
```

**Validation:**
- `outcome`: Must be `success`, `failure`, or `unknown`
- `yield_kg`: Optional, must be >= 0
- `revenue_tnd`: Optional, must be >= 0
- `notes`: Optional, max 500 characters

---

## 📊 Analytics Endpoints

### 9. Personal Analytics

**GET** `/api/analytics/personal`

**Headers:**
```
Authorization: Bearer {TOKEN}
```

**Response (200):**
```json
{
  "total_decisions": 25,
  "success_rate": "85%",
  "risk_avoided_count": 8,
  "estimated_savings": 1600
}
```

**Metrics Explanation:**
- `total_decisions`: Total advice requests
- `success_rate`: Percentage of successful outcomes
- `risk_avoided_count`: Number of "WAIT" recommendations followed
- `estimated_savings`: TND saved by avoiding risks (200 TND per avoided risk)

---

### 10. System Analytics (Admin)

**GET** `/api/analytics/system`

**Headers:**
```
Authorization: Bearer {ADMIN_TOKEN}
```

**Response (200):**
```json
{
  "total_farmers": 150,
  "total_decisions": 1250,
  "most_popular_crop_id": 2
}
```

---

## 🏥 Health Check Endpoints

### 11. Basic Health Check

**GET** `/api/health`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

### 12. Detailed Health Check

**GET** `/api/health/detailed`

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-15T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "healthy": true,
      "message": "Database connected",
      "response_time_ms": 5.2
    },
    "weather_api": {
      "healthy": true,
      "message": "Weather API responsive",
      "response_time_ms": 245.8
    },
    "ai_service": {
      "healthy": true,
      "message": "AI service available",
      "response_time_ms": 1250.3
    }
  },
  "uptime_seconds": 3600,
  "memory_usage_mb": 125.4
}
```

---

## ❌ Error Handling

All endpoints return consistent error responses:

### 400 - Validation Error
```json
{
  "error": "Validation failed",
  "status": "error",
  "errors": {
    "phone_number": ["Phone number must be Tunisian format (216XXXXXXXX)"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

### 401 - Authentication Error
```json
{
  "error": "Invalid credentials",
  "status": "error"
}
```

### 404 - Not Found
```json
{
  "error": "Resource not found",
  "status": "error"
}
```

### 429 - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "status": "error"
}
```

### 500 - Server Error
```json
{
  "error": "An unexpected error occurred",
  "status": "error"
}
```

### 503 - External Service Error
```json
{
  "error": "Weather service temporarily unavailable",
  "status": "error"
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Complete User Journey
1. Register new user
2. Login and save token
3. Get all crops
4. Get advice for Tomato in Spring
5. Record successful outcome
6. Check personal analytics

### Scenario 2: Weather-Dependent Decision
1. Login
2. Get advice for Tomato in Early Spring (P3)
3. Should return WAIT with frost risk
4. Check weather_analysis for specific risks

### Scenario 3: Forbidden Period
1. Login
2. Get advice for Wheat in Summer (P6)
3. Should return NOT_RECOMMENDED

### Scenario 4: Error Handling
1. Try to access protected endpoint without token (401)
2. Try to register with invalid phone format (400)
3. Try to get advice with invalid crop_id (400)

---

## 📦 Postman Collection

Import the complete collection from: `postman/AgriDecision-TN.postman_collection.json`

The collection includes:
- All 12 endpoints
- Pre-configured requests
- Environment variables
- Test scripts
- Example responses

---

## 🔄 Rate Limits

Default rate limits:
- **100 requests per day** per IP
- **10 requests per minute** per IP

For higher limits, contact API administrator.

---

## 📝 Notes

1. **JWT Tokens expire after 7 days** - re-login if you get 401 errors
2. **Weather data is cached for 5 minutes** to reduce API calls
3. **AI explanations have fallback templates** if OpenAI is unavailable
4. **All timestamps are in UTC**
5. **Governorate parameter is optional** - uses user's default if not provided

---

**Happy Testing! 🧪**