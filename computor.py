import sys
import re
import cmath

# called in get_reduced_form_coeffs() for each term of the equation
# returns the coefficient and power for a single term of the equation
def parse_term(term_str) -> tuple:
    term_str = term_str.replace(' ', '').replace('+', '').replace('-', '') # + and - are handled by "get_reduced_form_coeffs()"
    
    # Handle the special cases where coefficient is 1 or -1
	# coefficient in 4X^2 -> 4
    # special case because if 1 or -1, the coefficient is normally ommitted (just write X or -X)
    if term_str.startswith('X^'):
        coeff = 1.0
        power = int(term_str[2:])
    elif term_str.startswith('-X^'):
        coeff = -1.0
        power = int(term_str[3:])
    else:
        parts = term_str.split('*X^')
        coeff = float(parts[0])
        power = int(parts[1])
    
    return coeff, power

# called in main()
# Parses the entire equation and returns a dictionary of coefficients for the reduced form.
def get_reduced_form_coeffs(equation) -> dict:
    sides = equation.split('=')
    left_side = sides[0].replace(' ', '')
    right_side = sides[1].replace(' ', '')
    
    # r'': raw string literal (treats backslash as a literal char instead of the beginning of an escape sequence)
    # [+-]?: matches an optional plus or minus sign
    # \d*: matches zero or more digits (can be zero if coefficient is one)
    # \.?: matches an optional decimal point
    # \d*: matches zero or more digits (for the fractional part of a coefficient)
    # \*?: matches an optional literal asterisk (*)
    # X: matches the literal character 'X'
    # \^?: matches an optional literal caret (^)
    # \d+: matches one or more optional digits (for the power of X)
    left_terms = re.findall(r'[+-]?\d*\.?\d*\*?X\^?\d+?', left_side) # re.findall() returns an array of strings
    right_terms = re.findall(r'[+-]?\d*\.?\d*\*?X\^?\d+?', right_side)

    coeffs = {}
    
    for term in left_terms:
        sign = -1.0 if term.startswith('-') else 1.0
        coeff, power = parse_term(term) #lstrip -> strips leading chars
        coeffs[power] = coeffs.get(power, 0.0) + sign * coeff # combine all Terms with the same power of X into a single coefficient for that power

    for term in right_terms:
        sign = -1.0 if term.startswith('-') else 1.0
        coeff, power = parse_term(term)
        coeffs[power] = coeffs.get(power, 0.0) - sign * coeff
    
    return coeffs

# called in main()
# returns the formatted reduced form of the equation
def format_reduced_form(coeffs) -> str:
    parts = []
    # Sort the dictionary items by key (power) in ascending order
    for power, coeff in sorted(coeffs.items()):
        if abs(coeff) > 1e-6:
            sign = '+' if coeff >= 0 and len(parts) > 0 else ''
            parts.append(f'{sign} {coeff:.2f} * X^{power}')
            
    if not parts:
        return '0 * X^0 = 0'
    
    result = ' '.join(parts)
    return f'{result} = 0'
    
# called in main()
def solve_equation(coeffs, degree) -> None:
    if degree == 2:
        # For a second-degree polynomial (a*X^2 + b*X^1 + c*X^0 = 0), this section
        # extracts the coefficients a, b, and c from the 'coeffs' dictionary.
        # It uses .get(key, 0.0) to retrieve the coefficient for each power,
        # defaulting to 0.0 if the term doesn't exist in the equation.
        # The discriminant is then calculated using the standard formula (b^2 - 4ac).
        # The value of the discriminant determines the nature of the solutions (real or complex).
        a = coeffs.get(2, 0.0)
        b = coeffs.get(1, 0.0)
        c = coeffs.get(0, 0.0)
        discriminant = b**2 - 4*a*c
        
        if discriminant > 1e-6:
            print("Discriminant is strictly positive, the two solutions are:")
            sol1 = (-b + cmath.sqrt(discriminant)) / (2*a)
            sol2 = (-b - cmath.sqrt(discriminant)) / (2*a)
            print(f"{sol1.real:.6f}")
            print(f"{sol2.real:.6f}")
        elif abs(discriminant) < 1e-6:
            print("Discriminant is zero, the solution is:")
            sol = -b / (2*a)
            print(f"{sol:.6f}")
        else: # discriminant is strictly negative
            print("Discriminant is strictly negative, the two complex solutions are:")
            sol1 = (-b + cmath.sqrt(discriminant)) / (2*a)
            sol2 = (-b - cmath.sqrt(discriminant)) / (2*a)
            print(f"{sol1.real:.6f} + {sol1.imag:.6f}i")
            print(f"{sol2.real:.6f} + {sol2.imag:.6f}i")
            
    elif degree == 1:
        a = coeffs.get(1, 0.0)
        b = coeffs.get(0, 0.0)
        
        if abs(a) < 1e-6:
            if abs(b) < 1e-6:
                print("Any real number is a solution.")
            else:
                print("No solution.")
        else:
            solution = -b / a
            print("The solution is:")
            print(f"{solution:.6f}")
            
    elif degree == 0:
        if abs(coeffs.get(0, 0.0)) < 1e-6:
            print("Any real number is a solution.")
        else:
            print("No solution.")

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python computor.py \"equation\"")
        sys.exit(1)
        
    try:
        equation = sys.argv[1]
        reduced_coeffs = get_reduced_form_coeffs(equation)
        
        print(f"Reduced form: {format_reduced_form(reduced_coeffs)}")
        
        degree = 0
        for power in sorted(reduced_coeffs.keys(), reverse=True):
            if abs(reduced_coeffs[power]) > 1e-6:
                degree = power
                break
            
        print(f"Polynomial degree: {degree}")
        if degree > 2:
            print("The polynomial degree is strictly greater than 2, I can't solve.")
        else:
            solve_equation(reduced_coeffs, degree)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
