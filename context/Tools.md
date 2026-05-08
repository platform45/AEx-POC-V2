# Tool Use Functionality Context

- A core next functionality is to simulate 'taking actions'. Example, making changes to a database
- A Support Agent function to assist with diagnostics and queries and then take actions 

## Functionality Examples 

**1. Updating a value in the database**
A user submits an error that has occurred and the application adds it to the database by asking for the required details such as: 
- Device id 
- Incident description 

## Code Architecture

- A `agent_tools` folder needs to be created in `/backend/app` if it doesn't exist. This will function similar to `/backend/app/agent` but host code for defining and managing agentic tool usage 
- Tool usage will be agent and make use of the claude ecosystem 