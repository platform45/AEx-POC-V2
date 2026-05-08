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

## Updating tables 

### Resolving Issues 

- The agentic functionality should be able to read, insert and update values in the `issue_resolve` table 

**Flow**
- It should begin by asking a question to get the device id which is then used to retrieve previous issues with the device for context 
- The next question should be what the issue is (description). This should result in a new table insert 
- After the initial insert, it should try to resolve the issue by checking for similar issues and providing a solution
- Then ask if the issue is resolved. If the user enters yes, the entry for that issue is marked as resolved. 
- If no, it should try again in the loop
- After a set number of tries (initially set to 2 max), print a message to direct the user to call support and the leave the issue as unresolved 