import os
import sys
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Required environment variables
REQUIRED_ENV_VARS = [
    "ENVIRONMENT",
    "INTEGRATION_MGR_BASE_URL",
    "TICKETING_API_BASE_URL",
    "IDENTITY_API_BASE_URL",
    "DEV_INTEGRATION_MGR_BASE_URL",
    "DEV_TICKETING_API_BASE_URL",
    "DEV_IDENTITY_API_BASE_URL"
]


class Settings:
    def __init__(self):
        # Validate required environment variables
        missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)

        # Environment configuration
        self.environment = os.getenv("ENVIRONMENT", "prod").lower()
        # Redis configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://dragonfly-svc:6379")

        #API URLs based on environment
        if self.environment == "dev":
            self.integration_mgr_base_url = os.getenv("DEV_INTEGRATION_MGR_BASE_URL")
            self.ticketing_api_base_url = os.getenv("DEV_TICKETING_API_BASE_URL")
            self.identity_api_base_url = os.getenv("DEV_IDENTITY_API_BASE_URL")
            self.incident_api_base_url=os.getenv("DEV_INCIDENT_API_BASE_URL")
            self.scm_api_base_url=os.getenv("DEV_SCM_API_BASE_URL")
            self.pcr_api_base_url=os.getenv("DEV_PCR_API_BASE_URL")
            self.comms_api_base_url = os.getenv("DEV_COMMS_API_BASE_URL")
            self.key_management_api_base_url = os.getenv("DEV_KEY_MANAGEMENT_API_BASE_URL")
            self.vms_api_base_url = os.getenv("DEV_VMS_API_BASE_URL")
            self.observability_api_base_url = os.getenv("DEV_OBSERVABILITY_API_BASE_URL")
            self.infra_api_base_url = os.getenv("DEV_INFRA_API_BASE_URL")
            self.edr_api_base_url=os.getenv("DEV_EDR_API_BASE_URL")
            self.storage_api_base_url=os.getenv("DEV_STORAGE_API_BASE_URL")
        else:
            self.integration_mgr_base_url = os.getenv("INTEGRATION_MGR_BASE_URL")
            self.ticketing_api_base_url = os.getenv("TICKETING_API_BASE_URL")
            self.identity_api_base_url = os.getenv("IDENTITY_API_BASE_URL")
            self.incident_api_base_url = os.getenv("INCIDENT_API_BASE_URL")
            self.scm_api_base_url = os.getenv("SCM_API_BASE_URL")
            self.pcr_api_base_url = os.getenv("PCR_API_BASE_URL")
            self.comms_api_base_url = os.getenv("COMMS_API_BASE_URL")
            self.key_management_api_base_url=os.getenv("KEY_MANAGEMENT_API_BASE_URL")
            self.vms_api_base_url=os.getenv("VMS_API_BASE_URL")
            self.observability_api_base_url=os.getenv("OBSERVABILITY_API_BASE_URL")
            self.infra_api_base_url = os.getenv("INFRA_API_BASE_URL")
            self.edr_api_base_url = os.getenv("EDR_API_BASE_URL")
            self.storage_api_base_url = os.getenv("STORAGE_API_BASE_URL")

        # HTTP settings
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.log_level, logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        )


# Create global settings instance

settings = Settings()