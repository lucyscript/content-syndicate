#!/usr/bin/env python3
"""
Simple server startup script
"""
import uvicorn

if __name__ == "__main__":    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=False  # Disable reload for now
    )
