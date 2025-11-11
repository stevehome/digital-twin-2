# Alias for lambda_handler to support both handler names
# This allows the Lambda function to work with handler: lambda_function.handler
# or handler: lambda_function.lambda_handler
from mangum import Mangum
from server import app
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create the Mangum adapter for API Gateway HTTP API
# API Gateway HTTP API v2 uses AWS_PROXY integration
# Mangum should auto-detect API Gateway HTTP API v2 events by checking for:
# - version: "2.0" 
# - routeKey: present
# - rawPath: present
mangum_adapter = Mangum(
    app,
    lifespan="off"  # Disable lifespan events for Lambda
)

# Wrapper function to handle API Gateway HTTP API events explicitly
def handler(event, context):
    """
    Lambda handler for API Gateway HTTP API (v2) events.
    This wrapper ensures Mangum can properly handle the event structure.
    """
    try:
        # Ensure event is a dict (API Gateway HTTP API v2 format)
        if not isinstance(event, dict):
            logger.error(f"Event is not a dict: {type(event)}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid event format'})
            }
        
        # API Gateway HTTP API v2 events should have version "2.0"
        # If not present, it might be a different event type
        event_version = event.get('version', '')
        route_key = event.get('routeKey', '')
        
        logger.info(f"Processing event - version: {event_version}, routeKey: {route_key}")
        
        # Ensure the event looks like an API Gateway HTTP API v2 event
        # If it doesn't have the expected structure, Mangum might fail to infer
        if event_version != "2.0" and not route_key:
            logger.warning(f"Event might not be API Gateway HTTP API v2 format. Keys: {list(event.keys())}")
        
        # Call Mangum adapter - it should auto-detect API Gateway HTTP API v2
        response = mangum_adapter(event, context)
        return response
        
    except RuntimeError as e:
        # If Mangum can't infer the handler, check if this is a test event
        event_keys = list(event.keys())
        
        # Check if this is a Lambda console test event (has key1, key2, key3)
        is_test_event = set(event_keys) == {'key1', 'key2', 'key3'} or 'key1' in event_keys
        
        if is_test_event:
            # This is a test invocation from Lambda console, not from API Gateway
            logger.info("Lambda invoked with test event (not from API Gateway)")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Lambda function is working!',
                    'note': 'This is a test event. Invoke through API Gateway to test the actual endpoints.',
                    'test_event': event,
                    'endpoints': {
                        'GET /': 'Root endpoint',
                        'GET /health': 'Health check',
                        'POST /chat': 'Chat endpoint'
                    }
                })
            }
        
        # Real API Gateway event that Mangum couldn't handle
        logger.error(f"Mangum inference error: {str(e)}")
        logger.error(f"Event structure - version: {event.get('version', 'N/A')}, routeKey: {event.get('routeKey', 'N/A')}")
        logger.error(f"Event keys: {event_keys}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Handler inference error',
                'message': 'Mangum could not determine the event handler type. This usually means the event format is not recognized as API Gateway HTTP API v2.',
                'event_version': event.get('version', 'unknown'),
                'event_keys': event_keys[:10]  # First 10 keys for debugging
            })
        }
    except Exception as e:
        # Log any other errors for debugging
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

# Export as lambda_handler as well for compatibility
lambda_handler = handler
