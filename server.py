from mcp.server.fastmcp import FastMCP
from tools import logs as logs_tool
from tools import summaries as summaries_tool

mcp = FastMCP("CloudWatch MCP")


@mcp.tool()
def get_error_logs():
    """Return all ERROR and CRITICAL logs"""
    return logs_tool.get_error_logs()


@mcp.tool()
def get_logs_by_service(service_name: str):
    """Return logs for a specific service"""
    return logs_tool.get_logs_by_service(service_name)


@mcp.tool()
def get_logs_by_level(level: str):
    """Return logs for a specific severity level"""
    return logs_tool.get_logs_by_level(level)


@mcp.tool()
def list_services():
    """List available services in logs"""
    return logs_tool.list_services()


@mcp.tool()
def summarize_errors():
    """Return a summary of recent errors"""
    return summaries_tool.summarize_errors()


if __name__ == "__main__":
    mcp.run()