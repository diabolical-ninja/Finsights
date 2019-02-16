"""
Title: Growth Calcualtor
Description: 
"""

from tax_calculator import tax


class GrowthCalculator:
    """
    Simulates total returns, less tax, given a few basic parameters    
    """

    def __init__(self, salary, starting_investment, capital_growth, dividend_payout, years):
        self.salary = salary
        self.starting_investment = starting_investment
        self.current_investment = starting_investment
        self.cg = capital_growth
        self.dp = dividend_payout
        self.years = years


    def eoy_stats(self, year, salary, dividend_income, excess_tax, capital):
        """Object to capture results as generated
        
        Args:
            year (int): Year ID
            salary (float): Salary for that year
            dividend_income (float): Dividend income generated that year
            excess_tax (float): Extra tax paid that year due to additional income
            capital (float): Gross investment position
        
        Returns:
            dict: Object containing summary stats
        """

        return {
            'year': year,
            'salary': salary,
            'dividend_income': dividend_income,
            'excess_tax': excess_tax,
            'capital': capital
        }


    def compound_interest(self, principal, interest_rate, compounds_per_year, years):
        """Compound Interest Calculator
        
        Args:
            principal (float): Initial principal 
            interest_rate (float): Interest Rate % as a decimal
            compounds_per_year (int): Number of compound events per year
            years (float): Number of years to compount over
        
        Returns:
            float: Final return
        """

        return principal * (1 + interest_rate/compounds_per_year) ** (compounds_per_year * years)


    def taxable_capital_gains(self, initial_investment, years_held):
        """Calculates taxable capital gains over the life of an investment
        
        Args:
            initial_investment (float): Initial investment
            years_held (int): Years the investment was held
        
        Returns:
            float: Taxable component of capital gains
        """

        current_value = self.compound_interest(initial_investment, self.cg, 1, years_held)
        capital_gain = current_value - initial_investment
        
        if(years_held > 1):
            return capital_gain/2
        else:
            return capital_gain


    def calculate_growth(self, final_year_liquidation=False):
        """The main simulator

        Args:
            final_year_liquidation (bool, optional): Defaults to False. [description]
        """

        # Instantiate with current state pre investment
        growth_history = [self.eoy_stats(
                year = 0,
                salary = self.salary,
                dividend_income = 0,
                excess_tax =  0,
                capital = self.starting_investment)]
                
        for year in range(1, self.years+1):
            
            # Annual Earnings
            dividend_income = self.current_investment * self.dp

            # Total Investment Value
            self.current_investment = (self.current_investment * (1 + self.dp)) * (1 + self.cg)
            
            # If the shares are liquidated at the end of the investment period, factor in CGT
            if year == self.years and final_year_liquidation:

                # Calculate taxable capital gains from DRP
                cg_dividend = sum([self.taxable_capital_gains(x['dividend_income'], (self.years -  x['year'])) for x in growth_history])
                cg_initial_investment = self.taxable_capital_gains(self.starting_investment, self.years)

                # Factor into annual income & net investment value
                total_earnings = self.salary + dividend_income + cg_dividend + cg_initial_investment

                self.current_investment = self.current_investment - (tax(total_earnings) - tax(self.salary))

            else:
                total_earnings = self.salary + dividend_income
                self.salary + dividend_income

            # Determine tax paid
            tax_paid = tax(total_earnings)
            excess_tax = tax_paid - tax(self.salary)

            # Log outcome
            growth_history.append(self.eoy_stats(
                year = year,
                salary = self.salary,
                dividend_income = dividend_income,
                excess_tax = excess_tax,
                capital = self.current_investment
                )
            )

        self.investment_history = growth_history


    def summarise(self):
        """Summarise the final position
                
        Returns:
            dict: Contains the summary stats
        """

        # Total Tax
        total_excess_tax_paid = sum([x['excess_tax'] for x in self.investment_history])

        # Net Position
        final_capital = self.investment_history[-1]['capital']

        # Total Dividends
        total_dividends = sum([x['dividend_income'] for x in self.investment_history])

        return {
            'Total Tax Paid': round(total_excess_tax_paid,2),
            'Total Earnings': round(total_dividends,2),
            'Total Capital': round(final_capital, 2),
            'Final Position': round(final_capital - total_excess_tax_paid,2), 
        }
