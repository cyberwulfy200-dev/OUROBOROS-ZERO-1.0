#!/usr/bin/env python3
"""
Unit Tests for Autonomous Replicator 7G
"""

import unittest
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ouroboros_zero import OuroborosZero
from ai_decision_engine import AIDecisionEngine
from database_handler import DatabaseHandler


class TestOuroborosZero(unittest.TestCase):
    """Test cases for OUROBOROS-ZERO main engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ouroboros = OuroborosZero('config/config.yaml')
    
    def test_clone_id_generation(self):
        """Test clone ID generation"""
        clone_id = self.ouroboros._generate_clone_id()
        self.assertIsNotNone(clone_id)
        self.assertTrue(clone_id.startswith('OUROBOROS-'))
    
    def test_initialization(self):
        """Test OUROBOROS initialization"""
        async def run_test():
            result = await self.ouroboros.initialize()
            self.assertTrue(result)
        
        asyncio.run(run_test())
    
    def test_scan_network(self):
        """Test network scanning"""
        async def run_test():
            targets = await self.ouroboros.scan_network()
            self.assertIsInstance(targets, list)
        
        asyncio.run(run_test())


class TestAIDecisionEngine(unittest.TestCase):
    """Test cases for AI decision engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_handler = DatabaseHandler(':memory:')
        self.ai_engine = AIDecisionEngine(self.db_handler)
    
    def test_extract_features(self):
        """Test feature extraction"""
        target_info = {
            'ip_address': '192.168.1.100',
            'os_fingerprint': {'os': 'Linux'},
            'open_ports': [{'port': 22}, {'port': 80}],
            'vulnerabilities': [{'cve': 'CVE-2024-0001'}],
            'security_posture': {
                'firewall_detected': True,
                'ids_ips_active': False,
                'patch_level': 'current',
                'hardening_score': 0.7
            },
            'services': [],
            'network_topology': {'neighbors': 10}
        }
        
        features = self.ai_engine._extract_features(target_info)
        self.assertIsInstance(features, dict)
        self.assertEqual(features['os_type'], 'Linux')
        self.assertEqual(features['num_open_ports'], 2)
    
    def test_risk_assessment(self):
        """Test risk assessment"""
        target_info = {
            'ip_address': '192.168.1.100',
            'os_fingerprint': {'os': 'Linux'},
            'open_ports': [],
            'vulnerabilities': [],
            'security_posture': {
                'firewall_detected': True,
                'ids_ips_active': True,
                'patch_level': 'current',
                'hardening_score': 0.9
            },
            'services': [],
            'network_topology': {}
        }
        
        risk = self.ai_engine._assess_security_risk(target_info)
        self.assertGreater(risk, 0.5)  # High security should mean high risk
    
    def test_target_selection(self):
        """Test target selection"""
        async def run_test():
            await self.db_handler.connect()
            await self.ai_engine.initialize()
            
            targets = ['192.168.1.1', '192.168.1.2', '192.168.1.3']
            selected = await self.ai_engine.select_targets(targets)
            
            self.assertIsInstance(selected, list)
            self.assertLessEqual(len(selected), len(targets))
            
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())


class TestDatabaseHandler(unittest.TestCase):
    """Test cases for database handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db_handler = DatabaseHandler(':memory:')
    
    def test_connection(self):
        """Test database connection"""
        async def run_test():
            await self.db_handler.connect()
            self.assertIsNotNone(self.db_handler.connection)
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())
    
    def test_register_clone(self):
        """Test clone registration"""
        async def run_test():
            await self.db_handler.connect()
            
            result = await self.db_handler.register_clone(
                'TEST-001',
                parent_id=None,
                target_ip='192.168.1.100'
            )
            
            self.assertTrue(result)
            
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())
    
    def test_clone_generation(self):
        """Test clone generation tracking"""
        async def run_test():
            await self.db_handler.connect()
            
            # Register parent
            await self.db_handler.register_clone('PARENT-001')
            
            # Register child
            await self.db_handler.register_clone(
                'CHILD-001',
                parent_id='PARENT-001'
            )
            
            # Check generation
            gen = await self.db_handler.get_clone_generation('CHILD-001')
            self.assertEqual(gen, 2)
            
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())
    
    def test_statistics(self):
        """Test statistics retrieval"""
        async def run_test():
            await self.db_handler.connect()
            
            # Add some data
            await self.db_handler.register_clone('CLONE-001')
            await self.db_handler.register_clone('CLONE-002')
            
            stats = await self.db_handler.get_clone_statistics()
            
            self.assertIn('total_clones', stats)
            self.assertIn('active_clones', stats)
            self.assertGreaterEqual(stats['total_clones'], 2)
            
            await self.db_handler.disconnect()
        
        asyncio.run(run_test())


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestOuroborosZero))
    suite.addTests(loader.loadTestsFromTestCase(TestAIDecisionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseHandler))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
