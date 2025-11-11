from mangum import Mangum
from server import app

# Create the Lambda handler with explicit configuration for API Gateway HTTP API
handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events for Lambda
    log_level="info"  # Set log level
)