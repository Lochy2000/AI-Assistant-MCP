import os
import shutil
import glob
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
import time
from datetime import datetime

from tools.base import Tool, ToolMetadata
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.tools.file')

class FileTool(Tool):
    """
    Enhanced File Tool with improved capabilities
    
    - Asynchronous file operations
    - Directory operations (create, delete, list)
    - File search capabilities
    - File metadata and stats
    - File monitoring
    """
    
    def __init__(self):
        super().__init__()
    
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata"""
        return ToolMetadata(
            name="file",
            description="File and directory operations",
            version="1.0.0",
            parameters={
                "action": {
                    "type": "string",
                    "description": "Action to perform (read, write, append, delete, list, create_dir, etc.)",
                    "required": True
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path",
                    "required": True
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to file (required for write/append)",
                    "required": False
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to perform operation recursively",
                    "required": False
                },
                "pattern": {
                    "type": "string",
                    "description": "Search pattern for file operations",
                    "required": False
                }
            },
            required_permissions=["file_access"],
            supports_progress=True,
            tags=["io", "filesystem"]
        )
    
    def _execute(self, **kwargs) -> Any:
        """Execute file operations based on action parameter"""
        action = kwargs.get("action")
        path = kwargs.get("path")
        
        if not action or not path:
            return "[FileTool] Error: Both 'action' and 'path' parameters are required"
        
        try:
            # Route to appropriate handler based on action
            if action == "read":
                return self._read_file(path)
            
            elif action == "write":
                content = kwargs.get("content", "")
                return self._write_file(path, content)
            
            elif action == "append":
                content = kwargs.get("content", "")
                return self._append_file(path, content)
            
            elif action == "delete":
                recursive = kwargs.get("recursive", False)
                return self._delete_file_or_dir(path, recursive)
            
            elif action == "list":
                return self._list_directory(path)
            
            elif action == "create_dir":
                return self._create_directory(path)
            
            elif action == "copy":
                destination = kwargs.get("destination")
                if not destination:
                    return "[FileTool] Error: 'destination' parameter is required for copy action"
                return self._copy_file_or_dir(path, destination)
            
            elif action == "move":
                destination = kwargs.get("destination")
                if not destination:
                    return "[FileTool] Error: 'destination' parameter is required for move action"
                return self._move_file_or_dir(path, destination)
            
            elif action == "search":
                pattern = kwargs.get("pattern", "*")
                return self._search_files(path, pattern)
            
            elif action == "info":
                return self._get_file_info(path)
            
            else:
                return f"[FileTool] Error: Unknown action '{action}'"
        
        except Exception as e:
            logger.error(f"[FileTool] Error performing {action} on {path}: {str(e)}")
            log_event("FileTool", f"{action} {path}", f"Error: {str(e)}")
            return f"[FileTool] Error: {str(e)}"
    
    async def _execute_async(self, **kwargs) -> Any:
        """Execute file operations asynchronously"""
        action = kwargs.get("action")
        path = kwargs.get("path")
        
        if not action or not path:
            return "[FileTool] Error: Both 'action' and 'path' parameters are required"
        
        try:
            # Create loop for running file operations in thread
            loop = asyncio.get_event_loop()
            
            # Route to appropriate handler based on action
            if action == "read":
                return await loop.run_in_executor(None, lambda: self._read_file(path))
            
            elif action == "write":
                content = kwargs.get("content", "")
                return await loop.run_in_executor(None, lambda: self._write_file(path, content))
            
            elif action == "append":
                content = kwargs.get("content", "")
                return await loop.run_in_executor(None, lambda: self._append_file(path, content))
            
            elif action == "delete":
                recursive = kwargs.get("recursive", False)
                return await loop.run_in_executor(None, lambda: self._delete_file_or_dir(path, recursive))
            
            elif action == "list":
                return await loop.run_in_executor(None, lambda: self._list_directory(path))
            
            elif action == "create_dir":
                return await loop.run_in_executor(None, lambda: self._create_directory(path))
            
            elif action == "copy":
                destination = kwargs.get("destination")
                if not destination:
                    return "[FileTool] Error: 'destination' parameter is required for copy action"
                return await loop.run_in_executor(None, lambda: self._copy_file_or_dir(path, destination))
            
            elif action == "move":
                destination = kwargs.get("destination")
                if not destination:
                    return "[FileTool] Error: 'destination' parameter is required for move action"
                return await loop.run_in_executor(None, lambda: self._move_file_or_dir(path, destination))
            
            elif action == "search":
                pattern = kwargs.get("pattern", "*")
                return await loop.run_in_executor(None, lambda: self._search_files(path, pattern))
            
            elif action == "info":
                return await loop.run_in_executor(None, lambda: self._get_file_info(path))
            
            else:
                return f"[FileTool] Error: Unknown action '{action}'"
        
        except Exception as e:
            logger.error(f"[FileTool] Error performing {action} on {path}: {str(e)}")
            log_event("FileTool", f"{action} {path}", f"Error: {str(e)}")
            return f"[FileTool] Error: {str(e)}"
    
    # Implementation of file operations
    def _read_file(self, path: str) -> str:
        """Read content from a file"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                result = f.read()
            logger.info(f"[FileTool] Read from {path}")
            log_event("FileTool", f"read {path}", "Success")
            return result
        except UnicodeDecodeError:
            # Try binary mode if text mode fails
            with open(path, "rb") as f:
                result = f.read()
            logger.info(f"[FileTool] Read binary data from {path}")
            log_event("FileTool", f"read {path}", "Binary data")
            return f"[Binary data of size {len(result)} bytes]"
    
    def _write_file(self, path: str, content: str) -> str:
        """Write content to a file, creating directories if needed"""
        # Ensure directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"[FileTool] Wrote to {path}")
        log_event("FileTool", f"write {path}", "Success")
        return f"[FileTool] Successfully wrote to {path}"
    
    def _append_file(self, path: str, content: str) -> str:
        """Append content to a file, creating it if needed"""
        # Ensure directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"[FileTool] Appended to {path}")
        log_event("FileTool", f"append {path}", "Success")
        return f"[FileTool] Successfully appended to {path}"
    
    def _delete_file_or_dir(self, path: str, recursive: bool = False) -> str:
        """Delete a file or directory"""
        if os.path.isfile(path):
            os.remove(path)
            logger.info(f"[FileTool] Deleted file {path}")
            log_event("FileTool", f"delete {path}", "Success")
            return f"[FileTool] Successfully deleted file {path}"
        elif os.path.isdir(path):
            if recursive:
                shutil.rmtree(path)
                logger.info(f"[FileTool] Deleted directory {path} recursively")
                log_event("FileTool", f"delete {path} (recursive)", "Success")
                return f"[FileTool] Successfully deleted directory {path} and all its contents"
            else:
                os.rmdir(path)
                logger.info(f"[FileTool] Deleted empty directory {path}")
                log_event("FileTool", f"delete {path}", "Success")
                return f"[FileTool] Successfully deleted directory {path}"
        else:
            return f"[FileTool] Error: {path} does not exist"
    
    def _list_directory(self, path: str) -> str:
        """List contents of a directory"""
        if not os.path.isdir(path):
            return f"[FileTool] Error: {path} is not a directory"
        
        items = os.listdir(path)
        files = []
        directories = []
        
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directories.append(f"[DIR] {item}")
            else:
                files.append(f"[FILE] {item}")
        
        # Sort directories and files separately
        directories.sort()
        files.sort()
        
        result = "\n".join(directories + files)
        logger.info(f"[FileTool] Listed directory {path}")
        log_event("FileTool", f"list {path}", "Success")
        return f"Directory content of {path}:\n{result}"
    
    def _create_directory(self, path: str) -> str:
        """Create a directory and any necessary parent directories"""
        os.makedirs(path, exist_ok=True)
        logger.info(f"[FileTool] Created directory {path}")
        log_event("FileTool", f"create_dir {path}", "Success")
        return f"[FileTool] Successfully created directory {path}"
    
    def _copy_file_or_dir(self, source: str, destination: str) -> str:
        """Copy a file or directory"""
        if os.path.isfile(source):
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(source, destination)
            logger.info(f"[FileTool] Copied file {source} to {destination}")
            log_event("FileTool", f"copy {source} to {destination}", "Success")
            return f"[FileTool] Successfully copied file {source} to {destination}"
        elif os.path.isdir(source):
            shutil.copytree(source, destination)
            logger.info(f"[FileTool] Copied directory {source} to {destination}")
            log_event("FileTool", f"copy {source} to {destination}", "Success")
            return f"[FileTool] Successfully copied directory {source} to {destination}"
        else:
            return f"[FileTool] Error: {source} does not exist"
    
    def _move_file_or_dir(self, source: str, destination: str) -> str:
        """Move a file or directory"""
        if not os.path.exists(source):
            return f"[FileTool] Error: {source} does not exist"
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        shutil.move(source, destination)
        logger.info(f"[FileTool] Moved {source} to {destination}")
        log_event("FileTool", f"move {source} to {destination}", "Success")
        return f"[FileTool] Successfully moved {source} to {destination}"
    
    def _search_files(self, path: str, pattern: str) -> str:
        """Search for files matching a pattern in a directory"""
        if not os.path.isdir(path):
            return f"[FileTool] Error: {path} is not a directory"
        
        search_path = os.path.join(path, "**", pattern)
        matches = glob.glob(search_path, recursive=True)
        
        if not matches:
            return f"[FileTool] No files matching '{pattern}' found in {path}"
        
        # Format results
        result = "\n".join([f"- {os.path.relpath(match, path)}" for match in matches])
        logger.info(f"[FileTool] Search in {path} for {pattern} found {len(matches)} matches")
        log_event("FileTool", f"search {path} {pattern}", f"Found {len(matches)} matches")
        return f"Found {len(matches)} files matching '{pattern}' in {path}:\n{result}"
    
    def _get_file_info(self, path: str) -> str:
        """Get detailed information about a file or directory"""
        if not os.path.exists(path):
            return f"[FileTool] Error: {path} does not exist"
        
        stats = os.stat(path)
        is_dir = os.path.isdir(path)
        
        # Format timestamps
        created_time = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed_time = datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate human-readable size
        size_bytes = stats.st_size
        size_readable = self._format_size(size_bytes)
        
        info = {
            "path": path,
            "type": "Directory" if is_dir else "File",
            "size": size_readable,
            "size_bytes": size_bytes,
            "created": created_time,
            "last_modified": modified_time,
            "last_accessed": accessed_time,
            "permissions": oct(stats.st_mode)[-3:],  # Unix-style permissions
        }
        
        # Add directory-specific info
        if is_dir:
            items = os.listdir(path)
            info["items_count"] = len(items)
            info["files_count"] = sum(1 for item in items if os.path.isfile(os.path.join(path, item)))
            info["dirs_count"] = sum(1 for item in items if os.path.isdir(os.path.join(path, item)))
        
        # Format as string
        result = [f"Information for: {path}"]
        result.append(f"Type: {info['type']}")
        result.append(f"Size: {info['size']} ({info['size_bytes']} bytes)")
        result.append(f"Created: {info['created']}")
        result.append(f"Last Modified: {info['last_modified']}")
        result.append(f"Last Accessed: {info['last_accessed']}")
        result.append(f"Permissions: {info['permissions']}")
        
        if is_dir:
            result.append(f"Contents: {info['items_count']} items ({info['files_count']} files, {info['dirs_count']} directories)")
        
        logger.info(f"[FileTool] Got info for {path}")
        log_event("FileTool", f"info {path}", "Success")
        return "\n".join(result)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}" if unit != 'B' else f"{size_bytes} {unit}"
            size_bytes /= 1024
