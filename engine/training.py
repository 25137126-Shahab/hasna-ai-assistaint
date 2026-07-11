import sqlite3
import json
from datetime import datetime
import eel

# Database connection
conn = sqlite3.connect("hansa.db")
cursor = conn.cursor()

def init_training_db():
    """Initialize training database tables"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_keyword TEXT UNIQUE NOT NULL,
            command_description TEXT,
            action_type TEXT,
            action_value TEXT,
            response TEXT,
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enabled BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            command_matched TEXT,
            action_performed TEXT,
            success BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()

def add_custom_command(keyword, description, action_type, action_value, response, language='en'):
    """
    Add a new custom command for training
    
    action_type can be: 'open_app', 'open_url', 'speak', 'execute_command', 'search_youtube'
    """
    try:
        cursor.execute('''
            INSERT INTO custom_commands 
            (command_keyword, command_description, action_type, action_value, response, language)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (keyword.lower(), description, action_type, action_value, response, language))
        
        conn.commit()
        return {"status": "success", "message": f"Command '{keyword}' added successfully"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": f"Command '{keyword}' already exists"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_custom_commands():
    """Get all custom commands"""
    cursor.execute('SELECT * FROM custom_commands WHERE enabled = 1')
    commands = cursor.fetchall()
    return commands

def execute_custom_command(keyword, user_input):
    """Execute a custom command based on keyword"""
    try:
        cursor.execute('''
            SELECT action_type, action_value, response 
            FROM custom_commands 
            WHERE LOWER(command_keyword) = LOWER(?)
            AND enabled = 1
        ''', (keyword,))
        
        result = cursor.fetchone()
        
        if result:
            action_type, action_value, response = result
            
            # Log the training
            cursor.execute('''
                INSERT INTO training_logs 
                (user_input, command_matched, action_performed, success)
                VALUES (?, ?, ?, ?)
            ''', (user_input, keyword, action_type, True))
            conn.commit()
            
            return {
                "status": "success",
                "action_type": action_type,
                "action_value": action_value,
                "response": response
            }
        else:
            return {"status": "not_found", "message": f"Command '{keyword}' not found"}
    
    except Exception as e:
        cursor.execute('''
            INSERT INTO training_logs 
            (user_input, command_matched, action_performed, success)
            VALUES (?, ?, ?, ?)
        ''', (user_input, keyword, str(e), False))
        conn.commit()
        
        return {"status": "error", "message": str(e)}

def update_custom_command(command_id, **kwargs):
    """Update a custom command"""
    allowed_fields = ['command_keyword', 'command_description', 'action_type', 'action_value', 'response', 'enabled']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return {"status": "error", "message": "No valid fields to update"}
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [command_id]
    
    try:
        cursor.execute(f"UPDATE custom_commands SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return {"status": "success", "message": "Command updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_custom_command(command_id):
    """Delete a custom command (soft delete)"""
    try:
        cursor.execute("UPDATE custom_commands SET enabled = 0 WHERE id = ?", (command_id,))
        conn.commit()
        return {"status": "success", "message": "Command deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_training_stats():
    """Get training statistics"""
    cursor.execute('''
        SELECT 
            COUNT(*) as total_commands,
            SUM(CASE WHEN enabled = 1 THEN 1 ELSE 0 END) as active_commands,
            (SELECT COUNT(*) FROM training_logs WHERE success = 1) as successful_executions,
            (SELECT COUNT(*) FROM training_logs WHERE success = 0) as failed_executions
        FROM custom_commands
    ''')
    
    stats = cursor.fetchone()
    return {
        "total_commands": stats[0] or 0,
        "active_commands": stats[1] or 0,
        "successful_executions": stats[2] or 0,
        "failed_executions": stats[3] or 0
    }

@eel.expose
def export_training_data():
    """Export all training data as JSON"""
    try:
        cursor.execute('SELECT * FROM custom_commands WHERE enabled = 1')
        commands = cursor.fetchall()
        
        commands_data = []
        for cmd in commands:
            commands_data.append({
                "id": cmd[0],
                "keyword": cmd[1],
                "description": cmd[2],
                "action_type": cmd[3],
                "action_value": cmd[4],
                "response": cmd[5],
                "language": cmd[6]
            })
        
        return {
            "status": "success",
            "data": commands_data,
            "total": len(commands_data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Initialize on import
init_training_db()
