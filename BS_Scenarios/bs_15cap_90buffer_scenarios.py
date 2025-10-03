import numpy as np
import pandas as pd
from scipy.stats import norm
from openpyxl import Workbook
import math

class BlackScholesPricer:
    def __init__(self):
        pass
    
    def calculate_d1_d2(self, S, K, T, r, sigma):
        """Calculate d1 and d2 for Black-Scholes formula"""
        if sigma <= 0 or T <= 0:
            return 0, 0
            
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2
    
    def call_price(self, S, K, T, r, sigma):
        """Calculate European call option price"""
        if T <= 0:
            return max(S - K, 0)
        if sigma <= 0:
            return max(S - K * np.exp(-r * T), 0)
        
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        call_prc = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return max(call_prc, 0)  # Ensure non-negative
    
    def put_price(self, S, K, T, r, sigma):
        """Calculate European put option price"""
        if T <= 0:
            return max(K - S, 0)
        if sigma <= 0:
            return max(K * np.exp(-r * T) - S, 0)
        
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        put_prc = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return max(put_prc, 0)  # Ensure non-negative
    
    def calculate_greeks(self, S, K, T, r, sigma, option_type='call'):
        """Calculate option Greeks"""
        if T <= 0 or sigma <= 0:
            # At expiration or zero vol
            if option_type == 'call':
                price = max(S - K, 0)
                delta = 1 if S > K else 0
            else:
                price = max(K - S, 0)
                delta = -1 if S < K else 0
            return {'delta': delta, 'gamma': 0, 'vega': 0, 'theta': 0, 'rho': 0, 'price': price}
        
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'call':
            delta = norm.cdf(d1)
            price = self.call_price(S, K, T, r, sigma)
        else:
            delta = norm.cdf(d1) - 1
            price = self.put_price(S, K, T, r, sigma)
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T)) if sigma > 0 else 0
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100 if sigma > 0 else 0  # per 1% change in vol
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == 'call' else -d2)) / 365
        rho = (K * T * np.exp(-r * T) * 
              norm.cdf(d2 if option_type == 'call' else -d2)) / 100  # per 1% change in rates
        
        return {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
            'rho': rho,
            'price': price
        }

