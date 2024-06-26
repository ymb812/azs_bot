from core.handlers.welcome import router as welcome_router
from core.handlers.basic import router as basic_router
from core.handlers.admin import router as admin_router
from core.handlers.inline_mode import router as inline_router
from core.handlers.payment import router as payment_router


routers = [welcome_router, basic_router, admin_router, inline_router, payment_router]
