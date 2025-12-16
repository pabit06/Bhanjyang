# API Endpoints Reference

Complete reference of all available API endpoints.

## News & Events API

### Get News Articles
```
GET /api/news-events/articles/
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `category` - Filter by category
- `search` - Search query

**Response:**
```json
{
    "count": 100,
    "next": "http://api.example.com/api/news-events/articles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Article Title",
            "content": "...",
            "published_date": "2025-12-16T10:00:00Z",
            "author": "Author Name",
            "category": "news"
        }
    ]
}
```

### Get Single Article
```
GET /api/news-events/articles/{id}/
```

### Get Events
```
GET /api/news-events/events/
```

## Services API

### Get Services
```
GET /api/services/
```

### Get Service Details
```
GET /api/services/{slug}/
```

## Downloads API

### Get Downloadable Files
```
GET /api/downloads/files/
```

### Download File
```
GET /api/downloads/files/{id}/download/
```

## Gallery API

### Get Gallery Images
```
GET /api/gallery/images/
```

### Get Albums
```
GET /api/gallery/albums/
```

## Contact API

### Submit Contact Form
```
POST /api/contact/submit/
```

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Inquiry",
    "message": "Message content"
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Server Error

