import os
import re
import time
import asyncio
import json
from typing import Dict, List, Any, Optional
import logging

from agents.base import Agent, AgentMetadata
from tools.file_tool import FileTool
from llm.ollama_wrapper import OllamaLLM
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.agents.code')

class CodeAgent(Agent):
    """
    Enhanced code generation agent with improved capabilities
    
    - Project-based code organization
    - Multi-file project generation
    - Code execution capabilities
    - VSCode integration
    - History and version tracking
    """
    
    def __init__(self, llm_model: str = "deepseek-coder"):
        super().__init__()
        self.file_tool = FileTool()
        self.llm = OllamaLLM(llm_model)
        self.current_project = None
    
    def _initialize_metadata(self) -> AgentMetadata:
        """Initialize agent metadata"""
        return AgentMetadata(
            name="code",
            description="Generates code based on natural language descriptions",
            version="1.0.0",
            required_tools=["file", "command"],
            capabilities=[
                "code_generation",
                "project_scaffolding",
                "file_management",
                "refactoring"
            ]
        )
    
    def _execute(self, input_text: str) -> str:
        """Execute agent logic for code generation"""
        logger.info(f"[CodeAgent] Generating code for: {input_text}")
        
        # Parse input to determine mode
        mode = self._detect_mode(input_text)
        
        if mode == "new_project":
            return self._create_new_project(input_text)
        elif mode == "add_file":
            return self._add_file_to_project(input_text)
        elif mode == "modify_file":
            return self._modify_file(input_text)
        elif mode == "execute_code":
            return self._execute_code(input_text)
        else:
            return self._create_single_file(input_text)
    
    async def _execute_async(self, input_text: str) -> str:
        """Execute agent logic asynchronously"""
        logger.info(f"[CodeAgent] Generating code asynchronously for: {input_text}")
        
        # Parse input to determine mode
        mode = self._detect_mode(input_text)
        
        # Since LLM generation might be slow, do it asynchronously
        loop = asyncio.get_event_loop()
        
        if mode == "new_project":
            return await loop.run_in_executor(None, self._create_new_project, input_text)
        elif mode == "add_file":
            return await loop.run_in_executor(None, self._add_file_to_project, input_text)
        elif mode == "modify_file":
            return await loop.run_in_executor(None, self._modify_file, input_text)
        elif mode == "execute_code":
            return await loop.run_in_executor(None, self._execute_code, input_text)
        else:
            return await loop.run_in_executor(None, self._create_single_file, input_text)
    
    def _detect_mode(self, input_text: str) -> str:
        """Detect the operation mode from input text"""
        input_lower = input_text.lower()
        
        if re.search(r'create\s+(?:a\s+)?(?:new\s+)?project', input_lower):
            return "new_project"
        elif re.search(r'add\s+(?:a\s+)?(?:new\s+)?file', input_lower):
            return "add_file"
        elif re.search(r'modify|change|update|edit', input_lower) and re.search(r'file', input_lower):
            return "modify_file"
        elif re.search(r'run|execute|test', input_lower) and re.search(r'code|script|program', input_lower):
            return "execute_code"
        else:
            return "single_file"
    
    def _create_new_project(self, input_text: str) -> str:
        """Create a new project with multiple files"""
        logger.info(f"[CodeAgent] Creating new project: {input_text}")
        
        # Extract project requirements
        prompt = f"""
        Create a multi-file project based on this description:
        "{input_text}"
        
        Provide your response in the following JSON format:
        
        {{
            "project_name": "name_of_project",
            "description": "brief description of the project",
            "language": "main programming language",
            "files": [
                {{
                    "path": "relative/path/to/file.ext",
                    "content": "full file content here",
                    "description": "what this file does"
                }},
                ...
            ],
            "setup_instructions": "how to set up and run the project"
        }}
        
        Make sure all the necessary files are included to make the project work.
        """
        
        # Generate project structure using LLM
        response = self.llm.generate(prompt)
        
        try:
            # Extract JSON from response (might be in a code block)
            json_match = re.search(r'```(?:json)?\s*([\s\S]+?)```', response)
            json_str = json_match.group(1) if json_match else response
            
            # Parse project structure
            project_data = json.loads(json_str)
            
            # Create project folder
            project_name = project_data.get("project_name", "untitled_project")
            safe_project_name = re.sub(r'\W+', '_', project_name.lower()).strip('_')
            timestamp = time.strftime("%Y%m%d_%H%M")
            base_dir = "generated"
            
            project_folder = os.path.join(base_dir, f"project_{timestamp}_{safe_project_name}")
            os.makedirs(project_folder, exist_ok=True)
            
            # Store project metadata
            project_info = {
                "name": project_name,
                "description": project_data.get("description", ""),
                "language": project_data.get("language", ""),
                "created_at": timestamp,
                "files": [],
                "setup_instructions": project_data.get("setup_instructions", "")
            }
            
            # Create each file in the project
            files_created = []
            for file_info in project_data.get("files", []):
                file_path = file_info.get("path", "")
                file_content = file_info.get("content", "")
                
                # Create full path
                full_path = os.path.join(project_folder, file_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file
                self.file_tool.execute(
                    action="write",
                    path=full_path,
                    content=file_content
                )
                
                files_created.append(file_path)
                project_info["files"].append({
                    "path": file_path,
                    "description": file_info.get("description", "")
                })
            
            # Save project info
            self.file_tool.execute(
                action="write",
                path=os.path.join(project_folder, "project_info.json"),
                content=json.dumps(project_info, indent=2)
            )
            
            # Save original prompt and raw LLM output
            self.file_tool.execute(
                action="write",
                path=os.path.join(project_folder, "prompt.txt"),
                content=input_text
            )
            
            self.file_tool.execute(
                action="write",
                path=os.path.join(project_folder, "output.md"),
                content=response
            )
            
            # Update agent memory with current project
            self.current_project = project_folder
            self.memory.store("current_project", project_folder)
            
            # Add project to memory's project history
            if not self.memory.has_key("project_history"):
                self.memory.store("project_history", [])
            
            project_history = self.memory.retrieve("project_history")
            project_history.append({
                "name": project_name,
                "path": project_folder,
                "created_at": timestamp
            })
            self.memory.store("project_history", project_history)
            
            # Log the event
            log_event("CodeAgent", f"Created project: {project_name}", f"Saved to {project_folder}")
            
            # Return success message with file list
            file_list = "\n".join([f"- {file}" for file in files_created])
            setup_instructions = project_data.get("setup_instructions", "")
            
            return f"""
Project '{project_name}' created successfully in {project_folder}

Files created:
{file_list}

Setup Instructions:
{setup_instructions}
"""
        
        except Exception as e:
            logger.error(f"[CodeAgent] Error creating project: {str(e)}")
            # Fallback to single file creation if project creation fails
            return self._create_single_file(input_text)
    
    def _create_single_file(self, input_text: str) -> str:
        """Create a single file (original behavior)"""
        logger.info(f"[CodeAgent] Creating single file for: {input_text}")
        
        # Step 1: Send prompt to model
        prompt = f"Write code to: {input_text}"
        full_response = self.llm.generate(prompt)
        
        # Step 2: Extract code block (clean version)
        code = self._extract_code_block(full_response)
        
        # Step 3: Detect file extension from task
        ext = self._detect_extension(input_text)
        
        # Step 4: Create folder for this task
        folder = self._create_task_folder(input_text)
        filename = f"{folder}/main{ext}"
        
        # Step 5: Save code to main file
        result = self.file_tool.execute(
            action="write",
            path=filename,
            content=code
        )
        
        # Step 6: Save prompt + raw output
        self.file_tool.execute(
            action="write",
            path=os.path.join(folder, "prompt.txt"),
            content=input_text
        )
        self.file_tool.execute(
            action="write",
            path=os.path.join(folder, "output.md"),
            content=full_response
        )
        
        # Update agent memory
        self.current_project = folder
        self.memory.store("current_project", folder)
        
        # Log event
        log_message = f"Saved to {filename}"
        logger.info(f"[CodeAgent] {log_message}")
        log_event("CodeAgent", input_text, log_message)
        
        return f"[CodeAgent] Generated code and saved to {filename}"
    
    def _add_file_to_project(self, input_text: str) -> str:
        """Add a new file to an existing project"""
        # Check if there's a current project
        current_project = self.memory.retrieve("current_project")
        
        if not current_project or not os.path.exists(current_project):
            return "No active project found. Please create a new project first."
        
        # Extract file details from input
        file_name_match = re.search(r'(?:called|named)\s+["\']?([^"\']+)["\']?', input_text)
        file_name = file_name_match.group(1) if file_name_match else "new_file"
        
        # Ensure file has extension
        if "." not in file_name:
            ext = self._detect_extension(input_text)
            file_name = f"{file_name}{ext}"
        
        # Generate file content
        prompt = f"""
        Create a new file called '{file_name}' for the project with the following requirements:
        "{input_text}"
        
        Only include the code with no explanations.
        """
        
        file_content = self.llm.generate(prompt)
        file_content = self._extract_code_block(file_content)
        
        # Create file path
        file_path = os.path.join(current_project, file_name)
        
        # Write file
        self.file_tool.execute(
            action="write",
            path=file_path,
            content=file_content
        )
        
        # Update project_info.json
        project_info_path = os.path.join(current_project, "project_info.json")
        if os.path.exists(project_info_path):
            try:
                project_info_content = self.file_tool.execute(
                    action="read",
                    path=project_info_path
                )
                project_info = json.loads(project_info_content)
                
                # Add file to project_info
                project_info["files"].append({
                    "path": file_name,
                    "description": f"Added based on: {input_text}"
                })
                
                # Update project_info file
                self.file_tool.execute(
                    action="write",
                    path=project_info_path,
                    content=json.dumps(project_info, indent=2)
                )
            except Exception as e:
                logger.error(f"[CodeAgent] Error updating project info: {str(e)}")
        
        # Log event
        log_message = f"Added file {file_name} to project {current_project}"
        logger.info(f"[CodeAgent] {log_message}")
        log_event("CodeAgent", input_text, log_message)
        
        return f"[CodeAgent] Added file {file_name} to project {os.path.basename(current_project)}"
    
    def _modify_file(self, input_text: str) -> str:
        """Modify an existing file in the current project"""
        # Check if there's a current project
        current_project = self.memory.retrieve("current_project")
        
        if not current_project or not os.path.exists(current_project):
            return "No active project found. Please create a new project first."
        
        # Extract file name from input
        file_name_match = re.search(r'(?:modify|change|update|edit)\s+["\']?([^"\']+)["\']?', input_text)
        file_name = file_name_match.group(1) if file_name_match else None
        
        if not file_name:
            return "Please specify which file to modify."
        
        # Find the file in the project
        file_path = os.path.join(current_project, file_name)
        if not os.path.exists(file_path):
            # Look for partial matches
            for root, dirs, files in os.walk(current_project):
                for f in files:
                    if file_name.lower() in f.lower():
                        file_path = os.path.join(root, f)
                        break
                if os.path.exists(file_path):
                    break
        
        if not os.path.exists(file_path):
            return f"File '{file_name}' not found in the current project."
        
        # Read the current file content
        current_content = self.file_tool.execute(
            action="read",
            path=file_path
        )
        
        # Generate modified file content
        prompt = f"""
        Modify the following file according to these requirements:
        "{input_text}"
        
        Current file content:
        ```
        {current_content}
        ```
        
        Provide only the updated code with no explanations.
        """
        
        modified_content = self.llm.generate(prompt)
        modified_content = self._extract_code_block(modified_content)
        
        # Write modified content back to file
        self.file_tool.execute(
            action="write",
            path=file_path,
            content=modified_content
        )
        
        # Log event
        relative_path = os.path.relpath(file_path, current_project)
        log_message = f"Modified file {relative_path} in project {os.path.basename(current_project)}"
        logger.info(f"[CodeAgent] {log_message}")
        log_event("CodeAgent", input_text, log_message)
        
        return f"[CodeAgent] Modified file {relative_path} in project {os.path.basename(current_project)}"
    
    def _execute_code(self, input_text: str) -> str:
        """Execute code in the current project"""
        # This would require CommandTool to be available
        # For now, we'll just return a message
        return "Code execution capability is not implemented yet. Will be added in a future update."
    
    # Helper methods (from original implementation)
    def _detect_extension(self, prompt):
        prompt = prompt.lower()
        if "python" in prompt or "py" in prompt:
            return ".py"
        elif "html" in prompt and "css" in prompt:
            return ".html"
        elif "html" in prompt:
            return ".html"
        elif "javascript" in prompt or "js" in prompt:
            return ".js"
        elif "bash" in prompt or "shell" in prompt:
            return ".sh"
        elif "json" in prompt:
            return ".json"
        elif "java" in prompt:
            return ".java"
        elif "c++" in prompt or "cpp" in prompt:
            return ".cpp"
        elif "c#" in prompt:
            return ".cs"
        elif "typescript" in prompt or "ts" in prompt:
            return ".ts"
        return ".txt"

    def _create_task_folder(self, task_prompt):
        base_dir = "generated"
        os.makedirs(base_dir, exist_ok=True)

        safe_name = re.sub(r'\W+', '_', task_prompt.lower()).strip('_')
        timestamp = time.strftime("%Y%m%d_%H%M")
        folder_name = os.path.join(base_dir, f"project_{timestamp}_{safe_name[:30]}")
        os.makedirs(folder_name, exist_ok=True)
        return folder_name

    def _extract_code_block(self, text):
        matches = re.findall(r"```(?:\w+)?\s*([\s\S]+?)```", text)
        return matches[0].strip() if matches else text.strip()
