import logging

# Configure logging for the module name
logger = logging.getLogger(__name__)

# Helper to handle flash messages of the system
def set_flash(request, message, message_type = "success"):
    # Restart session flash if it is not a list already
    if type(request.session.get("flash")) != list:
        request.session["flash"] = []
    
    request.session["flash"] += [{ 'type': message_type, 'message': message }]

    if message_type == "danger":
        logger.warning(message)
    
# Clears flash from session
def clear_flash(request):
    request.session["flash"] = []
    
# Returns current flash messages and clears flash from session
def get_flash(request):
    if type(request.session.get("flash")) == list:
        tmp_flash = request.session["flash"]
    else:
        tmp_flash = []

    clear_flash(request)
    return tmp_flash