class ScenarioAnalyzer:
    def __init__(self):
        self.bs = BlackScholesPricer()
        self.params = {}
        
    def load_parameters(self):
        """Load base parameters similar to Excel sheet"""
        self.params = {
            'S_0': 6638,      # Spot price
            'K_atm': 6638,    # ATM strike
            'r': 0.03,        # Risk-free rate
            'T': 1,           # Time to expiration (1 year)
            'atm_vol': 0.18,  # ATM volatility
            'vol_90': 0.22,   # 90% put volatility
            'vol_115': 0.14,  # 115% call volatility
            'cap_level': 0.15,  # 15% OTM cap
            'buffer': 0.10    # 10% buffer
        }
        
        # Calculate option strikes
        self.params['K_90_put'] = self.params['S_0'] * 0.90    # 90% put strike
        self.params['K_115_call'] = self.params['S_0'] * 1.15  # 115% call strike
        
    def create_scenario_grids(self):
        """Create scenario grids matching the updated template structure"""
        
        # Base values
        base_rate = self.params['r']
        
        # Rate scenarios: +/- 250 bps in 50 bps increments (13 scenarios total)
        # From -2.5% to +2.5% in 0.5% increments relative to base
        rate_scenarios = [base_rate + (i - 6) * 0.005 for i in range(13)]
        
        # ATM vol scenarios: 15% to 25% in 1% increments (11 scenarios total)
        atm_vol_scenarios = [0.15 + i * 0.01 for i in range(11)]
        
        # Skew scenarios: 0% to 20% in 2% increments (11 scenarios total) - matching template
        skew_scenarios = [i * 0.02 for i in range(11)]
        
        return {
            'rate_scenarios': rate_scenarios,
            'atm_vol_scenarios': atm_vol_scenarios,
            'skew_scenarios': skew_scenarios
        }
    
    def calculate_skew_volatilities(self, atm_vol, skew_level):
        """
        Calculate 90% put and 115% call volatilities given ATM vol and skew level
        Skew = 90% put vol - 115% call vol
        Keep ATM vol constant, adjust put and call vols to maintain skew
        """
        # Base skew from parameters
        base_skew = self.params['vol_90'] - self.params['vol_115']  # Should be 8%
        
        # For skew scenarios, we want to achieve the target skew level while keeping ATM vol constant
        # We'll adjust both put and call vols symmetrically around ATM vol
        vol_90 = atm_vol + (skew_level / 2)
        vol_115 = atm_vol - (skew_level / 2)
        
        # Ensure volatilities don't go negative
        vol_90 = max(vol_90, 0.01)
        vol_115 = max(vol_115, 0.01)
        
        return vol_90, vol_115
    
    def price_individual_options(self, S, r, T, atm_vol, vol_90, vol_115):
        """Price individual options in the package"""
        
        options = {
            'short_115_call': {
                'type': 'call',
                'strike': self.params['K_115_call'],
                'vol': vol_115,
                'position': -1
            },
            'long_atm_call': {
                'type': 'call', 
                'strike': self.params['K_atm'],
                'vol': atm_vol,
                'position': 1
            },
            'short_90_put': {
                'type': 'put',
                'strike': self.params['K_90_put'],
                'vol': vol_90,
                'position': -1
            }
        }
        
        results = {}
        for opt_name, opt_params in options.items():
            greeks = self.bs.calculate_greeks(
                S, opt_params['strike'], T, r, opt_params['vol'],
                opt_params['type']
            )
            # Apply position (long/short)
            for greek in ['delta', 'gamma', 'vega', 'theta', 'rho']:
                greeks[greek] *= opt_params['position']
            greeks['price'] *= opt_params['position']
            
            results[opt_name] = greeks
        
        return results
    
    def calculate_combined_package(self, individual_results):
        """Calculate combined package values"""
        combined = {
            'price': 0,
            'delta': 0,
            'gamma': 0, 
            'vega': 0,
            'theta': 0,
            'rho': 0
        }
        
        for opt_result in individual_results.values():
            for greek in combined.keys():
                combined[greek] += opt_result[greek]
        
        return combined
    
    def run_atm_vol_analysis(self):
        """ATM Vol vs Rates scenario analysis - PARALLEL MOVEMENT of all vols"""
        scenarios = self.create_scenario_grids()
        
        # Create matrix: 11 rows (ATM vol) x 13 columns (rates)
        results_matrix = np.zeros((11, 13))
        
        print("ATM Vol vs Rates Analysis (Parallel Movement):")
        
        # Calculate base skew levels for parallel shifts
        base_atm_vol = self.params['atm_vol']
        base_skew_90 = self.params['vol_90'] - base_atm_vol  # +4% for 90 put
        base_skew_115 = self.params['vol_115'] - base_atm_vol  # -4% for 115 call
        
        for i, atm_vol in enumerate(scenarios['atm_vol_scenarios']):
            for j, rate in enumerate(scenarios['rate_scenarios']):
                # PARALLEL MOVEMENT: Apply same shift to all volatilities
                # Maintain the same relative skew structure
                vol_shift = atm_vol - base_atm_vol
                
                vol_90 = self.params['vol_90'] + vol_shift
                vol_115 = self.params['vol_115'] + vol_shift
                
                # Ensure volatilities don't go negative
                vol_90 = max(vol_90, 0.01)
                vol_115 = max(vol_115, 0.01)
                
                individual = self.price_individual_options(
                    self.params['S_0'], rate, self.params['T'], 
                    atm_vol, vol_90, vol_115
                )
                combined = self.calculate_combined_package(individual)
                
                results_matrix[i, j] = combined['price']
                
                # Debug print for first row
                if i == 0 and j == 0:
                    print(f"  Sample calculation - ATM Vol: {atm_vol:.1%}, Rate: {rate:.1%}")
                    print(f"  Parallel vols - 90P: {vol_90:.1%}, ATM: {atm_vol:.1%}, 115C: {vol_115:.1%}")
                    print(f"  Vol shifts - 90P: {vol_shift:+.1%}, 115C: {vol_shift:+.1%}")
                    print(f"  Combined Price: {combined['price']:.4f}")
        
        print(f"  Matrix range: {results_matrix.min():.4f} to {results_matrix.max():.4f}")
        return results_matrix
    
    def run_skew_rates_analysis(self):
        """Skew vs Rates scenario analysis"""
        scenarios = self.create_scenario_grids()
        
        # Create matrix: 11 rows (skew) x 13 columns (rates)
        results_matrix = np.zeros((11, 13))
        
        print("Skew vs Rates Analysis:")
        for i, skew in enumerate(scenarios['skew_scenarios']):
            for j, rate in enumerate(scenarios['rate_scenarios']):
                # Calculate vols based on skew level (keep ATM vol constant at base)
                vol_90, vol_115 = self.calculate_skew_volatilities(
                    self.params['atm_vol'], skew
                )
                
                individual = self.price_individual_options(
                    self.params['S_0'], rate, self.params['T'],
                    self.params['atm_vol'], vol_90, vol_115
                )
                combined = self.calculate_combined_package(individual)
                
                results_matrix[i, j] = combined['price']
                
                # Debug print for first row
                if i == 0 and j == 0:
                    print(f"  Sample calculation - Skew: {skew:.1%}, Rate: {rate:.1%}")
                    print(f"  Vols - 90P: {vol_90:.1%}, 115C: {vol_115:.1%}")
                    print(f"  Combined Price: {combined['price']:.4f}")
        
        print(f"  Matrix range: {results_matrix.min():.4f} to {results_matrix.max():.4f}")
        return results_matrix
    
    def run_skew_atm_vol_analysis(self):
        """Skew vs ATM Vol scenario analysis"""
        scenarios = self.create_scenario_grids()
        
        # Create matrix: 11 rows (skew) x 11 columns (ATM vol)
        results_matrix = np.zeros((11, 11))
        
        print("Skew vs ATM Vol Analysis:")
        for i, skew in enumerate(scenarios['skew_scenarios']):
            for j, atm_vol in enumerate(scenarios['atm_vol_scenarios']):
                # Calculate vols based on both skew level and current ATM vol
                vol_90, vol_115 = self.calculate_skew_volatilities(atm_vol, skew)
                
                individual = self.price_individual_options(
                    self.params['S_0'], self.params['r'], self.params['T'],
                    atm_vol, vol_90, vol_115
                )
                combined = self.calculate_combined_package(individual)
                
                results_matrix[i, j] = combined['price']
                
                # Debug print for first row
                if i == 0 and j == 0:
                    print(f"  Sample calculation - Skew: {skew:.1%}, ATM Vol: {atm_vol:.1%}")
                    print(f"  Vols - 90P: {vol_90:.1%}, 115C: {vol_115:.1%}")
                    print(f"  Combined Price: {combined['price']:.4f}")
        
        print(f"  Matrix range: {results_matrix.min():.4f} to {results_matrix.max():.4f}")
        return results_matrix
    
    def create_excel_output(self):
        """Create Excel output matching the template exactly"""
        self.load_parameters()
        
        # Run all analyses
        print("Running scenario analyses...")
        atm_vol_matrix = self.run_atm_vol_analysis()
        skew_rates_matrix = self.run_skew_rates_analysis()
        skew_atm_vol_matrix = self.run_skew_atm_vol_analysis()
        
        # Create Excel workbook
        wb = Workbook()
        
        # Remove default sheet
        wb.remove(wb.active)
        
        # Add Params sheet
        ws_params = wb.create_sheet("Params")
        params_data = [
            ["BS Inputs", "", "", "15% CAP, 10% buffer strategy, hedging only the one year payout"],
            ["S_0", self.params['S_0'], "", "Skew is defined as the 90% put - 115% call, when skew steepens, keep the ATM vol the same"],
            ["K", self.params['K_atm'], "", "Scenarios defined as rates +/- 250 bps, in 50 bps increments"],
            ["r", self.params['r'], "", "Skew going from 5% to 15% in 1% increment"],
            ["Time", self.params['T'], "", "ATM vol ranging from 15% to 25% in 1% increments"],
            ["ATM vol", self.params['atm_vol'], "", ""],
            ["90% vol", self.params['vol_90'], "", ""],
            ["115% vol", self.params['vol_115'], "", ""]
        ]
        for row in params_data:
            ws_params.append(row)
        
        # Add analysis sheets
        self._create_atm_vol_rates_sheet(wb, atm_vol_matrix)
        self._create_skew_rates_sheet(wb, skew_rates_matrix)
        self._create_skew_atm_vol_sheet(wb, skew_atm_vol_matrix)
        
        # Save the workbook
        wb.save("scenario_analysis_output.xlsx")
        print("\nExcel file created: scenario_analysis_output.xlsx")
        
        return {
            'atm_vol_matrix': atm_vol_matrix,
            'skew_rates_matrix': skew_rates_matrix,
            'skew_atm_vol_matrix': skew_atm_vol_matrix
        }
    
    def _create_atm_vol_rates_sheet(self, wb, matrix):
        """Create ATM_Vol_Rates sheet matching template exactly"""
        ws = wb.create_sheet("ATM_Vol_Rates")
        
        # Header row - rates from -2.5% to +2.5% in 0.5% increments
        headers = [""]
        base_rate = self.params['r']
        
        for i in range(13):
            rate = base_rate + (i - 6) * 0.005
            headers.append(rate)
        
        ws.append(headers)
        
        # Data rows - ATM vol from 15% to 25% in 1% increments
        for i in range(11):
            row_data = []
            atm_vol = 0.15 + i * 0.01
            
            # Add row header (formula representation)
            if i == 0:
                row_header = "=A3-1%"
            elif i == 5:  # Middle row - base ATM vol
                row_header = "=Params!B6"
            elif i == 10:
                row_header = "=A11+1%"
            else:
                row_header = atm_vol  # Show actual value for clarity
                
            row_data.append(row_header)
            
            # Add matrix data
            for j in range(13):
                row_data.append(matrix[i, j])
            
            ws.append(row_data)
    
    def _create_skew_rates_sheet(self, wb, matrix):
        """Create Skew_Rates sheet matching template exactly"""
        ws = wb.create_sheet("Skew_Rates")
        
        # Header row - same rates as ATM_Vol_Rates
        headers = [""]
        base_rate = self.params['r']
        
        for i in range(13):
            rate = base_rate + (i - 6) * 0.005
            headers.append(rate)
        
        ws.append(headers)
        
        # Data rows - skew from 0% to 20% in 2% increments (matching template)
        for i in range(11):
            row_data = []
            skew_level = i * 0.02
            
            # Add row header (formula representation)
            if i == 0:
                row_header = "0"
            else:
                row_header = f"=A{i+1}+2%"  # A2+2%, A3+2%, etc.
                
            row_data.append(row_header)
            
            # Add matrix data
            for j in range(13):
                row_data.append(matrix[i, j])
            
            ws.append(row_data)
    
    def _create_skew_atm_vol_sheet(self, wb, matrix):
        """Create Skew_ATM_Vol sheet matching template exactly"""
        ws = wb.create_sheet("Skew_ATM_Vol")
        
        # Header row - ATM vol from 15% to 25% in 1% increments
        headers = [""]
        for i in range(11):
            atm_vol = 0.15 + i * 0.01
            headers.append(atm_vol)
        
        ws.append(headers)
        
        # Data rows - skew from 0% to 20% in 2% increments
        for i in range(11):
            row_data = []
            skew_level = i * 0.02
            
            # Add row header (formula representation)
            if i == 0:
                row_header = "0"
            else:
                row_header = f"=A{i+1}+2%"  # A2+2%, A3+2%, etc.
                
            row_data.append(row_header)
            
            # Add matrix data
            for j in range(11):
                row_data.append(matrix[i, j])
            
            ws.append(row_data)

# Run the analysis
if __name__ == "__main__":
    analyzer = ScenarioAnalyzer()
    analyzer.load_parameters()
    
    print("DEBUG: Parameter Check")
    print(f"Spot: {analyzer.params['S_0']}")
    print(f"Strikes - 90P: {analyzer.params['K_90_put']}, ATM: {analyzer.params['K_atm']}, 115C: {analyzer.params['K_115_call']}")
    print(f"Base Vols - ATM: {analyzer.params['atm_vol']:.1%}, 90P: {analyzer.params['vol_90']:.1%}, 115C: {analyzer.params['vol_115']:.1%}")
    print(f"Base Skew: {analyzer.params['vol_90'] - analyzer.params['vol_115']:.1%}")
    
    # Test a single option pricing
    print("\nDEBUG: Single Option Pricing Test")
    bs = BlackScholesPricer()
    call_price = bs.call_price(6638, 6638, 1, 0.03, 0.18)
    put_price = bs.put_price(6638, 6638*0.9, 1, 0.03, 0.22)
    print(f"ATM Call Price: {call_price:.4f}")
    print(f"90 Put Price: {put_price:.4f}")
    
    # Run full analysis
    results = analyzer.create_excel_output()