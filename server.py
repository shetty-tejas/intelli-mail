from app import app

if __name__ == "__main__":
    print("Starting IntellliMail MCP server on port 8000...")
    print("Connect to this server using http://localhost:8000/mcp")
    app.run(transport="http", host="0.0.0.0", port=8000)
