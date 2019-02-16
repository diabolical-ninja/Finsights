"""
Title: Australian Tax Calculator
Desc:  Calculates tax owed given factors such as franking, deductions, etc
"""



# class AusTax():
#     """Australian Tax Caluclator

#     """


#     def __init__():
        
#         self.payg
#         self.franking_credits
#         self.dividends
#         self.deductions




def tax(income: int, fin_year: int = None) -> float:
    """Calculates progressive tax owed 
    
    Args:
        income (int): Net income for the tax year
        fin_year (int, optional): Defaults to None.
                Financial year of interest, with the latter year being the identifier
                eg, fy 2017/18 is represented as 2018
    
    Returns:
        float: Gross tax owed
    """

    # Define tax rates (%'s) & corresponding income thresholds for fin years
    fy_tax_rates = {
        "2019":{
            "tax_rates": [0,0.19,0.325,0.37,0.45],
            "income_thresholds": [0, 18200, 37000, 90000, 180000]
        },
        "2018":{
            "tax_rates": [0,0.19,0.325,0.37,0.45],
            "income_thresholds": [0, 18200, 37000, 87000, 180000]
        }
    }

    # Assign appropriate tax rates
    # If no financial year is provided, select the most recent
    if fin_year is None:
        fin_year = max(fy_tax_rates.keys())

    tax_rates = fy_tax_rates[fin_year]['tax_rates']
    income_thresholds = fy_tax_rates[fin_year]['income_thresholds']

    # This ensures the upport most tax bracket is calculated
    income_thresholds.append(income)

    # Divy up salaray based off tax bands
    income_by_band = []
    for lower, upper in zip(income_thresholds, income_thresholds[1:]):
        income_by_band.append(max(min(upper-lower, income - lower),0))

    # Calculate progressive tax owed
    return sum([a*b for a,b in zip(tax_rates,income_by_band)])


def franked_dividends(dividend: float, franking: float = 1.0, corporate_tax_rate: float = 0.3):
    """Calculates dividend & paid tax for dividends

    Ref: https://www.commsec.com.au/support/learn/managing-investments/how-do-franking-credits-work.html
    
    Args:
        dividend (float): 
                Total divident payment, in dollars
                eg, $1500 or 123456

        franking (float, optional): Defaults to 1.0
                Franking percentage as a decimal
                eg, fully franked = 100% thus 1.0
                eg, partially franked at 50% thus 0.5
                eg, not franked = 0% thus 0.0

        corporate_tax_rate (float, optional): Defaults to 0.3
                Corporate tax rate as a decimal
                eg, 30% as 0.3
    
    Returns:
        float, float: 
            1. Pre-tax dividend amount (includes franking credits)
            2. Franking credits
    """


    franking_credits = dividend * corporate_tax_rate / (1 - corporate_tax_rate) * franking
    pre_tax_dividend = dividend + franking_credits

    return pre_tax_dividend, franking_credits
