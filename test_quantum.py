#!/usr/bin/env python3
"""
Unit Tests for Quantum Replication Module
"""

import unittest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_replication import QuantumReplicator
from database_handler import DatabaseHandler


class TestQuantumReplicator(unittest.TestCase):
    """Test cases for quantum replication"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_handler = DatabaseHandler(':memory:')
        self.replicator = QuantumReplicator(self.db_handler)
    
    def test_quantum_id_generation(self):
        """Test quantum ID generation"""
        clone_id = self.replicator._generate_quantum_id('192.168.1.100', 'PARENT-001')
        
        self.assertIsNotNone(clone_id)
        self.assertTrue(clone_id.startswith('QC-'))
        self.assertEqual(len(clone_id), 19)  # QC- + 16 char hash
    
    def test_quantum_signature(self):
        """Test quantum signature generation"""
        signature = self.replicator._generate_quantum_signature('TEST-CLONE-001')
        
        self.assertIsNotNone(signature)
        self.assertEqual(len(signature), 128)  # SHA-512 hex digest
    
    def test_replication_package_creation(self):
        """Test replication package creation"""
        async def run_test():
            package = await self.replicator._create_replication_package(
                'CLONE-001',
                'PARENT-001'
            )
            
            self.assertIn('clone_id', package)
            self.assertIn('parent_id', package)
            self.assertIn('version', package)
            self.assertIn('source_files', package)
            self.assertIn('config', package)
            self.assertIn('quantum_signature', package)
            
            self.assertEqual(package['clone_id'], 'CLONE-001')
            self.assertEqual(package['parent_id'], 'PARENT-001')
        
        asyncio.run(run_test())
    
    def test_quantum_entanglement(self):
        """Test quantum entanglement establishment"""
        async def run_test():
            key = await self.replicator._establish_quantum_entanglement(
                'CLONE-001',
                'PARENT-001'
            )
            
            self.assertIsNotNone(key)
            self.assertEqual(len(key), 64)  # SHA-256 hex digest
        
        asyncio.run(run_test())
    
    def test_quantum_state_capture(self):
        """Test quantum state capture"""
        state = self.replicator._capture_quantum_state('CLONE-001')
        
        self.assertIn('coherence', state)
        self.assertIn('entanglement_strength', state)
        self.assertIn('superposition_active', state)
        self.assertIn('measurement_timestamp', state)
        
        self.assertGreaterEqual(state['coherence'], 0)
        self.assertLessEqual(state['coherence'], 1)
    
    def test_clone_status_check(self):
        """Test clone status checking"""
        async def run_test():
            # Create entanglement pair first
            self.replicator.entanglement_pairs['CLONE-001'] = {
                'parent': 'PARENT-001',
                'key': 'test-key'
            }
            self.replicator._capture_quantum_state('CLONE-001')
            
            status = await self.replicator.check_clone_status('CLONE-001')
            
            self.assertTrue(status['healthy'])
            self.assertEqual(status['clone_id'], 'CLONE-001')
        
        asyncio.run(run_test())
    
    def test_clone_repair(self):
        """Test clone repair functionality"""
        async def run_test():
            # Setup entanglement
            self.replicator.entanglement_pairs['CLONE-001'] = {
                'parent': 'PARENT-001',
                'key': 'old-key'
            }
            
            result = await self.replicator.repair_clone('CLONE-001')
            
            self.assertTrue(result)
            self.assertIn('CLONE-001', self.replicator.entanglement_pairs)
            self.assertNotEqual(
                self.replicator.entanglement_pairs['CLONE-001']['key'],
                'old-key'
            )
        
        asyncio.run(run_test())
    
    def test_clone_termination(self):
        """Test clone termination"""
        async def run_test():
            await self.db_handler.connect()
            
            # Setup clone
            await self.db_handler.register_clone('CLONE-001')
            self.replicator.entanglement_pairs['CLONE-001'] = {
                'parent': 'PARENT-001',
                'key': 'test-key'
            }
            self.replicator._capture_quantum_state('CLONE-001')
            
            # Terminate
            result = await self.replicator.terminate_clone('CLONE-001')
            
            self.assertTrue(result)
            self.assertNotIn('CLONE-001', self.replicator.entanglement_pairs)
            self.assertNotIn('CLONE-001', self.replicator.quantum_state)
            
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
