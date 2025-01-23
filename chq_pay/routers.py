from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SessionDatabaseRouter:
    """
    A database router to route database operations based on the session's db_key.
    """

    def db_for_read(self, model, **hints):
        """
        Route read operations to the appropriate database.
        """
        request = hints.get('request')
        if not request:
            logger.warning("No request provided; defaulting to 'default' database.")
            return 'default'

        db_key = request.session.get('reg_code', 'default')
        if db_key in settings.DATABASES:
            logger.debug(f"Routing read operation to database: {db_key}")
            return db_key

        logger.warning(f"Invalid db_key '{db_key}' in session; defaulting to 'default' database.")
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Route write operations to the appropriate database.
        """
        request = hints.get('request')
        if not request:
            logger.warning("No request provided; defaulting to 'default' database.")
            return 'default'

        db_key = request.session.get('reg_code', 'default')
        if db_key in settings.DATABASES:
            logger.debug(f"Routing write operation to database: {db_key}")
            return db_key

        logger.warning(f"Invalid db_key '{db_key}' in session; defaulting to 'default' database.")
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the same database.
        """
        db_set = {obj1._state.db, obj2._state.db}
        if len(db_set) == 1:
            return True
        logger.warning(f"Disallowing relation between objects in databases: {db_set}")
        return False
