from trading.optimizer import StrategyOptimizer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    optimizer = StrategyOptimizer()
    
    logger.info("Starting strategy optimization process...")
    best_params, best_metrics = optimizer.optimize()
    
    if best_params and best_metrics:
        # Save results
        results = {
            'parameters': best_params,
            'metrics': best_metrics
        }
        
        with open('optimal_parameters.json', 'w') as f:
            json.dump(results, f, indent=4)
            
        logger.info("Optimization completed successfully")
        logger.info(f"Best parameters: {best_params}")
        logger.info(f"Performance metrics: {best_metrics}")
    else:
        logger.error("Optimization failed")

if __name__ == "__main__":
    main()
