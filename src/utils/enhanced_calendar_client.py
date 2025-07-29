"""
Enhanced Calendar Client with Retry Logic, Circuit Breaker, and Resource Management
"""
import os
import asyncio
import httpx
import logging
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker moving to HALF_OPEN state")
            else:
                raise CircuitBreakerOpenException("Calendar service temporarily unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (self.last_failure_time and 
                datetime.now().timestamp() - self.last_failure_time > self.recovery_timeout)
    
    def _on_success(self):
        if self.state == 'HALF_OPEN':
            logger.info("Circuit breaker reset to CLOSED state")
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now().timestamp()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")

class EnhancedCalendarClient:
    """Enhanced calendar client with resilience patterns"""
    
    def __init__(self, calendar_url: Optional[str] = None):
        self.calendar_url = calendar_url or os.getenv('CALENDAR_URL', 'http://localhost:3005')
        self._client = None
        self._closed = False
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        self.max_retries = 3
        
        logger.info(f"Enhanced calendar client initialized with URL: {self.calendar_url}")
    
    @property
    def client(self):
        """Lazy initialization of HTTP client"""
        if self._client is None:
            timeout = httpx.Timeout(10.0, connect=5.0, read=15.0, write=10.0)
            limits = httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            )
            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                http2=True
            )
        return self._client
    
    async def close(self):
        """Properly close the client and cleanup resources"""
        if self._client and not self._closed:
            await self._client.aclose()
            self._closed = True
            logger.info("Calendar client closed")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def health_check(self) -> bool:
        """Check if calendar service is healthy"""
        try:
            response = await self.client.get(
                f"{self.calendar_url}/health",
                timeout=5.0
            )
            healthy = response.status_code == 200
            logger.info(f"Calendar health check: {'healthy' if healthy else 'unhealthy'}")
            return healthy
        except Exception as e:
            logger.warning(f"Calendar health check failed: {e}")
            return False
    
    @retry(
        retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request with retry logic"""
        try:
            url = f"{self.calendar_url}{endpoint}"
            response = await getattr(self.client, method.lower())(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                logger.warning(f"Server error {e.response.status_code}, will retry")
                raise
            else:
                logger.error(f"Client error {e.response.status_code}: {e}")
                return {
                    "success": False, 
                    "message": f"Service error: {e.response.status_code}",
                    "error_code": f"HTTP_{e.response.status_code}"
                }
        except (httpx.ConnectTimeout, httpx.TimeoutException) as e:
            logger.warning(f"Timeout error, will retry: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False, 
                "message": "Unerwarteter Fehler beim Kalender-Zugriff",
                "error_code": "UNEXPECTED_ERROR"
            }
    
    async def _safe_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make request with circuit breaker protection"""
        try:
            return await self.circuit_breaker.call(self._make_request, method, endpoint, **kwargs)
        except CircuitBreakerOpenException as e:
            logger.error(f"Circuit breaker open: {e}")
            return {
                "success": False,
                "message": "Kalender-Service ist überlastet. Bitte versuchen Sie es in wenigen Minuten erneut.",
                "error_code": "CIRCUIT_BREAKER_OPEN"
            }
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "message": f"Verbindungsfehler zum Kalender: {str(e)}",
                "error_code": "CONNECTION_ERROR"
            }
    
    async def book_appointment(
        self,
        patient_name: str,
        patient_phone: str,
        requested_date: str,
        requested_time: str,
        treatment_type: str = "Beratung"
    ) -> Dict[Any, Any]:
        """Book an appointment with enhanced error handling"""
        start_time = datetime.now()
        
        # Hash phone for privacy in logs
        phone_hash = hashlib.sha256(patient_phone.encode()).hexdigest()[:8]
        
        logger.info(f"Booking attempt for patient {phone_hash} on {requested_date} at {requested_time}")
        
        try:
            # Check health before booking
            if not await self.health_check():
                return {
                    "success": False,
                    "message": "Kalender-Service ist momentan nicht verfügbar. Bitte rufen Sie uns direkt an.",
                    "error_code": "SERVICE_UNAVAILABLE"
                }
            
            result = await self._safe_request(
                "POST",
                "/api/sofia/appointment",
                json={
                    "patientName": patient_name,
                    "patientPhone": patient_phone,
                    "requestedDate": requested_date,
                    "requestedTime": requested_time,
                    "treatmentType": treatment_type
                }
            )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            success = result.get("success", False)
            
            logger.info(f"Booking result for {phone_hash}: success={success}, duration={duration:.0f}ms")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Booking failed for {phone_hash} after {duration:.0f}ms: {e}")
            return {
                "success": False,
                "message": f"Terminbuchung fehlgeschlagen: {str(e)}",
                "error_code": "BOOKING_ERROR"
            }
    
    async def get_next_available(self) -> Dict[Any, Any]:
        """Get next available appointment slot"""
        return await self._safe_request("GET", "/api/sofia/next-available")
    
    async def check_date_availability(self, date: str) -> Dict[Any, Any]:
        """Check availability for specific date"""
        return await self._safe_request("GET", f"/api/sofia/check-date/{date}")
    
    async def get_suggestions(self, days: int = 7, limit: int = 5) -> Dict[Any, Any]:
        """Get appointment suggestions"""
        return await self._safe_request("GET", f"/api/sofia/suggest-times?days={days}&limit={limit}")
    
    async def get_today_appointments(self) -> Dict[Any, Any]:
        """Get today's appointments"""
        return await self._safe_request("GET", "/api/sofia/today")
    
    async def get_patient_appointments(self, phone: str) -> Dict[Any, Any]:
        """Get patient's appointments"""
        phone_hash = hashlib.sha256(phone.encode()).hexdigest()[:8]
        logger.info(f"Fetching appointments for patient {phone_hash}")
        return await self._safe_request("GET", f"/api/sofia/patient/{phone}")

# Global client manager
class CalendarClientManager:
    """Manages calendar client lifecycle"""
    
    def __init__(self):
        self._client = None
    
    async def get_client(self) -> EnhancedCalendarClient:
        """Get singleton client instance"""
        if self._client is None:
            self._client = EnhancedCalendarClient()
        return self._client
    
    async def shutdown(self):
        """Shutdown client gracefully"""
        if self._client:
            await self._client.close()
            self._client = None

# Global manager instance
calendar_manager = CalendarClientManager()

@asynccontextmanager
async def get_calendar_client():
    """Context manager for calendar client"""
    client = await calendar_manager.get_client()
    try:
        yield client
    finally:
        # Client lifecycle managed by manager
        pass