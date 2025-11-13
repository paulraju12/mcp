import traceback
import structlog
from typing import Dict, Any, Optional, List

from .vms_integration import vms_integration_service

logger = structlog.getLogger(__name__)


class VMSService:
    """Service for managing VMS operations"""

    DEFAULT_ASSET_ID = "default"  # Default asset ID for providers without asset support

    async def _check_provider_supports_assets(self, integration_id: str) -> bool:
        """
        Check if the provider supports assets by trying to list assets.
        If it fails or returns empty, the provider doesn't support assets.
        """
        try:
            result = await vms_integration_service.list_assets(
                integration_id=integration_id,
                offset=0,
                limit=1
            )

            if result["status"] == "success":
                data = result["data"]
                # Check if we have data structure and it's not empty or error
                if data and isinstance(data, dict):
                    assets_data = data.get("data", [])
                    # Even if no assets exist, if the API call succeeds, provider supports assets
                    return True
                return False
            else:
                logger.warning(
                    f"Provider {integration_id} does not support assets: {result.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            logger.warning(f"Provider {integration_id} does not support assets: {str(e)}")
            return False

    async def _get_asset_id_for_provider(self, integration_id: str, asset_id: Optional[str] = None) -> str:
        """
        Get the appropriate asset ID to use for the provider.
        If provider doesn't support assets, use default asset ID.
        """
        if asset_id:
            return asset_id

        # Check if provider supports assets
        supports_assets = await self._check_provider_supports_assets(integration_id)

        if not supports_assets:
            logger.info(f"Provider {integration_id} doesn't support assets, using default asset ID")
            return self.DEFAULT_ASSET_ID

        # If provider supports assets but no asset_id provided, we might need to get first available asset
        # or handle this case based on your business logic
        assets_result = await self.list_assets(integration_id=integration_id, limit=1)
        if assets_result["status"] == "success" and assets_result["data"]["assets"]:
            first_asset_id = assets_result["data"]["assets"][0].get("id")
            if first_asset_id:
                return first_asset_id

        # Fallback to default if no assets found
        return self.DEFAULT_ASSET_ID

    # ---------- VULNERABILITY OPERATIONS (Updated to use asset-based endpoints) ----------
    async def list_vulnerabilities(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            severity: Optional[str] = None,
            state: Optional[str] = None,
            cve: Optional[str] = None,
            search: Optional[str] = None,
            asset_id: Optional[str] = None,
            port: Optional[int] = None,
            protocol: Optional[str] = None,
            cvss_score_min: Optional[float] = None,
            cvss_score_max: Optional[float] = None,
            first_seen_from: Optional[str] = None,
            first_seen_to: Optional[str] = None,
            last_seen_from: Optional[str] = None,
            last_seen_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """List vulnerabilities using asset-based endpoint with comprehensive filtering options"""
        logger.info(f"Listing vulnerabilities for integration: {integration_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.list_vulnerabilities(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort,
                asset_id=effective_asset_id
            )

            if result["status"] == "success":
                vulnerabilities_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(vulnerabilities_data)} vulnerabilities for asset {effective_asset_id}",
                    "data": {
                        "vulnerabilities": vulnerabilities_data,
                        "pagination": pagination,
                        "asset_id": effective_asset_id,
                        "total_count": pagination.get("total", len(vulnerabilities_data)) if pagination else len(
                            vulnerabilities_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_vulnerabilities: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_asset_vulnerabilities(
            self,
            integration_id: str,
            asset_id: Optional[str] = None,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            severity: Optional[str] = None,
            state: Optional[str] = None
    ) -> Dict[str, Any]:
        """List vulnerabilities for a specific asset"""
        logger.info(f"Listing vulnerabilities for asset: {asset_id}, integration: {integration_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.list_asset_vulnerabilities(
                integration_id=integration_id,
                asset_id=effective_asset_id,
                offset=offset,
                limit=limit,
                sort=sort,
                severity=severity,
                state=state
            )

            if result["status"] == "success":
                vulnerabilities_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(vulnerabilities_data)} vulnerabilities for asset {effective_asset_id}",
                    "data": {
                        "vulnerabilities": vulnerabilities_data,
                        "pagination": pagination,
                        "asset_id": effective_asset_id,
                        "total_count": pagination.get("total", len(vulnerabilities_data)) if pagination else len(
                            vulnerabilities_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_asset_vulnerabilities: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_asset_vulnerability_details(
            self,
            integration_id: str,
            vulnerability_id: str,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific vulnerability for an asset"""
        logger.info(f"Getting vulnerability details: {vulnerability_id} for asset: {asset_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.get_asset_vulnerability(
                integration_id=integration_id,
                asset_id=effective_asset_id,
                vulnerability_id=vulnerability_id
            )

            if result["status"] == "success":
                vulnerability_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved vulnerability {vulnerability_id} details for asset {effective_asset_id}",
                    "data": {
                        "vulnerability": vulnerability_data,
                        "asset_id": effective_asset_id,
                        "vulnerability_id": vulnerability_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting vulnerability details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- ASSET OPERATIONS ----------
    async def list_assets(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            asset_type: Optional[str] = None,
            operating_system: Optional[str] = None,
            ip_address: Optional[str] = None,
            hostname: Optional[str] = None,
            domain: Optional[str] = None,
            tags: Optional[List[str]] = None,
            has_vulnerabilities: Optional[bool] = None,
            risk_score_min: Optional[float] = None,
            risk_score_max: Optional[float] = None,
            last_scan_from: Optional[str] = None,
            last_scan_to: Optional[str] = None,
            cloud_provider: Optional[str] = None,
            environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """List assets with comprehensive filtering options"""
        logger.info(f"Listing assets for integration: {integration_id}")
        try:
            result = await vms_integration_service.list_assets(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort
            )

            if result["status"] == "success":
                assets_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(assets_data)} assets",
                    "data": {
                        "assets": assets_data,
                        "pagination": pagination,
                        "total_count": pagination.get("total", len(assets_data)) if pagination else len(assets_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_assets: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_asset_details(
            self,
            integration_id: str,
            asset_id: str,
            include_vulnerabilities: Optional[bool] = None,
            include_scan_history: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific asset"""
        logger.info(f"Getting asset details for asset: {asset_id}")
        try:
            result = await vms_integration_service.get_asset(
                integration_id=integration_id,
                asset_id=asset_id
            )

            if result["status"] == "success":
                asset_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved asset details for {asset_id}",
                    "data": {
                        "asset": asset_data,
                        "asset_id": asset_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting asset details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- SCAN OPERATIONS (Updated to use asset-based endpoints) ----------
    async def list_scans(
            self,
            integration_id: str,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            scan_type: Optional[str] = None,
            status: Optional[str] = None,
            scanner_name: Optional[str] = None,
            target: Optional[str] = None,
            start_time_from: Optional[str] = None,
            start_time_to: Optional[str] = None,
            end_time_from: Optional[str] = None,
            end_time_to: Optional[str] = None,
            has_findings: Optional[bool] = None,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List scans using asset-based endpoint with filtering options"""
        logger.info(f"Listing scans for integration: {integration_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.list_scans(
                integration_id=integration_id,
                offset=offset,
                limit=limit,
                sort=sort,
                asset_id=effective_asset_id
            )

            if result["status"] == "success":
                scans_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(scans_data)} scans for asset {effective_asset_id}",
                    "data": {
                        "scans": scans_data,
                        "pagination": pagination,
                        "asset_id": effective_asset_id,
                        "total_count": pagination.get("total", len(scans_data)) if pagination else len(scans_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_scans: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_scan_details(
            self,
            integration_id: str,
            scan_id: str,
            include_assets: Optional[bool] = None,
            include_vulnerabilities: Optional[bool] = None,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific scan using asset-based endpoint"""
        logger.info(f"Getting scan details for scan: {scan_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.get_scan(
                integration_id=integration_id,
                scan_id=scan_id,
                asset_id=effective_asset_id
            )

            if result["status"] == "success":
                scan_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved scan details for {scan_id} on asset {effective_asset_id}",
                    "data": {
                        "scan": scan_data,
                        "scan_id": scan_id,
                        "asset_id": effective_asset_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting scan details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def list_asset_scans(
            self,
            integration_id: str,
            asset_id: Optional[str] = None,
            offset: int = 0,
            limit: int = 20,
            sort: Optional[str] = None,
            status: Optional[str] = None,
            scan_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """List scans for a specific asset"""
        logger.info(f"Listing scans for asset: {asset_id}, integration: {integration_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.list_asset_scans(
                integration_id=integration_id,
                asset_id=effective_asset_id,
                offset=offset,
                limit=limit,
                sort=sort,
                status=status,
                scan_type=scan_type
            )

            if result["status"] == "success":
                scans_data = result["data"].get("data", [])
                pagination = result["data"].get("pagination")

                return {
                    "status": "success",
                    "message": f"Retrieved {len(scans_data)} scans for asset {effective_asset_id}",
                    "data": {
                        "scans": scans_data,
                        "pagination": pagination,
                        "asset_id": effective_asset_id,
                        "total_count": pagination.get("total", len(scans_data)) if pagination else len(scans_data)
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error in list_asset_scans: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_asset_scan_details(
            self,
            integration_id: str,
            scan_id: str,
            asset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific scan for an asset"""
        logger.info(f"Getting scan details: {scan_id} for asset: {asset_id}")
        try:
            # Get the appropriate asset ID for the provider
            effective_asset_id = await self._get_asset_id_for_provider(integration_id, asset_id)

            result = await vms_integration_service.get_asset_scan(
                integration_id=integration_id,
                asset_id=effective_asset_id,
                scan_id=scan_id
            )

            if result["status"] == "success":
                scan_data = result["data"]

                return {
                    "status": "success",
                    "message": f"Retrieved scan {scan_id} details for asset {effective_asset_id}",
                    "data": {
                        "scan": scan_data,
                        "asset_id": effective_asset_id,
                        "scan_id": scan_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting asset scan details: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # ---------- ANALYTICS AND REPORTING ----------
    async def get_vulnerability_summary(
            self,
            integration_id: str,
            group_by: Optional[str] = None,
            filter_severity: Optional[List[str]] = None,
            filter_state: Optional[List[str]] = None,
            date_range_from: Optional[str] = None,
            date_range_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get vulnerability summary and statistics"""
        logger.info(f"Getting vulnerability summary for integration: {integration_id}")
        try:
            # This would typically call a dedicated summary endpoint
            # For now, we'll get recent vulnerabilities and summarize
            result = await self.list_vulnerabilities(
                integration_id=integration_id,
                limit=1000  # Get larger set for summary
            )

            if result["status"] == "success":
                vulnerabilities = result["data"]["vulnerabilities"]

                # Basic summary calculation
                summary = {
                    "total_vulnerabilities": len(vulnerabilities),
                    "by_severity": {},
                    "by_state": {},
                    "high_risk_assets": 0,
                    "recent_discoveries": 0
                }

                for vuln in vulnerabilities:
                    # Count by severity
                    severity = vuln.get("severity", "Unknown")
                    summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1

                    # Count by state
                    state = vuln.get("state", "Unknown")
                    summary["by_state"][state] = summary["by_state"].get(state, 0) + 1

                return {
                    "status": "success",
                    "message": "Generated vulnerability summary",
                    "data": {
                        "summary": summary,
                        "integration_id": integration_id
                    }
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error getting vulnerability summary: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    async def get_asset_risk_assessment(
            self,
            integration_id: str,
            asset_id: Optional[str] = None,
            top_n: int = 10,
            risk_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get asset risk assessment and rankings"""
        logger.info(f"Getting asset risk assessment for integration: {integration_id}")
        try:
            if asset_id:
                # Get specific asset risk
                result = await self.get_asset_details(integration_id, asset_id)
                if result["status"] == "success":
                    asset = result["data"]["asset"]
                    risk_data = {
                        "asset_id": asset_id,
                        "risk_score": asset.get("riskScore"),
                        "vulnerability_count": asset.get("vulnerabilityCount"),
                        "exploitability": asset.get("exploitability"),
                        "vulnerability_summary": asset.get("vulnerabilitySummary")
                    }
                    return {
                        "status": "success",
                        "message": f"Retrieved risk assessment for asset {asset_id}",
                        "data": {"risk_assessment": risk_data}
                    }
            else:
                # Get top risky assets
                assets_result = await self.list_assets(
                    integration_id=integration_id,
                    limit=top_n * 2,  # Get more to filter by risk
                    sort="-riskScore"  # Sort by risk score descending
                )

                if assets_result["status"] == "success":
                    assets = assets_result["data"]["assets"]
                    risk_assessments = []

                    for asset in assets[:top_n]:
                        if risk_threshold is None or float(asset.get("riskScore", "0")) >= risk_threshold:
                            risk_assessments.append({
                                "asset_id": asset.get("id"),
                                "hostname": asset.get("hostname"),
                                "risk_score": asset.get("riskScore"),
                                "vulnerability_count": asset.get("vulnerabilityCount"),
                                "exploitability": asset.get("exploitability"),
                                "vulnerability_summary": asset.get("vulnerabilitySummary")
                            })

                    return {
                        "status": "success",
                        "message": f"Retrieved top {len(risk_assessments)} risky assets",
                        "data": {"risk_assessments": risk_assessments}
                    }

            return assets_result

        except Exception as e:
            logger.error(f"Error getting asset risk assessment: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }


# Global VMS service instance
vms_service = VMSService()